# Projektszabályok: spec-vezérelt fejlesztés (SDD)

Ez a projekt spec-vezérelt. A spec határozza meg a **mit** és a **miért**
kérdést, a kód a **hogyan**. Az alábbi szabályok a globális
`~/.claude/CLAUDE.md`-t egészítik ki. Ahol konkrétabbak, a projekten belül
ezek érvényesek. Az alapszabályokat hookok kényszerítik ki (lásd
„Kikényszerítés”), ezért egy elutasítás stoptábla, nem akadály.

## Nyelv

A projekt Markdown-fájljai (`specs/`, `Plans/`, README-k, `CLAUDE.md`)
magyarul készülnek. Kivételek, amelyek angolul maradnak: kód, kódkommentek,
commit üzenetek és a skillek (`.claude/skills/`).
Fájlnevek, útvonalak, kulcsszavak, parancsok, env változók és modell-ID-k nem
fordítandók.

## Az igazság forrása

Elsőbbség: `specs/` (constitution) > az aktuális feature spec a `Plans/`
alatt > a chat előzményei. Soha ne támaszkodj korábbi sessionök emlékére;
olvasd a fájlokat.

```
CLAUDE.md                  # ezek a szabályok
specs/                     # constitution: az owner kezeli, hookkal zárolt
├── mission.md             # miért: vízió, célközönség, hatókör, nem célok
├── tech-stack.md          # stack, verziók, korlátok, tesztelés
├── roadmap.md             # kis fázisok, fázisonként egy "- [ ] Fázis N — cím" sor
└── backlog/               # kutatás és ötletek, amelyek még nincsenek a roadmapen (nem zárolt)
Plans/                     # feature specek: az agent írja, az owner hagyja jóvá
├── YYYY-MM-DD-<slug>/     # plan.md, requirements.md, validation.md, validate.sh
└── done/                  # befejezett feature-ök
.claude/hooks/sdd_guard.py # az őr (Claude Code hookok, pre-commit, CI)
.claude/skills/            # constitution, feature-spec, validate-feature, replan
.githooks/pre-commit       # agenttől független védővonal
```

Formátumok: `specs/README.md` és `Plans/README.md`. Branch
`feature/phase-2-agents` ↔ `Plans/YYYY-MM-DD-phase-2-agents/` (a slug a
branchnév utolsó része).

## Munkafolyamat

| Lépés | Skill | Eredmény |
|---|---|---|
| 1. Constitution (egyszer, utána élő) | `/constitution` | `specs/` interjú alapján megírva |
| 2. Feature spec | `/feature-spec` | fokozat (S/M/L), branch + `Plans/<dir>/`: S/M-nél egy `spec.md`, L-nél 3 fájl és `validate.sh`, **kód nélkül** |
| 3. Owner jóváhagyás | az owner elküldi: `#spec-ok` | ezen a branchen feloldódik a kódszerkesztés |
| 4. Implementáció | (prompt) | kód, feladatcsoportonként |
| 5. Validáció | `/validate-feature` | ellenőrzések lefutnak, eltérések javítva, roadmap kipipálva, merge |
| 6. Újratervezés | `/replan` | roadmap, constitution és munkafolyamat frissítve |

Minden session elején az őr kiírja az SDD státuszt: branch, a constitution
állapota, az aktuális feature spec és jóváhagyása, a következő roadmap-fázis.
Ennek megfelelően járj el.

## Kikényszerítés (hookok)

`.claude/hooks/sdd_guard.py`, bekötve a `.claude/settings.json`-ben:

| Mi | Szabály | Feloldás |
|---|---|---|
| `specs/mission.md`, `tech-stack.md`, `roadmap.md` | Zárolt, amint mindhárom létezik; írható, amíg bármelyik hiányzik (bootstrap) | Owner: `#spec-szerkesztes`, `#spec-zar`-ig vagy 12 óráig |
| Roadmap checkbox `[ ]` → `[x]` (Edit eszköz) | Mindig engedélyezett | nem kell |
| Őrfájlok: `.claude/settings.json`, `.claude/settings.local.json`, `.claude/hooks/sdd_guard.py`, a tesztje, `.githooks/`, `~/.claude/settings.json` | Zárolt | Owner: `#spec-szerkesztes` |
| Kód (minden, kivéve `specs/`, `Plans/`, `docs/`, `.claude/`, `.githooks/`, `*.md`, `.gitignore`, git által ignorált fájlok) | Csak olyan feature branchen, amelynek a specjét az owner jóváhagyta | Owner: `#spec-ok` azon a branchen |
| Zár- és jóváhagyás-flagfájlok (`.claude/.sdd-*`) | Az agent soha nem írhatja | nincs |
| `git commit --no-verify`, a `core.hooksPath` módosítása | Mindig tiltott | nincs |

