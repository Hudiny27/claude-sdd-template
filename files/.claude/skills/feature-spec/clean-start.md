# Clean start

Used by `/feature-spec` and `/replan`. Report each check; stop if any fails.

- The working tree is clean (`git status --short` is empty).
- The previous feature branch is merged and you are on an up-to-date `main`
  (with a remote: `git fetch` and no commits behind; without one, only the
  fetch is skipped).
- The constitution exists (`specs/mission.md`, `specs/tech-stack.md`,
  `specs/roadmap.md`). If not, run `/constitution` first.

`/replan` only: list the manual checks earlier features left open (`- [ ]`
lines in `Plans/done/*/validation.md`) and ask the owner about them.
