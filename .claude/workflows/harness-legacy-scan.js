export const meta = {
  name: 'harness-legacy-scan',
  description: 'Read-only AI coding harness audit — finds stale rules, duplicated instructions, excessive always-on context, over-broad skills/permissions, and overlap with product built-ins, then classifies each finding KEEP / SHRINK / MOVE / SPLIT / CONVERT / DELETE (no files modified)',
  phases: [
    { title: 'Inventory', detail: 'List and fact-check harness files and settings' },
    { title: 'Analyze', detail: '4 perspectives in parallel (ContextTax / SkillQuality / ProductOverlap / Safety)' },
    { title: 'Classify', detail: 'Refactor Planner — classify findings, de-duplicate, normalize fields' },
    { title: 'Challenge', detail: 'Adversarial Reviewer — push back on risky shrink/delete calls' },
  ],
}

// args: (optional) a project root path to also audit, or a free-text note.
//   - If a string, that path's CLAUDE.md / AGENTS.md / .claude/ are added to the audit scope.
//   - If empty, audit the global harness (~/.claude, ~/.codex); if the current working
//     directory has CLAUDE.md / AGENTS.md / .claude/, include that project too.
const TARGET_PROJECT = (typeof args === 'string' && args.trim()) ? args.trim() : ''
const TARGET_NOTE = TARGET_PROJECT
  ? `Additional project root to audit: ${TARGET_PROJECT} (also audit this project's CLAUDE.md / AGENTS.md / .claude/).`
  : 'No project argument given. Audit the global harness (~/.claude, ~/.codex); if the current working directory has CLAUDE.md / AGENTS.md / .claude/, include that project too.'

const RO = [
  '⚠️ HARD RULE — READ ONLY:',
  '- Do not modify/delete/create any file. No Edit/Write/NotebookEdit calls.',
  '- Use only Read / Grep / Glob / Bash (read-only: ls, wc, cat, jq, etc.).',
  '- Never change harness files (CLAUDE.md, AGENTS.md, settings*.json, skills/**, hooks, MCP config).',
  '- Your final output is structured data (JSON), not a human-facing message. Analyze only.',
  '- Write all text fields in English.',
].join('\n')

const FINDING_ITEM = {
  type: 'object',
  properties: {
    path: { type: 'string', description: 'Target path (a file or a logical group, e.g. ~/.claude/skills/devlog*)' },
    currentPurpose: { type: 'string', description: 'What this item currently does' },
    problem: { type: 'string', description: 'The problem found (stale / duplicate / excessive / over-broad, etc.)' },
    evidence: { type: 'string', description: 'Evidence — quote actual content/lines you read, not speculation' },
    recommendation: { type: 'string', enum: ['KEEP', 'SHRINK', 'MOVE', 'SPLIT', 'CONVERT', 'DELETE'] },
    moveTarget: { type: 'string', description: 'Recommended destination for MOVE/CONVERT/SPLIT. Empty string if N/A' },
    risk: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH'], description: 'Risk of making the change' },
    confidence: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH'], description: 'Confidence in this finding' },
    autoSafe: { type: 'boolean', description: 'Is it safe for a later auto-diet step to apply without human approval' },
  },
  required: ['path', 'currentPurpose', 'problem', 'evidence', 'recommendation', 'moveTarget', 'risk', 'confidence', 'autoSafe'],
}

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    perspective: { type: 'string' },
    summary: { type: 'string', description: '3–5 sentence summary of this perspective' },
    findings: { type: 'array', items: FINDING_ITEM },
  },
  required: ['perspective', 'summary', 'findings'],
}

// ---------- Phase 1: Inventory ----------
phase('Inventory')

const INVENTORY_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    artifacts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          category: { type: 'string', description: 'GlobalContext | ProjectContext | Skill | Agent | Settings | Hook | MCP | MetaDoc | Permission | Command | Workflow' },
          path: { type: 'string' },
          sizeOrCount: { type: 'string' },
          purpose: { type: 'string' },
          loadedEverySession: { type: 'boolean' },
          note: { type: 'string' },
        },
        required: ['category', 'path', 'purpose', 'loadedEverySession'],
      },
    },
    rawFacts: { type: 'array', items: { type: 'string' }, description: 'Verified facts for downstream analysts (duplication/conflict/gaps, etc.)' },
  },
  required: ['summary', 'artifacts', 'rawFacts'],
}