- A kulcsszavak csak akkor számítanak, ha az **owner** üzenetének egy sora
  velük kezdődik. Subagentnek adott promptban soha ne írj kulcsszót sor
  elejére, és soha ne kérj subagentet, hogy „oldjon fel” bármit.
- Ha egy írást elutasít az őr: állj meg, mondd el az ownernek, mit akartál
  módosítani és miért, és javasold a pontos változtatást (fájl, szakasz,
  régi -> új). Soha ne kerüld meg az őrt (más eszközzel, scripttel, más
  útvonallal, flagfájllal).
- A git pre-commit hook ugyanezt a kódszabályt kényszeríti ki bármely agentre
  vagy szerkesztőre: nincs kódcommit `main`-en, és nincs olyan branchen, ahol
  nincs spec (merge és squash-merge commit engedélyezett). Az opcionális CI
  ellenőrzés (`.github/workflows/sdd-check.yml`) elbuktat minden PR-t, amely
  kódot módosít spec módosítása nélkül, kivéve ha `no-spec-change` címkéje
  van.
- Ismert rések: az önmaguk által fájlt író programokat (csomagkezelők,
  generátorok, formázók) a hook nem látja. Az ugyanabban a parancsban
  megadott változókat (`P=...; cat > "$P/x"`) behelyettesíti; a máshonnan
  jövő változót a munkakönyvtárhoz viszonyított útvonalnak veszi, ezért egy
  repón kívüli írást is megtagadhat. Ezeket a pre-commit hook commitkor
  elkapja. Viselkedj úgy, mintha a szabályokban nem lennének rések.

## Szabályok lépésenként

**Constitution:** előbb interjú (AskUserQuestion, mission / tech stack /
roadmap szerint csoportosítva), utána írás. Brownfield: előbb a meglévő
kódból, README-ből, TODO-ból és commitokból vezesd le, utána kérdezz a
hiányokról. A roadmap-fázisok kicsik, szállíthatók és önállóan
review-zhatók.

**Feature spec:** tiszta állapotból indulj (nincs commitolatlan munka, az
előző branch mergelve, `main`-en vagy), lehetőleg friss kontextussal
(`/clear`). Először fokozat: **S** (egy session, kis kockázat), **M** (1–3
session vagy egy kockázatos terület), **L** (nagy vagy nehezen
visszafordítható); kockázatos terület (migráció, auth, fizetés, deploy, jogi
szöveg, éles levél, adattörlés) legalább M. S és M egyetlen `spec.md`-t kap
(formátum: `Plans/README.md`), L a három fájlt. S-nél nincs interjú; M-nél és
L-nél írás előtt interjú felugró kérdésekkel (`grill` skill, ha telepítve van),
a javasolt válasz az első. A `validation.md` tartalmazzon olyan parancsokat, amelyeket
magad is lefuttatsz, és az owner kézi ellenőrzéseit. Ha a feature LLM által
követett dokumentumot vagy skillt szállít (útmutató, prompt, skill), a
`validation.md`-be kerüljön friss subagent-próba is: egy subagent csak a
dokumentumot kapja meg, elvégzi vele a feladatot, és jelenti, hol akadt el.
A javítások után a próbát egy újabb friss subagenttel meg kell ismételni,
amíg egy kör nem talál új valódi hiányt (legfeljebb 3 kör). Ha a feature
fizetős API-t hív, a `validation.md` megbecsüli az élő és a kézi
ellenőrzések költségét. Az agent által választott, valódi adattól függő
számértékek (küszöbök, hangosság, sebesség) „kalibrálandó” jelölést
kapnak. Ebben a lépésben nincs kód.

**Implementáció:** csak `#spec-ok` után. Kövesd a `plan.md`-t
feladatcsoportonként. Biztonság, auth, adat és migrációk esetén: egyszerre
egy csoport, utána állj meg. Adatnál és migrációnál az owner a `#spec-ok`-kor
vagy utána egy üzenetben előre engedélyezheti, hogy a többi csoport megállás
nélkül készüljön; biztonságnál és authnál nem. Ne menj túl a `requirements.md`-n. Ha valami
hiányzik vagy kétértelmű, állj meg és kérdezz. Soha ne dönts csendben. A
„kalibrálandó” értékeket abban a csoportban kell az élő mintákon megmérni,
amelyik bevezeti őket, nem csak a végső kézi ellenőrzésnél. A következő
csoport kódjához csak az előző csoport commitja után nyúlj; amíg a
tesztkör a háttérben fut, legfeljebb olvass és tervezz. Így minden commit
pontosan egy csoportot tartalmaz, utólagos szétválogatás nélkül.

