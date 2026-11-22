# Terms and decision records

Used by the `grill` skill whenever an answer fixes a name or a weighty
decision.

When a decision fixes a name users or the team will use (a page, a role, a
category, a concept), record it in the project's glossary right away, one
term per answer, not batched at the end:

- an SDD project (its `specs/README.md` has a `docs/szotar.md` section):
  `docs/szotar.md` in that format, created with the first term;
- a project with its own glossary (a `/szotar` page, a glossary file): there;
- otherwise: one question in the next round: start `docs/szotar.md`?

Decisions live in the plan's "Döntések". Offer a decision record
(`docs/decisions/NNNN-<slug>.md`, the project's format) only when all three
hold: hard to reverse, surprising without context, a real trade-off.
