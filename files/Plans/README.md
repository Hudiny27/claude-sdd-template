# Plans/: feature specek

Minden roadmap-fázis (és minden kódot érintő újratervezési változtatás) saját
feature specet kap, mielőtt bármilyen kód készülne:

```
Plans/
├── YYYY-MM-DD-<slug>/     # aktív feature, <slug> = a branchnév utolsó része
│   ├── plan.md            # számozott feladatcsoportok
│   ├── requirements.md    # hatókör, hatókörön kívül, döntések, kontextus
│   └── validation.md      # ellenőrzések, amelyek igazolják, hogy kész és mergelhető
└── done/                  # befejezett feature-ök, merge előtt ide kerülnek
```

Branch `feature/phase-2-agents` ↔ könyvtár `Plans/2026-10-05-phase-2-agents/`.
Az SDD őr, a git pre-commit hook és a CI ellenőrzés is e névszabály alapján
találja meg a specet.

## Életciklus

1. `/feature-spec`: branch + interjú + a három fájl. Még nincs kód.
2. Owner review. A módosítások az agenten keresztül mennek, hogy a három fájl
   konzisztens maradjon.
3. Az owner a `#spec-ok` kulcsszóval jóváhagyja. Ettől kezdve ezen a branchen
   engedélyezett a kódszerkesztés.
4. Implementáció, feladatcsoportonként.
5. `/validate-feature`: a `validation.md` minden ellenőrzése, roadmap
   kipipálása, a könyvtár áthelyezése a `done/` alá, merge.

## plan.md

```markdown
# Terv: <feature>

Roadmap: Fázis <n> — <cím>
Branch: feature/<slug>

## 1. csoport — <név>
1. <feladat>
2. <feladat>

## 2. csoport — <név>
3. <feladat>

## N. csoport — Ellenőrzés
- A validation.md minden ellenőrzésének lefuttatása
```

## requirements.md

```markdown
# Követelmények: <feature>

## Hatókör
- <mit szállít ez a feature>

## Hatókörön kívül
- <mit nem csinál szándékosan>

## Döntések
- <döntés> — <miért> (YYYY-MM-DD, döntött: owner | agent)

## Kontextus
- <korlátok, kapcsolódó kód, érintettek megjegyzései>
```

Minden döntésnél jelölni kell, ki hozta. `owner`: a spec-interjúból, a
constitutionből vagy az owner kifejezett kéréséből származik. `agent`: az
agent döntötte el (feltételezés, alapérték, implementációs választás), és a
`#spec-ok` hagyja jóvá; a review során később hozott agent-döntésekre az
owner rákérdezhet. Soronként egy döntéshozó szerepel, a vegyes döntéseket
szét kell bontani.

## validation.md

```markdown
# Validáció: <feature>

## Automatikus ellenőrzések (az agent futtatja)
- [ ] `<parancs>` — <várt eredmény>

## Kézi ellenőrzések (az owner futtatja)
- [ ] <mit kell megnézni, hol>

## Kész definíciója
- A fenti ellenőrzések mind sikeresek.
- A spec és a kód szinkronban van (nincs dokumentálatlan döntés).
- A roadmap-fázis ki van pipálva.
```

## Részletesség

Írd le a célokat, korlátokat, sikerkritériumokat, felhasználói folyamatokat és
a fontos technikai döntéseket (rögzített verziók, szigorúság, adatmodell).
Hagyd ki a változóneveket, CSS-osztályokat és a fájlok belső szerkezetét: ezekről
az agent dönt.
