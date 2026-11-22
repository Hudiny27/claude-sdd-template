---
szint: L
allapot: tervezet
---
# Terv: a sablon átalakítása maggá

Alapja: `2026-11-22-matt-pocock-osszevetes.md` (a javaslat) és
`2026-11-22-sablon-atvilagitas.md` (a 231 szabály besorolása). Minden
szakasz külön branchen készül a sablon repójában, a végén owner-átnézés, és
csak utána jön a következő. Push és merge csak kérésre.

## Közös elvek minden szakaszra

- **Sablonfájl és projektfájl szétválik.** A sablon fájljait a projekt nem
  szerkeszti; frissítéskor felülíródnak. A projekt saját tanulságai a
  bővítési pontokra kerülnek: `.claude/rules/*.md` (útvonalhoz kötve),
  `.claude/project.md` (a projekt rövid, mindig betöltött kiegészítése, a
  CLAUDE.md egy sorral hivatkozik rá), a projekt saját scriptjei és tesztjei.
- **Méretkeret, teszttel őrizve:** CLAUDE.md legfeljebb 150 sor, SKILL.md
  legfeljebb 100 sor, a lépések részletei a skill mappájában segédfájlban.
- **Szabályhely-sorrend:** kód vagy ellenőrzés → útvonalhoz kötött szabály →
  egy lépés segédfájlja → CLAUDE.md.

## 1. szakasz: törlés és átrendezés (csak szöveg)

1. A 62 „üres” szabály törlése; a duplikátumokból egy hely marad.
2. A 14 „projektfüggő” szabály kivétele a sablonból. A pii-pajzsban élő
   megfelelőjük érintetlen marad; a sablon `backlog/` mappájába egy lista
   kerül arról, mi ment ki és hova tartozna.
3. A nyelvi és felugró ablakos szabályok törlése (owner döntése: a globális
   CLAUDE.md tartalmazza).
4. A `feature-spec` és a `validate-feature` lépésenként mutató lesz; a
   `validate.sh`-, próba- és kalibrálásrészletek segédfájlokba kerülnek a
   skill mappájában, a lépés szövegéből hivatkozva.
5. A `/replan` 10 tételenkénti review-jának új célja: helyben rendet tenni
   (kóddá alakítani, összevonni, törölni); a sablonba emelés szigorú kapuval
   (mechanizmus, legalább két projekt, helyben nem oldható meg).
6. `install.sh --update`: a sablon saját fájljait felülírja, a bővítési
   pontokhoz soha nem nyúl; előtte diffet mutat.

Ellenőrzés: a meglévő őrtesztek zöldek; méretkeret-teszt (új, a sablon
tesztjei közé); friss subagent-próba egy mintaprojekten egy M fokozatú spec
megírásával csak a karcsúsított sablonnal, legfeljebb 3 kör.

Kockázat: egy törölt szabály valódi hibát előzött meg. Visszaút: a
táblázat minden törlést indokol, a git története visszaadja a szöveget.

## 2. szakasz: közös ellenőrző könyvtár

1. `files/.claude/lib/sdd_check.sh` az átvilágítás „Közös lib-függvények”
   listája szerint (`sdd_init`, `check`, `sdd_finish`, `start_bg`,
   `free_port`, `export_main`, `run_suite`, `full_once`, `live_only`,
   `assert_absent`, `check_url`, `prove_red`, `suite_lock`).
2. `files/.claude/lib/sdd_probe.sh` (`probe_base`, `probe_copy`,
   `snapshot_status`, `assert_no_new_files`) projekthorgokkal.
3. Tesztek a sablon repójában, minden függvényre legalább egy bukó és egy
   sikeres eset (például: a `start_bg`-vel indított folyamat a script hibás
   kilépése után sem fut).
4. A `Plans/README.md` `validate.sh`-szakasza néhány sorra rövidül: „használd
   a lib-et; ha valami hiányzik belőle, bővítsd a lib-et a sablonban”.

Ellenőrzés: a lib tesztjei; egy minta `validate.sh` a lib-bel, `shellcheck`
tisztán.

Kockázat: a lib hibája minden projektet érint. Ezért van saját teszt, és a
meglévő projektek régi `validate.sh`-i változatlanul futnak tovább.

## 3. szakasz: lint, `sdd` parancs, őrbővítés

1. `sdd_lint.py`: spec-formátum, Döntések-sorok, kalibrálás, lefedettség,
   beírt útvonalak, shell-lint, lógó útvonalak, méretkeret. A pre-commit hook
   és a `validate-feature` futtatja.
