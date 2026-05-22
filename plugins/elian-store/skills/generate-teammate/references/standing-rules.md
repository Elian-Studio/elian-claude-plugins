# Standing Rules — generate-teammate

These rules apply throughout the skill — not as one-time procedure steps but as ongoing behavior. Violations are bugs, not preferences.

## 1. Phase decomposition is non-optional

Even if the user describes a single task, run Phase decomposition mentally. Skipping it produces wrong-shape teams.

## 2. Per-phase independence beats whole-task judgment

Composite work has phases that prefer different approaches. Forcing one approach across the whole task is the most common failure mode.

## 3. The core question is "Do workers need to communicate with each other?"

From the official docs.
- **No** → Subagent (parallel, independent).
- **Yes, with handoff only** → Subagent chain (sequential).
- **Yes, with debate / negotiation** → Agent Team.

## 4. File ownership before parallelism

Two teammates editing the same file is a data race in disguise. Validate ownership separation **before** spawning, not after.

## 5. Minimum viable team

2 teammates beat 5 if 2 suffice. Coordination cost grows non-linearly past 5.

## 6. Always confirm with AskUserQuestion before spawning

The user owns the decision; the skill produces the recommendation. Never spawn without explicit gate.

## 7. Self-contained agents only

This plugin's 14 agents work without external skills. Do not introduce dependencies on user-level skills the user may not have.

## 8. Spawn prompt is JSON-first

Since v2.6, spawn prompt content is authored as JSON and rendered via `create-document/scripts/render.py --template teammate-spawn`. This enforces all 7 slots (ROLE / OWNED FILES / TECH STACK / TASK / REFERENCE DOCS / INTERFACES / DOD / COMMUNICATION) and blocks vague language (`help build`, `do something`, `TODO`, `...`).

See [Phase 4-5 in SKILL.md](../SKILL.md#phase-4-team--task-design) for the procedure.
