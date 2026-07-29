# Review severity rubric and finding shape

Shared by the engineering review skills in this plugin (`/review`, `/pr-review`). One
definition, so a severity means the same thing whether a reviewer is reading a local diff
or an open pull request. Before this file existed the two skills carried separate copies
that had already drifted apart in four of five rows.

## Severity rubric

| Severity | Meaning |
|---|---|
| `CRITICAL` | likely data loss, auth bypass, production outage, or unsafe deploy |
| `HIGH` | likely bug/regression, broken contract, or unmet requirement before merge |
| `MEDIUM` | plausible defect, missing test for risky behavior, or near-term maintainability risk |
| `LOW` | minor issue, readability, local polish, or non-blocking observation |
| `INFO` | useful note, not a finding |

`HIGH` covers unmet requirements because a change that does not do what it was asked to do
blocks a merge just as surely as one that breaks. Judge severity by consequence, not by how
much code the fix touches.

## Finding shape

```text
- [SEVERITY] path/to/file.ext:42 - concise problem
  Evidence:
  Impact:
  Suggested fix:
  Test/verification gap:
```

**Cite `file:line`, or state the evidence gap explicitly.** A finding without a location is
an opinion, and an opinion presented as a finding costs the author more time to disprove
than it saved the reviewer to write.

Leave a field out when it genuinely does not apply rather than padding it. `Evidence:` is
the one that never gets to be empty — if there is nothing to point at, that is the finding.

## Domain rubrics that intentionally differ

Two agents define their own scales because their axis is not "how badly does this break":

- `agents/security-engineer.md` — ranks by exploitability and blast radius.
- `agents/ux-researcher.md` — ranks by whether a user can complete the task.

Do not unify these into the table above. A usability issue that stops task completion and a
race condition that corrupts data are both severe, but nothing useful is learned by forcing
them onto one scale.
