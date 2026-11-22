# Decision window

The owner has 15–30 minutes. Everything is decided here; nothing is built.

## The report

Written at the end of the night into the overnight folder's `jelentes.md`
and given as the chat message; with `artifact: igen` also as a private
artifact page with the same content. Plain Hungarian (the `plain` rules):

1. **Egy mondatban:** how many features are merge-ready, parked, unfinished.
2. **Feature-enként** (in the batch order): a status (zöld: merge-kész;
   sárga: merge-kész, but a decision or a check needs the owner; piros:
   parkolva), the evidence (the checks with their result line, a screenshot
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

- **Merge:** in the main checkout, merge each chosen branch into `main` in
  dependency order (`--no-ff`), tick its roadmap phase with the Edit tool,
  run the project's check once on `main`, remove its worktree, and set
  `Állapot: mergelve`.
- **Javítás:** record the owner's request under the spec's "Döntések"
  (`döntött: owner`), set `Állapot: javítás`; the feature becomes the first
  item of the next batch. Its worktree stays.
- **Elvetés:** set `Állapot: elvetve`, note the reason in the batch file;
  remove the worktree and the branch only if the owner ticked that too.
- **Később:** nothing changes; the next report shows it again.
- **Push:** only if ticked; a denied push is a stop sign.

Commit the batch file on `main` (`docs(plans): close batch <név>`).
