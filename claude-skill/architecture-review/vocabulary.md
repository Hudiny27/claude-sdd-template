# Vocabulary for deep modules

Adapted from Matt Pocock's `codebase-design` skill (MIT, see
`LICENSE-mattpocock-skills.txt`). Use these terms exactly, in the skill's
instructions, the subagent brief and the report. The Hungarian name is for
the owner-facing report; explain it in brackets the first time.

| Term | Magyarul | Meaning |
|---|---|---|
| Module | modul | Anything with an interface and an implementation: a function, a class, a package, a slice across tiers. _Avoid_: unit, component, service. |
| Interface | felület | Everything a caller must know to use the module correctly: types, but also invariants, ordering, error modes, required configuration, performance. _Avoid_: API, signature. |
| Implementation | megvalósítás | What is inside the module. |
| Depth | mélység | Leverage at the interface: how much behaviour a caller or a test gets per unit of interface it has to learn. **Deep**: much behaviour, small interface. **Shallow**: the interface is nearly as complex as the implementation. |
| Seam | varrat | A place where behaviour can change without editing there; where a module's interface lives. Where to put it is its own decision. _Avoid_: boundary. |
| Adapter | adapter | A concrete thing that fills an interface at a seam (a role, not a size). |
| Leverage | emelő | What callers get from depth: one implementation pays back across many call sites and tests. |
| Locality | lokalitás | What maintainers get from depth: change, bugs and verification concentrate in one place. |

## Principles

- **Depth is a property of the interface.** A deep module may be built from
  small, swappable parts inside; they are not part of its interface. It can
  have internal seams for its own tests and one external seam.
- **The deletion test.** Imagine deleting the module. If complexity
  vanishes, it was a pass-through. If it reappears across many callers, it
  earned its keep.
- **The interface is the test surface.** Callers and tests cross the same
  seam. A test that has to reach past the interface means the module has the
  wrong shape.
- **One adapter is a hypothetical seam; two adapters make it real.** Do not
  add a seam unless something actually varies across it (typically:
  production and test).
- Not a measure: the ratio of implementation lines to interface lines (it
  rewards padding). Depth is leverage.

## Dependency categories (decide how the deepened module is tested)

1. **In-process**: pure computation, in-memory state. Merge the modules and
   test through the new interface; no adapter.
2. **Local-substitutable**: a local stand-in exists (SQLite or PGLite for
   Postgres, an in-memory filesystem). Test with the stand-in; the seam stays
   internal.
3. **Remote but owned**: your own service across a network. A port at the
   seam; an HTTP (or queue) adapter in production, an in-memory adapter in
   tests.
4. **True external**: a third party you do not control. Inject it as a port;
   tests use a mock adapter.

## Testing: replace, do not layer

Once tests at the deepened interface exist, the old tests of the shallow
modules are waste: delete them. Tests assert on observable outcomes through
the interface and survive internal refactors.

## Design it twice

When the owner wants to compare interfaces for a picked candidate: first
write the constraints, the dependencies (with their category) and a rough
sketch for the owner. Then spawn 3 or more subagents in parallel, each with
the same technical brief (paths, coupling, category, this vocabulary, the
project's glossary) and one different constraint:

- minimise the interface: 1–3 entry points, most leverage per entry point;
- maximise flexibility: many use cases and extension;
- optimise for the most common caller: the default case is trivial;
- (if it applies) ports and adapters for the cross-seam dependencies.

Each returns: the interface (types, invariants, ordering, error modes), a
usage example, what hides behind the seam, the dependency strategy, the
trade-offs. Present them one by one, compare by depth, locality and seam
placement, and recommend one (or a hybrid). Be opinionated.