2. `sdd new`, `sdd handover`, `sdd archive`, `sdd commit` parancsok.
3. Az őr új tiltásai: `git add -A`/`.`, `git commit -a`, `pkill -f`,
   branchváltás futó feature alatt, kulcsszóval kezdődő sor subagent
   promptban. A státusz a nyitott kézi ellenőrzések számát is kiírja.
4. A kiváltott mondatok törlése a skillekből.

Ellenőrzés: az őr regressziós tesztjei bővülnek minden új tiltásra (a
javítás előtt bukó teszttel); a lint tesztjei.

Kockázat: az őr túl szigorú lesz, és megakaszt egy jogos lépést. Minden
tiltás üzenete megmondja a jogos utat. Az őr fájljainak szerkesztéséhez a
pii-pajzsban `#spec-szerkesztes` kell; a sablon repójában nincs zár, de az
owner minden őrváltozást a szakasz végén átnéz.

## 4. szakasz: a stratégiai réteg

1. **Szótár:** `docs/szotar.md` formátum (Matt `GLOSSARY.md`-je alapján:
   fogalom, 1–2 mondat, kerülendő szinonimák, a kódbeli név). A `grill`
   tiltása helyett lusta bővítés a kikérdezés közben.
2. **Döntésnapló:** a meglévő `docs/decisions/` minta (pii-pajzs) és Matt
   ADR-feltétele (nehezen visszafordítható, kontextus nélkül meglepő, valódi
   mérlegelés eredménye; ha egy hiányzik, nincs ADR).
3. **Kódszerkezet-felmérés:** globális skill Matt
   `improve-codebase-architecture` és `codebase-design` skillje alapján (MIT
   licenc, a forrásmegjelöléssel), a `/replan` felajánlja, a találatok a
   backlogba mennek.
4. **Kockázat szerinti review:** a spec „Kockázat és visszaút” szakasza
   kap egy `ajtó:` és egy `hatósugár:` mezőt; a `validate-feature` átadása
   ebből méretezi a kért kézi ellenőrzést.
5. **Szabályok a reviewernek, nem az implementálónak:** a projekt kódolási
   szabályai (`docs/kodolasi-szabalyok.md`, csak mérlegelést igénylő ügyek)
   a mély review subagentjeinek kontextusába kerülnek, nem a CLAUDE.md-be.

Ellenőrzés: egy csak olvasó próbafutás a pii-pajzson (szótár-kivonat és
kódszerkezet-riport), amelyet az owner értékel.

## Utána: a pii-pajzs átállása

Külön, a pii-pajzs saját SDD-folyamatában (`replanning/` branch, külön
worktree, a futó feature-től függetlenül): `install.sh --update`, a projekt
helyi szabályainak átköltöztetése a bővítési pontokra, a `validate.sh`-k
lib-re állítása csak új specekben.

## Döntések

- 1. szakasz, friss subagent-próba (M fokozatú spec egy mintaprojekten, csak a karcsúsított sablonnal), két kör (döntött: agent, 2026-11-22):
  - 1. kör: 3 lényeges hiány (M-nél a `plan.md`-re mutató implementációs utasítás; a `validate.sh` által hívott felület rögzítése ütközött a „hagyd ki a belső szerkezetet” szabállyal; a kód előtti offline futás nem tudta elérni a kódot igénylő ágakat), mind a három a régi sablonban is megvolt; javítva (`339add1`).
  - 2. kör: nincs új lényeges hiány. A próba egy tételt lényegesnek jelölt (adatfeltöltés a szerverpróbához egy létrehozó végpont nélküli appban); ez a mintaapp tervezési kérdése, az agent `agent` döntésként rögzítette, ezért a mérce szerint apró. Az apró hiányok közül a M fokozatot félrevezetők javítva (`16a6879`).
- Az `install.sh --update` nem írja felül a `.claude/settings.json`-t, csak a diffet mutatja, mert a projektek saját hookokat és engedélyeket fésülnek bele (döntött: agent, 2026-11-22).
- A roadmap sorformátuma `- [ ] Fázis N: cím` (gondolatjel helyett kettőspont); az őr csak a `- [ ] ` előtagot olvassa (döntött: agent, 2026-11-22).
- A 3. szakaszra vár: az őr státuszszövege még a régi review-célt írja („sablonba, helyben, törlés”), a drift-ellenőrzése nem látja az új segédfájlokat, és a `.githooks/pre-commit` docstringje csak a három fájlos L specet említi.
