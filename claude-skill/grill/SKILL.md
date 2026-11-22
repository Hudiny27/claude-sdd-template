---
name: grill
description: >-
  Kikérdezés egy terv, spec vagy ötlet tisztázására, felugró kérdésekkel és
  javasolt válaszokkal; ha egy kérdésre más tudja a választ (jogász,
  kolléga), kérdőívet ír neki. Indítsd, ha a felhasználó ezt mondja:
  „kérdezz ki”, „faggass ki”, „grillezz meg”, „nézzük át a tervet”, „vannak
  még vak foltok?”, „tisztázzuk a részleteket”, „milyen kérdésekre
  válaszoljak?”, „kérdőív a jogásznak / kollégának”, vagy „/grill”; és a
  size-up F/M/L fokozatánál, valamint a feature-spec interjújánál. Original
  (Matt Pocock grilling + grill-with-docs + to-questionnaire): interview the
  user relentlessly about a plan as a design tree, one round of frontier
  questions at a time, each with a recommended answer; turn questions only
  someone else can answer into a questionnaire.
---

# Grill: settle the open decisions

Reach a shared understanding of the plan before building. Treat the plan as a
**design tree**: each decision opens the decisions that depend on it.

## Who answers what

- **Facts are your job.** Anything you can find in files, git, docs, the
  web or the running app: look it up (a subagent for anything broad). Never
  ask the owner a fact.
- **Reversible technical choices are your job.** Decide, and record the
  decision with "döntött: agent" so the owner can overrule it later.
- **The owner decides** product, scope, wording users see, priorities,
  cost, anything irreversible, and anything under "Ask first".
- **Someone else decides** legal, a colleague's system, a client's needs:
  write a questionnaire instead of guessing (`questionnaire.md` in this
  skill's folder), note in the plan that it waits on them, and go on.
- **A conflict with the project's baseline document** (a PRD, a
  constitution) is always an owner question. Never settle it in
  "Döntések"; follow the project's rule for it (for example a written
  change proposal instead of an edit).

## Critical pass

Before the first round, read the plan as a sceptic, even when it looks
complete: check its claims against the code and the data, walk 3–5 edge
scenarios through it, run a pre-mortem, and pin fuzzy words. When the plan
is hard to reverse or reaches far, a fresh break-it subagent attacks it
too. How: `critical-pass.md` in this skill's folder. What it finds enters
the frontier; facts you record, decisions you ask.

## Rounds

1. **Build the frontier:** the open owner-decisions whose prerequisites are
   already settled, including what the critical pass found. A question that
   depends on an answer still open waits for a later round.
2. **Ask the frontier with AskUserQuestion** (up to 4 questions per popup;
   more popups if needed). For each question:
   - the header: a 1-2 word topic;
   - the question: one plain-Hungarian sentence, with just enough context
     to answer without scrolling back;
   - 2-4 options, **the recommended one first, marked "(Javasolt)"**;
   - in each option's description: what changes for the owner if chosen
     (cost, time, what users see, what becomes hard later). No jargon; a
     technical term only with a short explanation in brackets.
   The owner can always pick "Other" and type; treat that answer as final,
   unless it is a question or says they do not understand: then explain the
   question with the `plain` rules and ask it again, simpler.
3. **Record each answer** right away where the plan lives (the spec's
   "Döntések" section, the map's "Eddigi döntések"), one line each, with
   "döntött: owner" and the date.
4. **Recompute the frontier** and ask the next round. Facts you looked up
   meanwhile may close questions; say so in one line instead of asking.
5. **Finish** when the frontier is empty **and** a second critical pass, over
   the settled plan, finds no new branch. Then:
   - **Your own decisions:** list every "döntött: agent" choice made so far
     in one popup, as multi-select questions of up to 4 decisions each
     ("Melyiket módosítanád?"). A ticked one becomes an owner question in
     one more round.
   - Show the decisions in a short list and confirm with one popup ("Ez így
     rendben?" / "Van még, amit tisztázni kell"). When the caller (size-up,
     feature-spec) asks for its own approval right after, skip this popup:
     the caller's approval covers it. Do not start building until it is
     confirmed.

There is no round limit. Most M-level plans take 2–4 rounds; start each
round with one line on what opened it (which answer, which scenario).

## Terms

When a decision fixes a name users or the team will use (a page, a role, a
category, a concept), record it in the project's glossary right away, one
term per answer, not batched at the end:

- an SDD project (its `specs/README.md` has a `docs/szotar.md` section):
  `docs/szotar.md` in that format, created with the first term;
- a project with its own glossary (a `/szotar` page, a glossary file): there;
- otherwise: offer once to start `docs/szotar.md`.

Decisions live in the plan's "Döntések". Offer a decision record
(`docs/decisions/NNNN-<slug>.md`, the project's format) only when all three
hold: hard to reverse, surprising without context, a real trade-off.
