# Decision window

The owner has 15–30 minutes. Everything is decided here; nothing is built.

## The report

Written at the end of the night from `.claude/bin/sdd batch report` (per
feature: state, commits, spec, the night's agent decisions, manual checks,
ledger lines) and the overnight log, into the overnight folder's
`jelentes.md`
and given as the chat message; with `artifact: igen` also as a private
artifact page with the same content. Plain Hungarian (the `plain` rules):

1. **Egy mondatban:** how many features are merge-ready, parked, unfinished.
2. **Feature-enként** (in the batch order): a status (zöld: merge-kész;
   sárga: merge-kész, but a night decision changed behaviour or scope, or a
   check was flaky or skipped; a manual check alone does not make it
   yellow; piros: parkolva), the evidence (the checks with their result line, a screenshot
   or command output for a visible change), and what it depends on.
3. **Éjjeli döntések:** the `agent` decision lines added during the night,
   per feature.
4. **Kézi ellenőrzések:** per merge-ready feature, the owner's checks from
   its spec, each with where to look.
5. **Parkolt:** what stopped, why, and what the owner needs to decide.

## The decisions

On the owner's next message, one popup round:

- **The night's decisions:** a multi-select per up to 3 decisions plus
  "Egyiket sem"; a ticked one becomes a fix (below).
- **Per feature** (up to 4 questions per popup): "Merge" (recommended for a
  green one; its description says that the feature's worktree folder is
  removed after the merge), "Javítás", "Elvetés", "Később". A dependant can
  be merged only with what it builds on; say so in its question.
- **Push:** one question after the merges: push `main` now, or later.

Then, in this order:

- **Merge:** `.claude/bin/sdd batch merge <név> <branch>...` with every
  chosen feature: it refuses a dependant without its base, merges in
  dependency order (`--no-ff`), runs `.claude/check.sh` once on `main`, and
  only then removes the worktrees and branches and sets `mergelve`. If it
  stops, report what it says; undo nothing without the owner. Then tick
  each merged feature's roadmap phase with the Edit tool.
- **Javítás:** record the owner's request under the spec's "Döntések"
  (`döntött: owner`), `sdd batch set … javítás`; the feature becomes the first
  item of the next batch. Its worktree stays.
- **Elvetés:** `sdd batch set … elvetve "<reason>"`;
  remove the worktree and the branch only if the owner ticked that too.
- **Később:** nothing changes; the next report shows it again.
- **Kézi ellenőrzések:** a merged feature's manual checks stay open (`[ ]`)
  unless the owner says they are done; the next `/replan` asks about them.
- **Push:** only if ticked; a denied push is a stop sign.

Commit the batch file on `main` (`docs(plans): close batch <név>`).
