# UX Checklist — must pass before Phase 5 (Deliver)

21 items. Auto-pass means the skill itself enforces the rule via the templates;
needs-confirm means the human (or Claude reading the design back) must verify.

## Readability (auto-pass via visual.html tokens)

1. **Body font size ≥ 16px** — `--fs-body: 16px`. Never drop below.
2. **Line height ≥ 1.5 for body** — `--lh-body: 1.6`.
3. **Line length 45–75ch** — `--measure: 65ch` applied to `<p>`.

## Contrast (needs-confirm)

4. **Body text on background ≥ 4.5:1 (WCAG AA)** — verify when choosing `--ink` and `--bg`.
5. **CTA text on accent ≥ 4.5:1** — verify when choosing `--accent` and `--accent-ink`.

## Interaction (auto-pass via .btn class)

6. **Touch target ≥ 44×44px** — `.btn` has `min-height: 44px; min-width: 44px`.
7. **Focus-visible outline** — `:focus-visible` styled with 2px accent outline + 3px offset.

## State coverage (auto-pass via template, needs-confirm content)

8. **Default + empty + loading + error variants present** — visual.html ships the four
   slot classes (`.state-empty`, `.state-loading`, `.state-error`, plus default content).
   Confirm each has a real message, not placeholder text.

## Responsive (auto-pass via .grid-12 media query)

9. **Mobile / tablet / desktop layouts validated** — wireframe.html and visual.html
   both collapse the 12-col grid to single column at ≤768px. Open both files at
   360px / 768px / 1280px widths and confirm.

## Motion (auto-pass via media query)

10. **`prefers-reduced-motion` honored** — global rule in visual.html disables animation
    and transition when the user prefers reduced motion.

## Reading order & placement (needs-confirm — the heart of Phase 3)

11. **Every box has Order + Intent + Why-here** — wireframe.html `.wf-section`s must
    carry the 4-slot annotation. A box with empty Intent means the author hasn't
    decided what experience it provides; remove or define before proceeding.
12. **Primary CTA is solo above the fold** — no competing CTA in the same visual
    weight class within the first 700px (desktop) / 600px (mobile). Selection paralysis
    is the most common UX failure on landing surfaces.
13. **References echoed in the visual** — every ref in references.md must have at
    least one Steal or Adapt visibly applied in visual.html, and every Reject must
    remain rejected (the pattern doesn't sneak back in). If a ref has zero echoes,
    delete it from references.md — it wasn't really informing the design.

## Anti-slop (needs-confirm — these are the patterns we explicitly reject)

14. **No Inter / Roboto / Arial / system-ui as fallback** — these are AI-default
    fingerprints. Pick a real display + body font pair from a foundry (Google Fonts
    catalogue is fine; just avoid the four above and Space Grotesk).
15. **No purple-gradient-on-white** — and no cream/serif house style if the project
    isn't editorial. Aesthetic must trace to the product's tone, not Claude's defaults.

## Prototype testability (needs-confirm — the artifact must work, not just render)

16. **Every primary task in brief.md has a clickable demo path** — for each task,
    open visual.html, perform the action with a mouse, and confirm visible feedback
    (state change / toast / sheet appearance). A task with no clickable path is
    a task whose UI you have not actually finished designing.
17. **State switcher present and wired** — top banner has a control to flip
    `default | empty | loading | error` instantly. Without it, reviewers see only
    the happy path and miss the failure modes that matter most.
18. **All toggles, timers, and counters are live** — mask toggle masks, filter chips
    filter, countdown ticks each second. Static labels lying about live behavior
    train the reviewer to mistrust the prototype.

## Multi-page flow integrity (needs-confirm — only meaningful when pages > 1)

19. **flow.html ⇆ wireframe.html ⇆ visual.html share the same page slugs** — every
    `page-N` referenced in one file exists in the other two with the same name and
    same transition arrows. Mismatch means reviewers don't know which file is canonical.
20. **Page-to-page state is preserved** — if user selects N items on page-1 and
    transitions to page-2 (confirm), page-2 actually shows those N items, not
    a static placeholder. Inter-page handoff is where most flow bugs hide.
21. **Every page has a return path** — no dead-end pages. From any page the user
    can return to the entry page (browser back, in-page "취소"/"닫기" button, or
    automatic redirect after action). Verify by clicking through each page and
    confirming you can get back home without page-reload.

---

## How to use during Phase 4 (Visual)

Before writing visual.html, walk through items 4, 5, 8 (content), 9, 11, 12, 13, 14, 15
with the user (or self-check). Items 1–3, 6, 7, 10 are guaranteed by the template — the
only failure mode is editing the template and dropping them. If you change those
values, re-state which item moved and why.

Items 11–13 cover wireframe→visual integrity. Items 16–18 cover prototype
testability. **If 16 fails, the visual is a renderable mockup, not a prototype** —
reviews will drift to "this color" debates and miss flow bugs until implementation.