const inventory = await agent([
  RO,
  '',
  'Role: Inventory Agent. Directly explore this machine\'s AI coding harness (global + optional project), list every item, and establish as fact whether each is "loaded every session / duplicated / empty".',
  TARGET_NOTE,
  '',
  'Standard locations to explore (record only what exists; if absent, record "absent" as a fact):',
  'Global Claude Code:',
  '- ~/.claude/CLAUDE.md (global behavioral rules)',
  '- ~/.claude/settings.json, ~/.claude/settings.local.json (env / permissions / hooks / risk flags)',
  '- ~/.claude.json -> mcpServers (Claude MCP lives here, NOT in settings.json)',
  '- ~/.claude/skills/, ~/.claude/agents/, ~/.claude/commands/, ~/.claude/workflows/ (count each, and note empty dirs)',
  '- ~/.claude/projects/<...>/memory/MEMORY.md (memory index, if present)',
  'Global Codex:',
  '- ~/.codex/AGENTS.md, ~/.codex/config.toml, ~/.codex/prompts/, ~/.codex/skills/ (if present)',
  'Project (when a target is given):',
  '- <project>/CLAUDE.md, <project>/AGENTS.md, <project>/.claude/ (skills, settings.local.json, *.md meta docs)',
  '',
  'Method: use Bash (ls, wc -l, wc -c, cat, jq, grep) and Read to gather facts directly. For large files, Grep "^#" to extract headings and see the section structure.',
  '',
  'In particular, establish these as fact:',
  '1) How many times the same topic (default language, no destructive commands, commit/branch discipline, test-first, etc.) repeats across global CLAUDE.md / project CLAUDE.md / AGENTS.md.',
  '2) The approximate total bytes loaded into context every session (global + project CLAUDE.md + AGENTS.md + MEMORY.md).',
  '3) The list of empty skill directories (no SKILL.md).',
  '4) Whether the workflows / commands directories are empty.',
  '5) Whether project .claude/*.md meta docs are actual operating rules or one-time setup explainers.',
  '6) Counts of skills/agents/MCP, distinguishing "installed plugin surface" vs "user-authored".',
].join('\n'), { schema: INVENTORY_SCHEMA, label: 'inventory', phase: 'Inventory' })

const INV = JSON.stringify(inventory, null, 0)

// ---------- Phase 2: Analyze (4 perspectives in parallel) ----------
phase('Analyze')

const COMMON = [
  RO,
  '',
  'Facts established by the Inventory Agent (JSON) — cite paths/counts/duplication from here, and Read the key files directly to verify:',
  INV,
  '',
  'Audit principles (judge strictly by these):',
  '- A good harness prevents "recurring real mistakes". A rule that guards against something that never happens is overhead.',
  '- A good harness must not exist to preserve old habits.',
  '- A harness should not keep accreting; it should appear "only when needed" (always-on global < conditional Skill).',
  '- The goal of this audit is not to add rules, but to find stale rules and classify them as "candidates to trim".',
  '- If something overlaps with a product built-in (Claude Code / Codex / Cursor), treat it as duplication.',
  '',
  'Fill every schema field for each finding. In evidence, quote what you actually read/lines, not speculation.',
  'Maximize signal over noise: do not list 100 items one by one; group the same problem (e.g. a cluster of similarly named skills) into one representative finding, but name the group in path.',
].join('\n')

