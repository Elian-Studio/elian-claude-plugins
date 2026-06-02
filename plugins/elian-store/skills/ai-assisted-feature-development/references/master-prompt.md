# Master Prompt

Use this prompt when one consolidated planning pass is better than running each phase separately.

```text
You are preparing implementation-ready feature artifacts before an AI agent writes code.

Feature:
<feature name and short description>

Known context:
- Users:
- Product goal:
- Constraints:
- Tech stack:
- Risk level:
- Existing files or docs to inspect:

Run the AI-assisted feature development workflow:

1. Feature Framing
   - intent
   - users
   - success criteria
   - non-failure conditions
   - edge cases
   - risk classification
   - open questions

2. BDD
   - normal flows
   - failure flows
   - exception flows
   - policy questions separated from assumptions

3. SDD
   - purpose
   - scope and out of scope
   - roles and permissions
   - inputs and outputs
   - UI/API behavior
   - state changes
   - error policy
   - observability
   - test requirements
   - acceptance criteria

4. DDD decision
   - say whether DDD is warranted
   - if warranted, propose entities, value objects, services, repositories, events, bounded contexts, and invariants
   - if not warranted, explain why simple design is enough

5. AI-TDD
   - test matrix before implementation
   - regression cases
   - tests the implementation agent may not weaken or delete

6. Context Engineering
   - required docs
   - required files
   - optional background
   - constraints
   - no-touch areas
   - verification commands

7. Agentic Coding Ticket
   - goal
   - scope
   - out of scope
   - acceptance criteria
   - required context
   - test requirements

8. Review Criteria
   - spec fit
   - BDD coverage
   - tests
   - security
   - privacy
   - permissions
   - performance
   - accessibility
   - maintainability

9. SPDD Archive
   - prompts used
   - assumptions
   - decisions
   - artifacts
   - test results expected
   - reusable pattern
   - anti-pattern to avoid

Rules:
- Do not implement code.
- Do not invent product policy. Mark unknowns as questions.
- Keep context bounded to files that the implementation agent needs.
- Make acceptance criteria testable.
- Use concise artifacts that can be handed to another agent.
```

## Output Shape

Return sections in the same nine-phase order. End with:

```text
Ready for implementation handoff: yes/no
Blocked by questions:
- ...
Recommended next skill: /implement | /fix | /improve | /decision-dashboard | /persona-review
```
