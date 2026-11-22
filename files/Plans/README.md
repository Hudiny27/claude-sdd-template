# Plans/: feature specek

```
Plans/
├── YYYY-MM-DD-<slug>/     # aktív feature, <slug> = a branchnév utolsó része
│   ├── plan.md            # számozott feladatcsoportok
│   ├── requirements.md    # hatókör, hatókörön kívül, döntések, kontextus
│   ├── validation.md      # ellenőrzések, amelyek igazolják, hogy kész és mergelhető
│   └── validate.sh        # a validation.md automatikus ellenőrzései egy futtatható scriptben
├── YYYY-MM-DD-<slug>/     # S vagy M fokozatú munka: egyetlen fájl
│   └── spec.md
└── done/                  # befejezett feature-ök, merge előtt ide kerülnek
```

Egy M fokozatú spec mellé is kerülhet `validate.sh`, ha az „Ellenőrzés”
szakasz több gépi ellenőrzést egy parancsra fűz. Az alábbi sablonokat a
`.claude/bin/sdd new` másolja be; a formátumot a `.claude/lib/sdd_lint.py`
ellenőrzi (a pre-commit hook futtatja).

## spec.md (S és M fokozat)

```markdown
---
szint: S | M
---
# <cím>

Roadmap: Fázis <n>: <cím> (vagy: nincs, `fix/` javítás)
Branch: <branch>

## Cél
<1–3 mondat: mit akar elérni az owner, és miért.>

## Bele tartozik
- …

## Nem tartozik bele
- …

## Döntések
- <döntés>: <miért> (döntött: owner | agent, ÉÉÉÉ-HH-NN)

## Kontextus (ha a kikérdezés tényt talált)
- <tény, és honnan tudjuk: fájl:sor, parancs, dokumentum>

## Kész, ha
- <ellenőrizhető állítás>

## Ellenőrzés
- [ ] Agent: <parancs vagy teszt> → <várt eredmény> (validate.sh esetén: `bash Plans/<dir>/validate.sh`, a check azonosítója: <ID>; ami a kód előtt csak bukhat, itt jelölve)
- [ ] Owner: <1–3 lépés, amit ő maga megnéz>

## Kockázat és visszaút
- ajtó: egyirányú | kétirányú: <visszavonható-e teljesen, és mivel>
- hatósugár: kicsi | közepes | nagy: <kit vagy mit ér el, ha elromlik>
- <mi romolhat el, és hogyan vonjuk vissza>

## Költség (ha fizetős API-t hív)
- <becslés: karakter, perc, hívás; élő és kézi ellenőrzésre külön>

## Kalibrálás (ha van kalibrálandó érték)
- <érték, mért eredmény, minta>
```

S fokozatnál elég a „Cél”, a „Kész, ha” és az „Ellenőrzés”; a többi szakasz
elhagyható.

A két kockázati mező (M és L fokozatnál kötelező) méretezi a validálás
végén kért kézi munkát. `ajtó`: egyirányú, ha a változás nem vonható vissza
teljesen (adatvesztés, kiküldött levél vagy adat, migráció, éles
konfiguráció); kétirányú, ha egy revert mindent helyreállít. `hatósugár`:
kicsi (egy felület vagy fájl, csak fejlesztői hatás), közepes (egy
felhasználói folyamat), nagy (minden felhasználó, adat vagy kimenő
forgalom). A projekt szigoríthat a saját szabályában (például „ami kimenő
adatot érint, az mindig nagy”).

## plan.md

```markdown
# Terv: <feature>

Roadmap: Fázis <n>: <cím>
Branch: feature/<slug>

## 1. csoport: <név>
1. <feladat>
2. <feladat>

## 2. csoport: <név>
3. <feladat>

## N. csoport: Ellenőrzés
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
- <döntés>: <miért> (döntött: owner | agent, ÉÉÉÉ-HH-NN)

## Kontextus
- <korlátok, kapcsolódó kód, érintettek megjegyzései>

## Kockázat és visszaút
- ajtó: egyirányú | kétirányú: <visszavonható-e teljesen, és mivel>
- hatósugár: kicsi | közepes | nagy: <kit vagy mit ér el, ha elromlik>
- <mi romolhat el, és hogyan vonjuk vissza>

## Kalibrálás
<!-- a kalibrálandó értékek mért eredménye, abban a csoportban, amelyik bevezeti őket -->
```

