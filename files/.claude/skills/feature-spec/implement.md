# Implementation details

Read before the first task group. The gates (one group per commit, one
group at a time for security, auth, data and migrations) are in
`CLAUDE.md`.

- When several subagents work in parallel in the same worktree, each
  commits only its own files, by name (`git add <paths>`, never
  `git add -A` or `git add .`); this goes into each subagent's prompt too.
- The "fails before the fix" check of a regression test runs only the new
  test, with a time limit: the old code may start other tests too.
- When the feature has visible or audible output (style, layout), the owner
  looks at a live sample in the task group that introduces it (for S/M,
  during the implementation), not only at the final manual check. The
  handover of the sample lists the agent's own decisions that affect
  visible behaviour (for example "the button stays active instead of
  disabled"), so the owner can overrule them on the sample. The
  fresh-subagent probe runs only after this, so it tests the final guide.
- One branch works in a worktree at a time. When work on another branch is
  needed during a feature (for example a backlog proposal on a
  `replanning/` branch), it happens in a separate git worktree
  (`git worktree add ../<repo>-<topic> <branch>`); no branch switch in the
  running feature's worktree. A switch replaces the files under the
  running session and its subagents, and the guard judges by the other
  branch's rules.
