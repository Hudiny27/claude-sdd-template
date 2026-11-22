# Report format

Adapted from Matt Pocock's `improve-codebase-architecture` report guide
(MIT, see `LICENSE-mattpocock-skills.txt`).

One HTML file, `lang="hu"`. The only scripts are Tailwind and Mermaid from a
CDN, with pinned versions (the Play CDN's console warning is expected; the
diagrams need network); everything else is static. No custom web font.

```html
<!doctype html>
<html lang="hu">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Kódszerkezet: {{repo}}</title>
    <script src="https://cdn.tailwindcss.com/3.4.16"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral" });
    </script>
    <style>.seam { stroke-dasharray: 4 4; } .leak { stroke: #dc2626; }</style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-4 py-10 space-y-12">...</main>
  </body>
</html>
```

## Top of the page

Repo name, date, the scope (which folders: named by the owner or found in
`git log`, and its hot spots), and a small legend: solid box = modul, dashed line = varrat,
red arrow = szivárgás (a detail leaking across a seam), thick dark box =
mély modul. Then one line per term the cards use, with its plain meaning.
Then straight to the candidates.

## Candidate card

One `<article>` each; the diagram carries the weight, the prose is short.

- Title: names the deepening ("Az álnév-visszaállítás egy modulba").
- Badges: strength (`Erős` emerald, `Érdemes megnézni` amber, `Spekulatív`
  slate) and the dependency category.
- Files: a monospace list.
- Before / after: two columns side by side, each in a box of at least
  320 px that scrolls instead of clipping a larger graph.
- Probléma: one sentence. Megoldás: one sentence.
- Nyereség: bullets of a few words in vocabulary terms ("lokalitás: a hiba
  egy helyen javul", "a felület szűkül, a wrapperek eltűnnek"); never
  "tisztább kód".
- If it reopens a recorded decision: one amber line naming it and why.

## Diagram patterns

Vary them; not every card is a Mermaid graph.

- **Mermaid flowchart or sequence**: call flow and dependencies ("before: 6
  round trips, after: 1"); colour leaking edges red with `classDef`.
- **Boxes and arrows by hand**: `<div>` modules and inline SVG arrows, when
  the "after" should look like one thick deep module with faded internals.
- **Cross-section**: stacked thin bands for layers a call passes through,
  collapsed into one thick band.
- **Mass diagram**: two rectangles per module, interface and implementation;
  shallow = almost equal heights, deep = short interface, tall
  implementation.

## Probable bugs (if any)

A separate section before the end: each with file:line evidence, marked
„kódolvasásból, nem futtatva”, and the card it belongs to.

## End

One larger card: the top recommendation, one sentence why, a link to its
card. No hedging; if a sentence could be a bullet, make it one.
