# Implementation details

Read before the first task group. The gates (one group per commit, a stop
only before a step that acts outside the branch and cannot be undone) are
in `CLAUDE.md`.

- Parallel subagents in one worktree each commit only their own files, by
  name; say so in each subagent's prompt.
- The "fails before the fix" check of a regression test: use `prove_red`
  from `.claude/lib/sdd_check.sh`.
- When the feature has visible or audible output (style, layout), the owner
  looks at a live sample in the task group that introduces it (for S/M,
  during the implementation), not only at the final manual check. The
  handover of the sample lists the agent's own decisions that affect
  visible behaviour (for example "the button stays active instead of
  disabled"), so the owner can overrule them on the sample. The
  fresh-subagent probe runs only after this, so it tests the final guide.
- Work on another branch during a feature (for example a backlog proposal
  on a `replanning/` branch) goes into its own worktree: `git worktree add
  ../<repo>-<topic> <branch>`.