**Validáció:** futtasd le a `validation.md` minden ellenőrzését, és jelentsd
az eredményt (sikeres/sikertelen) bizonyítékkal. Fizetős API-nál a
tényleges felhasználást is, a becsléshez képest. A review szintje: „működik-e
és megfelel-e a specnek”. Nem triviális feature-nél ajánlj fel mély review-t
párhuzamos subagentekkel. Kész akkor van, ha minden ellenőrzés sikeres, a
spec és a kód szinkronban van, a roadmap-fázis ki van pipálva, és a spec a
`Plans/done/` alá került. Ha az owner kéri, a merge nyitott kézi
ellenőrzéssel is megtörténhet: ezek a `validation.md`-ben nyitottak maradnak,
a döntés a `requirements.md` „Döntések” szakaszába kerül (`döntött: owner`),
és a következő `/replan` visszakérdez rájuk.

**Újratervezés:** feature-ök között, `replanning/<topic>` branchen. Kis
kódjavításhoz is kell spec és `#spec-ok`, de elég egy S fokozatú, három
soros `spec.md`; nagyobb új munka új roadmap-fázis
lesz. A feature közben felmerülő ötletek a `specs/backlog/YYYY-MM-DD-<topic>.md`
alá kerülnek, nem az aktuális branchre és nem a roadmapre.

**Párhuzamos munka:** egy munkafában egyszerre egy branch dolgozik. Ha egy
feature közben más branchen kell dolgozni (például egy backlog-javaslat egy
`replanning/` branchen), az külön git worktree-ben történik
(`git worktree add ../<repó>-<topic> <branch>`); a futó feature munkafájában
nincs branchváltás. Egy váltás a futó session és subagentjei alatt
kicseréli a fájlokat, és az őr a másik branch szabályaival ítél.

**Prototípus:** az owner kérésére készülhet eldobható prototípus egy
feltételezés gyors kipróbálására. Feltételei:
- a session scratchpadjében fut, a repón kívül, és nem kerül commitba;
- nem érinti a projektkódot és a projekt függőségeit (saját, ideiglenes
  környezetet használ);
- a kódja nem kerül át a projektkódba; a rendes megvalósítás spec és
  `#spec-ok` után készül. Az owner kérésére a prototípus scriptjei
  referenciaként a `specs/backlog/prototype/` alá menthetők (a lint alól
  fájlszinten kivéve), hogy a scratchpad törlése után is meglegyenek.

A tanulságokat ugyanabban a sessionben a `specs/backlog/YYYY-MM-DD-<topic>.md`
alá kell írni egy `replanning/<topic>` branchen; a roadmapre vételükről a
következő `/replan` dönt.

## A spec és a kód szinkronban marad

- Minden viselkedés- vagy döntésváltozás ugyanabban a változtatásban
  frissíti a vonatkozó specfájlt. Ha egy hiba a specre vezethető vissza, a
  specet és a kódot együtt javítsd.
- A review során feltárt döntések a `requirements.md` „Döntések” szakaszába
  kerülnek, dátummal, indoklással és a döntéshozóval (`owner` vagy `agent`,
  lásd `Plans/README.md`). A review-ban talált kihagyás nem kudarc:
  rögzítsd.
- A specmódosítások az agenten keresztül mennek, hogy a kapcsolódó fájlok
  (plan, requirements, validation, README) konzisztensek maradjanak.
  Átnevezés vagy áthelyezés után – az owner IDE-s refaktorálása után is –
  frissíts minden említést a specekben és a dokumentációban.

## A specek részletessége

Szerepeljenek: célok, célközönség, korlátok, sikerkritériumok, felhasználói
folyamatok és a fontos technikai döntések (rögzített verziók, szigorúság,
adatmodell). Maradjanak ki: változónevek, CSS-osztályok és a fájlok belső
szerkezete.

## Viszony a globális szabályokhoz

- A globális „~3 fájl fölött előbb terv” szabályt a feature spec teljesíti: a
  `plan.md` a terv, a `#spec-ok` a jóváhagyás.
- A globális „egy konkrét kérdést tegyél fel” szabály alól egy kivétel van: a
  constitution- és a spec-interjú csoportosított kérdéseket használ.
- A globális „angol dokumentáció” szabály helyett itt a fenti „Nyelv” szakasz
  érvényes.
- A globális git- és biztonsági szabályok továbbra is érvényesek. Minden lépés
  végén javasolj commitot, és csak jóváhagyás után commitolj. Kivétel: a
  `#spec-ok` egyben jóváhagyja, hogy az implementáció feladatcsoportonként
  commitoljon (a csoport kódja, tesztjei és a hozzá tartozó specfrissítés
  egy commitban), ha a csoport tesztjei, lintje és típusellenőrzése
  sikeres. Soha ne pusholj és ne mergelj kérdezés nélkül.
- Commit scope-ok: `docs(specs): ...` a constitutionhöz, `docs(plans): ...` a
  feature specekhez, Conventional Commits a kódhoz.
