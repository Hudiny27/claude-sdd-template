# Projektszabályok: spec-vezérelt fejlesztés (SDD)

Ez a projekt spec-vezérelt. A spec határozza meg a **mit** és a **miért**
kérdést, a kód a **hogyan**. Az alábbi szabályok a globális
`~/.claude/CLAUDE.md`-t egészítik ki. Ahol konkrétabbak, a projekten belül
ezek érvényesek. Az alapszabályokat hookok kényszerítik ki (lásd
„Kikényszerítés”), ezért egy elutasítás stoptábla, nem akadály.

## Az igazság forrása

Elsőbbség: `specs/` (constitution) > az aktuális feature spec a `Plans/`
alatt > a chat előzményei. Soha ne támaszkodj korábbi sessionök emlékére;
olvasd a fájlokat.

```
CLAUDE.md                  # ezek a szabályok (sablonfájl)
specs/                     # constitution: az owner kezeli, hookkal zárolt
├── mission.md             # miért: vízió, célközönség, hatókör, nem célok
├── tech-stack.md          # stack, verziók, korlátok, tesztelés
├── roadmap.md             # kis fázisok, fázisonként egy "- [ ] Fázis N: cím" sor
└── backlog/               # kutatás és ötletek, amelyek még nincsenek a roadmapen (nem zárolt)
Plans/                     # feature specek: az agent írja, az owner hagyja jóvá
├── YYYY-MM-DD-<slug>/     # S/M: spec.md (+ validate.sh); L: plan.md, requirements.md, validation.md, validate.sh
└── done/                  # befejezett feature-ök
.claude/hooks/sdd_guard.py # az őr (Claude Code hookok, pre-commit, CI)
.claude/bin/sdd            # parancsok: preflight, new, handover, archive, commit
.claude/lib/               # a validate.sh könyvtárai és a lint (sdd_lint.py)
.claude/skills/            # constitution, feature-spec, validate-feature, replan, segédfájlaikkal
.claude/project.md         # a projekt saját, mindig betöltött kiegészítése
.claude/rules/             # a projekt saját szabályai, útvonalhoz kötve
.claude/workflow-log.md    # helyi munkafolyamat-javítások naplója (10 tételenként review)
.githooks/pre-commit       # agenttől független védővonal
```

Formátumok: `specs/README.md` és `Plans/README.md`. Branch `feature/phase-2-agents`
↔ `Plans/YYYY-MM-DD-phase-2-agents/` (a slug a branchnév utolsó része:
`phase-<N>-` és rövid angol kebab-case a fázis címéből; a dátum a spec
megírásának napja).
Roadmapen kívüli S javítás branchneve `fix/<slug>`; ennek nincs fázisa.

## Munkafolyamat

| Lépés | Skill | Eredmény |
|---|---|---|
| 1. Constitution (egyszer, utána élő) | `/constitution` | `specs/` interjú alapján megírva |
| 2. Feature spec | `/feature-spec` | fokozat (S/M/L), branch + `Plans/<dir>/`: S/M-nél egy `spec.md`, L-nél 3 fájl és `validate.sh`, **kód nélkül** |
| 3. Owner jóváhagyás | az owner elküldi: `#spec-ok` | ezen a branchen feloldódik a kódszerkesztés |
| 4. Implementáció | (prompt) | kód, feladatcsoportonként |
| 5. Validáció | `/validate-feature` | ellenőrzések lefutnak, eltérések javítva, roadmap kipipálva, merge |
| 6. Újratervezés | `/replan` | roadmap, constitution és munkafolyamat frissítve |

Az őr minden session elején kiírja az SDD státuszt (branch, constitution,
aktuális spec és jóváhagyása, következő fázis); ennek megfelelően járj el.

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
| `git add -A`/`.`, `git commit -a`, `pkill -f`, branchváltás futó feature munkafájában, `#spec-` kezdetű sor subagent promptban | Tiltott; az üzenet megnevezi a jó utat | nincs |

- A kulcsszavak csak akkor számítanak, ha az **owner** üzenetének egy sora
  velük kezdődik. Subagenttől soha ne kérj feloldást vagy jóváhagyást.
- Ha egy írást elutasít az őr: állj meg, mondd el az ownernek, mit akartál
  módosítani és miért, és javasold a pontos változtatást (fájl, szakasz,
  régi -> új). Soha ne kerüld meg az őrt (más eszközzel, scripttel, más
  útvonallal, flagfájllal). Viselkedj úgy, mintha a szabályokban nem
  lennének rések.
- A pre-commit hook (a linttel együtt) és a CI (`sdd-check.yml`) ugyanezt minden szerkesztőre kényszeríti.

## Sablon és projekt

