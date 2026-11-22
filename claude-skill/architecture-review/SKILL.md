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
**deepening**: shallow modules turned into deep ones (much behaviour behind
a small interface, tested through it). Read-only: a deepening the owner
wants becomes a backlog item, later a spec.

Read `vocabulary.md` in this skill's folder first. Use its terms exactly
(module, interface, depth, seam, adapter, leverage, locality), never
"component", "service", "API" or "boundary".

## 1. Scope before you scan

- Take the area the owner named (a folder, a subsystem, a pain point);
  without one, the whole repo.
- Find the hot spots inside it: `git log --oneline -n 80 --stat -- <area>`,
  the files that keep coming up. Recent change is where a deepening pays
  off; scattered change means widen the net.
- Read the project's words and decisions first: `docs/szotar.md` (without
  one, use the names the code and the UI use, and say so in the report) and
  the titles of `docs/decisions/` (or `docs/adr/`); open the ones that
  touch the area. A recorded decision is not re-litigated unless the
  friction is real; then the card says which decision it reopens and why.

## 2. Explore with a fresh subagent

Spawn one read-only subagent (an `Explore` agent where available; it writes
nothing in the repo) with the scope, the hot-spot list, the relevant
decisions, the vocabulary file's path and these questions:

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
A candidate may reach outside the named area when its cause lives there;
the card says so. A probable bug found on the way (code reading only, not
run) goes in its own section of the report, marked as unproven: it is a
`fix/` item for the backlog, never fixed here.

## 3. Write the report

One HTML file outside the repo (static except two CDN scripts, so the
diagrams need network): the session's scratchpad if there is one, else
`${TMPDIR:-/tmp}/architecture-review-<timestamp>.html`. Format: `report.md`
in this skill's folder. Give the owner the absolute path; in an interactive
session also open it (`xdg-open`, `open`, or `explorer.exe` under WSL with
`wslpath -w`).

Per candidate: files, problem (one sentence), solution (one sentence), wins
in vocabulary terms, a before/after diagram, the dependency category, and
the strength: `Erős`, `Érdemes megnézni`, `Spekulatív`. Cards go by
strength; within one strength, a candidate others build on comes first.
The top recommendation is the strongest candidate that fixes a probable bug
or unblocks others, the smaller one on a tie. The prose is plain Hungarian;
the terms are explained once, in the legend at the top.

Do not propose interfaces yet. Ask in a popup which candidates the owner
wants to explore (multi-select), the recommended one first.

## 4. For each picked candidate

- Run the `grill` skill on it: constraints, dependencies, the shape of the
  deepened module, what sits behind the seam, which tests survive.
- To compare interfaces: "Design it twice" in `vocabulary.md`.
- A name the deepening introduces goes to `docs/szotar.md` (format: the
  project's `specs/README.md`); create it if missing.
- If the owner rejects a candidate for a reason a later review would need,
  offer a decision record in `docs/decisions/` (only if hard to reverse,
  surprising without context, and the result of a real trade-off).
- The outcome goes to `specs/backlog/YYYY-MM-DD-kodszerkezet-<slug>.md`
  (with `Állapot: nyitott` under the title): the candidate, the decisions,
  the open questions, a link to the report's path. In an SDD project this is written on the `/replan` branch
  (`replanning/<topic>`); the roadmap decides when it is built, as a feature
  with its own spec. Never change code in this skill.
- Close with one multi-select popup: commit the backlog file(s), `/replan`
  to schedule them. Do only what the owner ticks.
