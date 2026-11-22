# Active window

The owner is present, usually for 1–2 hours. Everything that needs the
owner happens here, so the night needs nobody.

## 1. Start

- Run `.claude/bin/sdd preflight` in the main checkout; stop on a `FAIL`.
- Offer the candidates in a multi-select popup: the open backlog items it
  lists, the next open roadmap phases, and features the owner names. Leave
  out (and say why) anything that touches authentication, permissions or
  security.
- Pick a short batch name (lower case, hyphens) and run
  `.claude/bin/sdd batch new <név>`. Ask in one popup: the time box
  (`idokeret`, when the night must stop) and whether the owner wants an
  artifact page with the morning report (`artifact: igen | nem`). Fill both
  into the front matter.

## 2. Shared round

Before any single feature, run the `grill` skill on the batch as a whole
(its critical pass included):

- the order, and which feature builds on which (a dependant gets
  `--after <branch>` in step 3);
- the files or modules two features would both change: they go in order,
  never at the same time;
- the shared words (`docs/szotar.md`) and the decisions that hold for
  several features.

Record the shared decisions in the batch file under `## Közös döntések`, in
the decision line format of `Plans/README.md`.

## 3. Per feature

For each feature, in the agreed order:

1. `.claude/bin/sdd batch add <név> <branch> --level S|M|L [--after <branch>]`.
2. In its worktree, do steps 3–5 of the `feature-spec` skill: the interview
   (the full `grill`), the spec, and `.claude/bin/sdd handover` (run from
   the worktree). Do not repeat what the shared round settled; refer to it.
3. Commit the spec in the worktree (`docs(plans): add spec for <feature>`),
   so the approval covers a committed spec.
4. Fill its row: `Becslés` (hours for the build and the validation) and
   `Auth/biztonság: nem`.

## 4. Estimate and approval

- Add up the estimates (two features can run at once; dependants wait for
  what they build on) and compare with the time box. If the batch does not
  fit, ask in a popup which features leave the batch; drop their rows and
  remove their worktrees (`git worktree remove`) only after that answer.
- Commit the batch file on `main` (`docs(plans): add batch <név>`); the
  pre-commit lint checks it.
- Write the overnight brief (the `overnight` skill, step 1) for the batch:
  the features, the time box, the budget (0 unless the owner names one), no
  push, no merge.
- End the window by telling the owner what to type, as two lines at the
  start of one message:

  ```
  #spec-ok köteg <név>
  #éjszaka
  ```

  The first approves every feature (the guard refuses a row with a reason;
  report any refusal). The second switches the safety guard to overnight
  mode. Then start the build window.
