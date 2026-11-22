---
name: architecture-review
description: >-
  Kódszerkezet-felmérés: csak olvasva megkeresi, hol lett a kód sekély,
  szétszórt vagy nehezen tesztelhető, és egy HTML-riportban mutat javaslatokat
  előtte–utána ábrával; a kiválasztott javaslatból backlog-tétel lesz, kód nem
  változik. Indítsd, ha a felhasználó ezt mondja: „nézd át a kódszerkezetet”,
  „hol romlik a kód?”, „mély modulok”, „architektúra-review”, „mit kellene
  átszervezni?”, vagy „/architecture-review”; és ha a `/replan` felajánlja
  feature-ök között. Original (Matt Pocock improve-codebase-architecture +
  codebase-design, MIT): scan a codebase for deepening opportunities, present
  them as a visual HTML report, then grill through the one the owner picks.
---

# Architecture review

Find where the code stopped being easy to change, and propose
**deepening**: turning shallow modules into deep ones (a lot of behaviour
behind a small interface, tested through that interface). The aim is
testability and code an agent can navigate. This skill only reads code; a
deepening the owner wants becomes a backlog item and later a spec.

Read `vocabulary.md` in this skill's folder first. Use its terms exactly
(module, interface, depth, seam, adapter, leverage, locality), never
"component", "service", "API" or "boundary".

## 1. Scope before you scan

- If the owner named an area (a folder, a subsystem, a pain point), take it.
- Otherwise find the hot spots: `git log --oneline -n 80 --stat` (or more),
  and the files and folders that keep coming up. Recent change is where a
  deepening pays off; scattered change means widen the net.
- Read the project's words and decisions first: `docs/szotar.md` (the
  glossary) and `docs/decisions/` (or `docs/adr/`) for the area. A decision
  recorded there is not re-litigated unless the friction is real; then the
  card says which decision it reopens and why.

## 2. Explore with a fresh subagent

Spawn one subagent (read-only; it writes nothing in the repo) with the scope,
the vocabulary file's path and these questions:

- Where does understanding one concept mean bouncing between many small
  modules?
- Which modules are shallow: the interface nearly as complex as the
  implementation?
- Where were pure functions pulled out only for tests, while the bugs hide
  in how they are called (no locality)?
- Where do tightly coupled modules leak across their seams?
- What is untested, or hard to test through its current interface? Which
  tests repeat the implementation instead of crossing the interface?
- The deletion test on every suspect: would deleting it concentrate
  complexity (it earns its keep) or just move it (a pass-through)?

It reports candidates with file paths and evidence (line ranges, call
counts), not opinions. Check each one yourself before it goes in the report.

## 3. Write the report

One self-contained HTML file outside the repo: the session's scratchpad if
there is one, else `${TMPDIR:-/tmp}/architecture-review-<timestamp>.html`.
Format: `report.md` in this skill's folder. Give the owner the absolute path
and open it (`xdg-open`, `open`, or `explorer.exe` under WSL with
`wslpath -w`).

Per candidate: files, problem (one sentence), solution (one sentence), wins
in vocabulary terms, a before/after diagram, the dependency category, and
the strength: `Erős`, `Érdemes megnézni`, `Spekulatív`. End with the top
recommendation. The report's prose is plain Hungarian; each vocabulary term
is explained in brackets the first time.

Do not propose interfaces yet. Ask in a popup which candidates the owner
wants to explore (multi-select), the recommended one first.

## 4. For each picked candidate

- Run the `grill` skill on it: constraints, dependencies, the shape of the
  deepened module, what sits behind the seam, which tests survive.
- If the owner wants to compare interfaces, use "Design it twice" in
  `vocabulary.md`.
- A name the deepening introduces goes to `docs/szotar.md` (format: the
  project's `specs/README.md`); create it if missing.
- If the owner rejects a candidate for a reason a later review would need,
  offer a decision record in `docs/decisions/` (only if hard to reverse,
  surprising without context, and the result of a real trade-off).
- The outcome goes to `specs/backlog/YYYY-MM-DD-kodszerkezet-<slug>.md`:
  the candidate, the decisions, the open questions, a link to the report's
  path. In an SDD project this is written on the `/replan` branch
  (`replanning/<topic>`); the roadmap decides when it is built, as a feature
  with its own spec. Never change code in this skill.

## Close

One popup, multi-select: commit the backlog file(s), and any next step
(`/replan` to schedule it). Do only what the owner ticks.