Az agent által választott, valódi adattól függő számértékek „kalibrálandó”
jelölést kapnak; a mérés és a „Kalibrálás” szakasz formátuma:
`.claude/skills/feature-spec/calibration.md`.

Minden döntésnél jelölni kell, ki hozta. `owner`: a spec-interjúból, a
constitutionből vagy az owner kifejezett kéréséből származik. `agent`: az
agent döntötte el (feltételezés, alapérték, implementációs választás), és
a `#spec-ok` hagyja jóvá; a review során később hozott agent-döntésekre az
owner rákérdezhet. Soronként egy döntéshozó szerepel, a vegyes döntéseket
szét kell bontani. Ha egy döntés felvált egy korábbit, ugyanabban a
változtatásban a régi a végén `(felváltva ÉÉÉÉ-HH-NN, lásd …)` jelölést
kap; a régi nem törlődik.

## validation.md

```markdown
# Validáció: <feature>

## Automatikus ellenőrzések (az agent futtatja: `bash Plans/<dir>/validate.sh`)
- [ ] `<parancs>`: <várt eredmény>

## Kézi ellenőrzések (az owner futtatja)
- [ ] <mit kell megnézni, hol>

## Költség (ha fizetős API-t hív)
- <élő és kézi ellenőrzések becsült költsége: karakter, perc, hívás>

## Kész definíciója
- A fenti ellenőrzések mind sikeresek.
- A spec és a kód szinkronban van (nincs dokumentálatlan döntés).
- A roadmap-fázis ki van pipálva.
```

Ha a feature LLM által követett dokumentumot szállít (útmutató, prompt,
skill), a `validation.md` friss subagent-próbát is tartalmaz:
`.claude/skills/feature-spec/probe.md`.

## validate.sh

A `validation.md` minden automatikus ellenőrzése egy bash scriptben, amelyet
az agent a speccel együtt ír meg; a spec-mappában él, ezért nem kódnak
számít, és nem kell hozzá `#spec-ok`. A sablon közös könyvtárát
(`.claude/lib/sdd_check.sh`) forrásolja be, és annak függvényeivel
ellenőriz; ha valami hiányzik belőle, a könyvtár a sablonban bővül. Minta
és szabályok: `.claude/skills/feature-spec/validate-sh.md`.

## köteg.md (kötegelt üzemmód)

Egy köteg több feature-t visz egy jóváhagyással (`#spec-ok köteg <név>`),
felügyelet nélküli építéssel és reggeli merge-döntéssel. A fájl a `main`
checkoutban él: `Plans/kotegek/ÉÉÉÉ-HH-NN-<név>.md`; az `sdd batch new`
hozza létre, az `sdd batch add` ad hozzá egy feature-t a saját worktree-jével
(`.claude/worktrees/<slug>`) és spec-mappájával.

```markdown
---
koteg: <név>
datum: ÉÉÉÉ-HH-NN
idokeret: ÓÓ:PP
artifact: igen | nem
---
# Köteg: <név>

## Feature-ök
| # | Branch | Fokozat | Függ | Worktree | Becslés | Auth/biztonság | Állapot |
|---|---|---|---|---|---|---|---|

## Közös döntések
- <döntés, amely több feature-re érvényes>: <miért> (döntött: owner | agent, ÉÉÉÉ-HH-NN)
```

- `Függ`: annak a feature-nek a branche, amelyre ez épül, vagy `-`.
- `Auth/biztonság`: `nem`; auth- vagy biztonsági feature nem lehet kötegben.
- `Állapot`: spec | jóváhagyva | épül | merge-kész | parkolva | mergelve |
  javítás | elvetve.

## Részletesség

Írd le a célokat, korlátokat, sikerkritériumokat, felhasználói folyamatokat és
a fontos technikai döntéseket (rögzített verziók, szigorúság, adatmodell).
Hagyd ki a változóneveket, CSS-osztályokat és a fájlok belső szerkezetét: ezekről
az agent dönt. Kivétel a nyilvános felület, amelyet a `validate.sh` vagy egy
teszt hív (függvény és paraméterei, végpont, parancssori kapcsoló): ez
`agent` döntésként a „Döntések” alá kerül. A `validate.sh` lehetőleg csak
ezen a felületen és a látható viselkedésen át ellenőriz.
