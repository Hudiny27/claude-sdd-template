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
  cost, anything irreversible, and anything the owner's rules list as "ask
  first" (deleting, dependencies, schema migrations, remote or production
  hosts). A choice the owner already stated is asked again only when a
  fact or a risk the critical pass found contradicts it.
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
the frontier as questions; facts go where the plan lives (before the spec
exists: a running list the caller writes into the spec's context). First
read the project's own rules for plans (`.claude/rules/` files whose paths
cover the plan, `.claude/project.md`): they may make a choice a question.

## Rounds

1. **Build the frontier:** the open owner-decisions whose prerequisites are
   already settled, including what the critical pass found. A question that
   depends on an answer still open waits for a later round. A question whose
   answer could void the rest (a conflict with the baseline document, "do
   we build this at all") is asked alone, first. Order the rest by impact;
   a round is at most two popups, the less consequential questions wait.
2. **Ask the frontier with AskUserQuestion** (up to 4 questions per popup):
   a 1-2 word header; one plain-Hungarian sentence with enough context to
   answer without scrolling back; 2-4 options, **the recommended one first,
   marked "(Javasolt)"**, each described by what changes for the owner
   (cost, time, what users see, what becomes hard later), technical terms
   explained in brackets. An "Other" answer is final, unless it is a
   question or says they do not understand: then explain with the `plain`
   rules and ask again, simpler.
3. **Record each answer** right away where the plan lives (the spec's
   "Döntések" section, the map's "Eddigi döntések"), one line each, with
   "döntött: owner" and the date.
4. **Recompute the frontier** and ask the next round. Facts you looked up
   meanwhile may close questions; say so in one line instead of asking.
5. **Finish** when the frontier is empty **and** a critical pass over the
   settled plan finds no new branch; a pass that finds one opens a round,
   and the pass runs again after it. If a third such pass still finds a
   branch, ask the owner whether to go on. Then:
   - **Your own decisions:** every "döntött: agent" choice, in one popup of
     multi-select questions of up to 3 decisions each plus a last option
     "Egyiket sem" ("Melyiket módosítanád?", no recommended option), so the
     owner moves on with one click; beyond 12, list the rest in the chat. A
     ticked decision becomes an owner question in one more round.
   - Show the decisions in a short list and confirm in one popup ("Ez így
     rendben?" / "Van még, amit tisztázni kell"), unless the caller
     (size-up, feature-spec) asks for its own approval right after. Do not
     start building until it is confirmed.

There is no round limit. Most M-level plans take 2–4 rounds; start each
round with one line on what opened it (which answer, which scenario).

## Terms

When an answer fixes a name users or the team will use, record it in the
project's glossary right away; a weighty decision may get a decision record.
Where and when: `terms.md` in this skill's folder.