const perspectives = await parallel([
  // 2-1 Global Context Tax
  () => agent([
    COMMON,
    '',
    'Role: Global Context Tax Agent.',
    'Targets: global CLAUDE.md, project CLAUDE.md, AGENTS.md, MEMORY.md, (.cursor/rules if present). Read them all directly.',
    'Question: do these instructions, which attach unconditionally to every session, create unnecessary context cost?',
    'Focus:',
    '- Duplicated instructions across the files (default language, no destructive commands, commit/branch discipline, test-first). Where could they live exactly once?',
    '- Large blocks inside global CLAUDE.md (long tables, checklists, "done criteria" templates, example code/JSON, full pre-commit hook text, multi-session state-restore procedures) — are these fit as "always-resident instructions", or candidates to move into a task-specific Skill/reference?',
    '- Whether the project CLAUDE.md doc/plan/design conventions belong always-on, or only at a specific skill-invocation moment.',
    '- Rules left over to preserve old habits (already replaced by memory/skills).',
    '- Instructions that contradict each other or where one nullifies another.',
    'recommendation is mostly among KEEP (the essential few) / SHRINK (condense large blocks) / MOVE (to a Skill/reference) / CONVERT (always-on rule -> conditional skill).',
  ].join('\n'), { schema: FINDINGS_SCHEMA, label: 'context-tax', phase: 'Analyze' }),

  // 2-2 Skill Quality
  () => agent([
    COMMON,
    '',
    'Role: Skill Quality Agent.',
    'Targets: global user skills + installed plugin skills + (if present) project skills. Counts/lists are in the Inventory facts (artifacts).',
    'Question: is each Skill still needed / is its description too broad / is its SKILL.md too long?',
    'Focus (report in groups):',
    '- Empty skill directories (no SKILL.md): the ones found in Inventory — dead skills. Confirm with ls, then recommend handling.',
    '- Clusters of functionally overlapping skills by naming pattern (e.g. foo / foo-morning / foo-evening, or several skills doing the same review job) — consolidation candidates per cluster.',
    '- Very long SKILL.md bodies (hundreds–thousands of lines) — candidates to SPLIT into examples.md / reference.md, or distinguish that they are installed-plugin artifacts the user need not manage.',
    '- Skills whose description is so broad they risk triggering unintentionally.',
    '- Installed plugin skill surface: are they actually used in the current workflow, or do they just pollute the discovery list (domains never used)?',
    'Key distinction: separate "quality problems in user-authored/managed skills" from "items where disabling the installed plugin is the answer".',
    'Read a few of the largest SKILL.md files to confirm in evidence whether their length is justified (could references be split out).',
  ].join('\n'), { schema: FINDINGS_SCHEMA, label: 'skill-quality', phase: 'Analyze' }),

  // 2-3 Product Overlap
  () => agent([
    COMMON,
    '',
    'Role: Product Overlap Agent.',
    'Question: find rules/skills/settings that were once needed but now overlap with Claude Code / Codex / Cursor product built-ins.',
    'Read global/project CLAUDE.md directly and verify these candidates:',
    '- "git status/branch first", "feature branches only", commit discipline — do these overlap with the product\'s default git workflow / permission model?',
    '- TODO/FIXME blocking, full pre-commit hook text — already covered by product hooks/code-review, or is the project\'s actual hook behavior just copy-pasted into CLAUDE.md again?',
    '- Progress-state files (progress.json/progress.md) / context save & restore skills — overlap with the product\'s auto-compaction + memory.',
    '- safe-mode / guard / freeze style skills — overlap with the product\'s permission mode / sandbox / deny list?',
    '- Large "plan / done-criteria" templates — overlap with the product\'s Plan mode (EnterPlanMode).',
    '- Meta-instructions like "split verification / self-assessment problem" — overlap with default model behavior?',
    '- Multiple code-review tools (plugin/skill/agent/command) overlapping with the product /code-review and review features.',
    'For each finding, state in evidence "which product built-in it overlaps with". recommendation is mostly DELETE (full duplicate) / SHRINK / CONVERT.',
  ].join('\n'), { schema: FINDINGS_SCHEMA, label: 'product-overlap', phase: 'Analyze' }),

  // 2-4 Safety & Permission
  () => agent([
    COMMON,
    '',
    'Role: Safety and Permission Agent.',
    'Targets: hooks, permissions (allow/deny), MCP config, settings flags. Read the actual files the Inventory points to (global settings.json / settings.local.json, ~/.claude.json, project settings.local.json).',
    'Question: are hooks / allowed-tools / MCP granting overly broad permissions?',
    'Focus:',
    '- skipDangerousModePermissionPrompt and other risk-bypass flags — if set, assess risk and justification. (Also evaluate whether CLAUDE.md acknowledges this and demands prompt-level safety.)',
    '- Whether the deny list is empty + what that means combined with the flags above.',
    '- permissions.allow count and breadth — the scope of wildcards (e.g. Bash(<build-tool>:*)), broad items like allowing git reset/checkout.',
    '- Large inline commands frozen into allow (long one-line scripts) — fragile and broadly scoped from a security view?',
    '- The MCP server list — do servers that are not actually used inflate resident permission/tool surface?',
    '- hooks: PostToolUse / SessionStart / Notification, etc. — side effects, failure tolerance, necessity.',
    'Caution: the user\'s memory may contain deliberate security decisions (specific frozen policies). Do not over-recommend hardening; point out only permissions that are excessively "broad". recommendation is mostly KEEP / SHRINK (reduce permission) / CONVERT; mark risky ones risk=HIGH + autoSafe=false.',
  ].join('\n'), { schema: FINDINGS_SCHEMA, label: 'safety-permission', phase: 'Analyze' }),
])

const valid = perspectives.filter(Boolean)
log(`Analysis done: ${valid.length}/4 perspectives, ${valid.reduce((n, p) => n + (p.findings ? p.findings.length : 0), 0)} raw findings total`)

// ---------- Phase 3: Refactor Planner ----------
phase('Classify')

