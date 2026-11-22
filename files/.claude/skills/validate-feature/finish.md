# Finishing details

## Archiving the spec

Commit the ticks first, then run `.claude/bin/sdd archive`: it moves the
folder to `Plans/done/`, fixes the paths that name it, reruns
`validate.sh` from there (its `full_once` skips the suite) and commits the
move on its own. An older `validate.sh` without the library: pass
`--no-validate` and rerun it by hand, with `--quick` if it has the switch
and the code has not changed since its last full pass, else in full.
