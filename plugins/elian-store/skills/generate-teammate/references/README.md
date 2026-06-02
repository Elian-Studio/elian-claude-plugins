# Examples — End-to-end traces

Each example shows the full pipeline from user input through Phase decomposition, approach decision, team / subagent design, and spawn prompts. Use them as references when working with `/generate-teammate`.

| # | Example | Strategy | Demonstrates |
|---|---------|----------|--------------|
| 1 | [Fullstack feature — Notification Center](01-fullstack-feature.md) | Hybrid (Sub → Team → Sub → Sub) | Standard fullstack hybrid; cross-layer API contract negotiation in design phase |
| 2 | [Competing-hypothesis debugging](02-competing-hypothesis-debugging.md) | Single — Agent Team (Research adapted) | Real-time mutual rebuttal between competing theories; why Subagents in parallel are wrong here |
| 3 | [Parallel multi-lens PR review](03-parallel-pr-review.md) | Single — Subagent (parallel) | Independent reviewers + lead aggregation; why Agent Team would only add overhead |
| 4 | [Product launch strategy (non-dev)](04-product-launch-strategy.md) | Hybrid (Sub → Team → Sub) | Non-engineering domain (marketing / business / risk); Strategy Team pattern |

## How to read each example

Every example follows the same structure as the skill execution flow:
1. **Input** — the actual `/generate-teammate` invocation
2. **Phase 1** — request analysis (RequestAnalysis object)
3. **Phase 2** — work phase decomposition table
4. **Phase 3** — per-phase approach decision table + strategy choice
5. **Phase 4-5** — team / subagent plan with role mapping
6. **Phase 6** — confirmation output the user would see
7. **Phase 7** — execution sketch (TypeScript-like pseudocode)
8. **Spawn prompt example** — one filled spawn prompt per example
9. **Why this works / why this approach** — rationale

## When to consult which example

- Building something new with FE + BE → **Example 1**
- Debugging where the root cause is unclear → **Example 2**
- Reviewing a PR / diff from multiple lenses → **Example 3**
- Strategic decision-making (launch, pricing, GTM, positioning) → **Example 4**

The 14 generate-teammate routing agents cover engineering, design, research, marketing, business, and adversarial lenses. Non-code workflows are first-class — see Example 4.