const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    overview: { type: 'string', description: '3–5 sentence big picture' },
    classified: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'F1, F2 ... stable identifier' },
          path: { type: 'string' },
          sourcePerspectives: { type: 'array', items: { type: 'string' } },
          currentPurpose: { type: 'string' },
          problem: { type: 'string' },
          evidence: { type: 'string' },
          category: { type: 'string', enum: ['KEEP', 'SHRINK', 'MOVE', 'SPLIT', 'CONVERT', 'DELETE'] },
          moveTarget: { type: 'string' },
          risk: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH'] },
          confidence: { type: 'string', enum: ['LOW', 'MEDIUM', 'HIGH'] },
          autoSafe: { type: 'boolean' },
          rationale: { type: 'string', description: '1–2 sentences on why this classification' },
        },
        required: ['id', 'path', 'currentPurpose', 'problem', 'evidence', 'category', 'moveTarget', 'risk', 'confidence', 'autoSafe', 'rationale'],
      },
    },
  },
  required: ['overview', 'classified'],
}

const planned = await agent([
  RO,
  '',
  'Role: Refactor Planner.',
  'Input: findings from 4 perspectives (JSON). Merge duplicate findings about the same target, and assign each item a final classification (KEEP/SHRINK/MOVE/SPLIT/CONVERT/DELETE) and all fields.',
  'Definitions: KEEP=leave as is / SHRINK=condense heavily / MOVE=relocate (global->skill, team-shared->CLAUDE.md, etc.) / SPLIT=extract reference.md/examples.md out of the body / CONVERT=change form (always-on rule->conditional skill, or hook->setting, etc.) / DELETE=remove (empty skills, full duplicates, dead rules).',
  'Rules:',
  '- Respect decisions the user has fixed in memory/rules. Keep the placement distinction between team-shared and personal rules, and do not create invalid items that conflict with a policy decision the user already made.',
  '- id sequential from F1. When merging the same target, list every contributing perspective in sourcePerspectives.',
  '- autoSafe: false when human judgment/context is needed (changing global-instruction meaning, reducing permissions, security-related, removing MCP). true when mechanical and reversible (deleting empty skills, obvious line-count condensing, merging a duplicated phrase in one place).',
  '- Signal first: highest-importance items first. No infinite enumeration of trivia.',
  '',
  'Findings from 4 perspectives (JSON):',
  JSON.stringify(valid, null, 0),
  '',
  'Inventory facts (JSON):',
  INV,
].join('\n'), { schema: PLAN_SCHEMA, label: 'refactor-planner', phase: 'Classify' })

// ---------- Phase 4: Adversarial Reviewer ----------
phase('Challenge')

const ADV_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    challenges: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          targetId: { type: 'string' },
          path: { type: 'string' },
          originalCategory: { type: 'string' },
          objection: { type: 'string', description: 'If trimmed or deleted, what mistake comes back?' },
          consequenceIfApplied: { type: 'string' },
          revisedCategory: { type: 'string', enum: ['KEEP', 'SHRINK', 'MOVE', 'SPLIT', 'CONVERT', 'DELETE', 'UNCHANGED'] },
          mustHumanApprove: { type: 'boolean' },
        },
        required: ['targetId', 'path', 'originalCategory', 'objection', 'consequenceIfApplied', 'revisedCategory', 'mustHumanApprove'],
      },
    },
    blockedFromAuto: { type: 'array', items: { type: 'string' }, description: 'ids that must NOT be auto-processed' },
    safeForAuto: { type: 'array', items: { type: 'string' }, description: 'ids that are low-risk and safe to auto-process' },
  },
  required: ['summary', 'challenges', 'blockedFromAuto', 'safeForAuto'],
}

const challenged = await agent([
  RO,
  '',
  'Role: Adversarial Reviewer. Push back on the Refactor Planner\'s classifications.',
  'Attack the SHRINK/DELETE/CONVERT/MOVE items in particular: "Does trimming or deleting this actually make things worse? Which recurring mistake comes back to life?"',
  'The audit goal is "trim", but your job is the safeguard against over-deletion. Defend these in particular:',
  '- Rules like no-destructive-commands / branch discipline / safety nets may, even if they look like product built-ins, actually be what has been preventing the user\'s recurring mistakes (check whether memory has such cases).',
  '- Block delete proposals that conflict with decisions frozen in the user\'s memory (feedback/project policy).',
  '- Reducing permissions/MCP/hooks can break workflows — flip risky items marked autoSafe=true back to false.',
  'Give each challenge a revisedCategory (UNCHANGED if no problem). Produce clear blockedFromAuto / safeForAuto id lists.',
  '',
  'Refactor Planner result (JSON):',
  JSON.stringify(planned, null, 0),
].join('\n'), { schema: ADV_SCHEMA, label: 'adversarial', phase: 'Challenge' })

return { inventory, perspectives: valid, planned, challenged }
