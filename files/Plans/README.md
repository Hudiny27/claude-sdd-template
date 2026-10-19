# Plans/: feature specek

Minden roadmap-fázis (és minden kódot érintő újratervezési változtatás) saját
feature specet kap, mielőtt bármilyen kód készülne:

```
Plans/
├── YYYY-MM-DD-<slug>/     # aktív feature, <slug> = a branchnév utolsó része
│   ├── plan.md            # számozott feladatcsoportok
│   ├── requirements.md    # hatókör, hatókörön kívül, döntések, kontextus
│   ├── validation.md      # ellenőrzések, amelyek igazolják, hogy kész és mergelhető
│   └── validate.sh        # a validation.md automatikus ellenőrzései egy futtatható scriptben
└── done/                  # befejezett feature-ök, merge előtt ide kerülnek
```

Branch `feature/phase-2-agents` ↔ könyvtár `Plans/2026-10-05-phase-2-agents/`.
Az SDD őr, a git pre-commit hook és a CI ellenőrzés is e névszabály alapján
találja meg a specet.

## Életciklus

1. `/feature-spec`: branch + interjú + a három fájl és a `validate.sh`. Még
   nincs kód.
2. Owner review. A módosítások az agenten keresztül mennek, hogy a spec fájljai
   konzisztensek maradjanak.
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

## Kalibrálás
<!-- a kalibrálandó értékek mért eredménye, abban a csoportban, amelyik bevezeti őket -->
```

Az agent által választott, valódi adattól függő számértékek (küszöbök,
hangosság, sebesség) „kalibrálandó” jelölést kapnak a döntésükben; a
`plan.md` abban a feladatcsoportban méri őket az élő mintákon, amelyik
bevezeti őket. Az eredmény a `requirements.md` „Kalibrálás” szakaszába
kerül, értékenként (vagy összetartozó értékcsoportonként) egy alszakaszban,
mindig ugyanebben a rendben:

```markdown
### <érték(ek)> (<n>. csoport)
- Minta: <min mért, milyen adaton, milyen beállítással>
- Söprés: | <paraméter> | <eredmény 1> | <eredmény 2> | (a kipróbált értékek és amit mértek)
- Választás: <érték> — <miért ez; mekkora a tartalék a határig>
- Ellenőrzés: <melyik teszt vagy élő teszt őrzi>
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

## Automatikus ellenőrzések (az agent futtatja: `bash Plans/<dir>/validate.sh`)
- [ ] `<parancs>` — <várt eredmény>

## Kézi ellenőrzések (az owner futtatja)
- [ ] <mit kell megnézni, hol>

## Költség (ha fizetős API-t hív)
- <élő és kézi ellenőrzések becsült költsége: karakter, perc, hívás>

## Kész definíciója
- A fenti ellenőrzések mind sikeresek.
- A spec és a kód szinkronban van (nincs dokumentálatlan döntés).
- A roadmap-fázis ki van pipálva.
```

## validate.sh

A `validation.md` minden automatikus ellenőrzése egy bash scriptben, amelyet
az agent a speccel együtt ír meg, és az owner bármikor újrafuttathat. A
spec-mappában él, ezért nem kódnak számít, és nem kell hozzá `#spec-ok`.

- A repó gyökeréből fut: `bash Plans/<dir>/validate.sh`.
- Ellenőrzésenként egy sort ír: `PASS` vagy `FAIL`, az ellenőrzés neve és egy
  rövid bizonyíték (kilépési kód, kulcssor).
- Ha bármelyik ellenőrzés elbukik, nem nulla kóddal lép ki.
- Az ideiglenes fájlokat egy saját ideiglenes könyvtárban tartja, és a végén
  törli.
- Élő, fizetős vagy hálózatot igénylő ellenőrzést csak kapcsolóval futtat
  (például `VTW_LIVE_TESTS=1`).
- A saját mappáját `$(dirname "$0")`-val találja meg, és sehol nem írja be a
  `Plans/<dir>` útvonalat, így a `Plans/done/` alá költözés után is fut.
- A helyi, git által ignorált beállításokat (például az élő minták útvonalát,
  titkot soha) a projekt által dokumentált fájlból olvassa.
- Az élő ellenőrzéseket egy kapcsolóval indítja: `bash Plans/<dir>/validate.sh
  --live` maga tölti be a dokumentált beállításfájlt és állítja be az élő
  kapcsolót, így nem kell kézzel exportálni semmit. Ha a projekt
  tech-stackje memóriakorlátot ír elő a nehéz lépésekre, a script azokat a
  korláttal futtatja.

## Friss subagent-próba

Ha a feature LLM által követett dokumentumot szállít (útmutató, prompt,
skill), a `validation.md` friss subagent-próbát is tartalmaz. Az agent a
validációkor futtatja, módonként (például interaktív, autonóm) egy-egy
próbával, párhuzamosan:

1. **Előkészítés körönként:** friss, eldobható projektmásolat a session
   scratchpadjében. A generált dokumentumokat (például az írási útmutatót)
   a másolaton újra kell generálni, hogy a legutóbbi javítások benne
   legyenek. Minden körnek és próbának saját másolat jár. Ha a próba a
   másolat szándékos rontására épül (például egy kivett lépés vagy egy
   rossz téglalap), a rontást és a várható mellékhatásait (például hogy a
   javítás visszaállítja a jóváhagyott tartalmat) a futtatás előtt le kell
   írni, hogy a próba erről szóló jelzése ne számítson hiánynak.
2. **Prompt:** az alábbi váz, a próba feladatával kitöltve.
3. **Értékelés:** a próba sikeres, ha teljesíti a `validation.md`
   sikerkritériumát. A „talált hiányok” közül csak a valódiak számítanak:
   a próba felállításából adódó félreértés (például egy másolt projekt
   útvonala) nem az.
4. **Javítás és ismétlés:** a valódi hiányok javítása után új, friss
   subagent és új másolat jön, amíg egy kör nem talál új valódi hiányt
   (legfeljebb 3 kör).
5. **Rögzítés:** a körök eredménye (siker, a javított hiányok, a nyitva
   maradt kérdések) a `requirements.md` „Döntések” szakaszába kerül, a
   hatókörön kívüli ötletek a backlogba.

```text
You are testing written instructions for an AI writer. Work only from the
documents named here; do not read the source code or tests.

Documents you may read:
- <the document(s) under test, with absolute paths>
- <the inputs the task needs, e.g. a project's generated files>

The project is a scratch copy: <absolute path>. <what is already there and
must not change>.

Situation: <mode, e.g. interactive at the review gate>. Do only this part:
1. <the task, step by step>
2. Then assume the owner answered: "<the owner's answer>". <what to do next>.

Rules: run commands from <repo> with <command prefix>. Never run <paid or
irreversible commands>. Write nothing outside <allowed folders>.

Report back (plain text), briefly:
- <the result items the success criterion needs>;
- every place where the documents were unclear, missing something,
  contradicting each other, or where you had to guess, quoting the passage.
  This list is the most important part; leave out what you found clear.
```

## Részletesség

Írd le a célokat, korlátokat, sikerkritériumokat, felhasználói folyamatokat és
a fontos technikai döntéseket (rögzített verziók, szigorúság, adatmodell).
Hagyd ki a változóneveket, CSS-osztályokat és a fájlok belső szerkezetét: ezekről
az agent dönt.
