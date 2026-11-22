# Finishing details

## Ticking the roadmap

Tick the phase in `specs/roadmap.md` (`[ ]` → `[x]`) only with the Edit
tool. This edit needs no unlock, but the guard blocks any shell command that
writes the file, and a blocked command runs none of its other steps either.

## Archiving the spec

- Start the move from an empty index (`git status` clean) and commit it on
  its own: a move staged early (`git mv`) lands in whatever commit comes
  next.
- After the move to `Plans/done/`, fix any `Plans/<dir>` path the archived
  files still mention, and rerun `validate.sh` from its new place: with
  `--quick` when the code has not changed since its last full pass (the
  move changes only paths), else in full. An older `validate.sh` without
  `--quick` runs in full.