A sablon fájljait (`CLAUDE.md`, a skillek és segédfájljaik, a két README, a
hookok, a `.claude/lib/` és a `.claude/bin/`) a projekt nem szerkeszti: az `install.sh --update` felülírja őket. A
projekt tanulságai a bővítési pontokra kerülnek: `.claude/rules/<téma>.md`
(fájlokhoz kötve `paths:` frontmatterrel, enélkül induláskor töltődik be),
`.claude/project.md`, és a projekt saját scriptjei és tesztjei. A
szabályhely sorrendje: `/replan`. A projekt kiegészítése: @.claude/project.md

## Szabályok lépésenként

**Feature spec:** először fokozat: **S** (egy session, kis kockázat), **M**
(1–3 session vagy egy kockázatos terület), **L** (nagy vagy nehezen
visszafordítható); kockázatos terület (migráció, auth, fizetés vagy fizetős
API, deploy, jogi szöveg, éles levél, adattörlés, a felhasználók meglévő
fájljaitól függő formátum) legalább M. Ha a fokozat menet közben nő, állj
meg, bővítsd a specet, és kérj új `#spec-ok`-ot; az őr addig tilt.

**Implementáció:** csak `#spec-ok` után. L-nél a `plan.md`-t kövesd
feladatcsoportonként, S-nél és M-nél a `spec.md`-t; kezdés előtt olvasd el a
`.claude/skills/feature-spec/implement.md`-t. Biztonság, auth, adat és
migrációk esetén (L): egyszerre egy csoport, utána állj meg. Adatnál és
migrációnál az owner a `#spec-ok`-kor vagy utána egy üzenetben előre
engedélyezheti, hogy a többi csoport megállás nélkül készüljön;
biztonságnál és authnál nem. Ne menj túl a hatókörön (`requirements.md`,
S/M-nél a `spec.md` „Bele tartozik” része). Ha valami
hiányzik vagy kétértelmű, állj meg és kérdezz. Soha ne dönts csendben. A
következő csoport kódjához csak az előző csoport commitja után nyúlj. Így
minden commit egy csoport.

**Ötletek:** a feature közben felmerülő ötletek a `specs/backlog/` alá
kerülnek, nem a branchre és nem a roadmapre; ezt a subagent promptjába is írd.

**Prototípus:** az owner kérésére, eldobhatóan: a session scratchpadjében,
a repón kívül, saját ideiglenes környezettel, commit nélkül; a kódja nem
kerül át a projektkódba, a rendes megvalósítás spec és `#spec-ok` után
készül. Tanulságai ugyanabban a sessionben a `specs/backlog/` alá kerülnek
egy `replanning/<topic>` branchen; a roadmapről a következő `/replan` dönt.

## A spec és a kód szinkronban marad

- Minden viselkedés- vagy döntésváltozás ugyanabban a változtatásban
  frissíti a vonatkozó specfájlt. Ha egy hiba a specre vezethető vissza, a
  specet és a kódot együtt javítsd.
- A review során feltárt döntések a „Döntések” szakaszba kerülnek, dátummal,
  indoklással és döntéshozóval (lásd `Plans/README.md`). A review-ban talált
  kihagyás nem kudarc: rögzítsd.
- A specmódosítások az agenten keresztül mennek, hogy a kapcsolódó fájlok
  (plan, requirements, validation, README) konzisztensek maradjanak.

## Döntések és következő lépések felugró ablakban

- Az ablak előtt a chatben röviden ott van az eredmény, a bizonyíték, a
  feltételezések és a kockázat; az ablak csak a döntést kéri.
- Az egymástól független döntések egy ablakba kerülnek (legfeljebb négy
  kérdés). Ha egy lépés végén több, egymást nem kizáró teendő van (például
  commit, merge, egy próbamappa törlése, a következő skill), ezek egy
  többválasztós kérdésbe (`multiSelect`) kerülnek. Az agent csak a
  bejelölt teendőket hajtja végre, a felsorolt sorrendben.
- A kulcsszavak (`#spec-ok`, `#spec-szerkesztes`, `#spec-zar`) nem
  kattinthatók: az ablakban adott válasz nem jóváhagyás. Az agent a chat
  végén pontosan megmondja, mit kell begépelni.

## Viszony a globális szabályokhoz

- A globális „~3 fájl fölött előbb terv” szabályt a feature spec teljesíti:
  a `plan.md` a terv, a `#spec-ok` a jóváhagyás.
- A `#spec-ok` jóváhagyja, hogy az implementáció feladatcsoportonként
  commitoljon (a csoport kódja, tesztjei és specfrissítése egy commitban),
  ha a csoport tesztjei, lintje és típusellenőrzése sikeres. S és M
  fokozatnál a teljes változás egy commit, miután az ellenőrzései
  sikeresek. Commitolni a `.claude/bin/sdd commit -m … -- <fájlok>`
  paranccsal kell: csak zöld `.claude/check.sh` után commitol.
