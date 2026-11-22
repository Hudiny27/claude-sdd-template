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
- A 3. szakaszra vár: az őr státuszszövege még a régi review-célt írja („sablonba, helyben, törlés”), a drift-ellenőrzése nem látja az új segédfájlokat, és a `.githooks/pre-commit` docstringje csak a három fájlos L specet említi. (elvégezve a 3. szakaszban, 2026-11-22)
- 2. szakasz: a lib két függvénnyel bővebb a megbízásnál: `prove_red` (a terv listájában szerepel) és `wait_port` (a `start_bg`-vel indított szerver megvárásához) (döntött: agent, 2026-11-22).
- 2. szakasz: a `full_once` nem a git tree hasht nézi, hanem a munkafa kódfájljainak tartalmát az őr kóddefiníciója szerint (`specs/`, `Plans/`, `docs/`, `.claude/`, `.githooks/`, `*.md`, `.gitignore` nélkül), és a parancsot is a kulcsba veszi; így az archiválás és a doksiváltozás nem indít új teljes kört. A `--quick` megmaradt: a `full_once`-t feltétel nélkül kihagyja (döntött: agent, 2026-11-22).
- 2. szakasz: a `check` alhéjban, bekapcsolt `errexit`-tel futtatja a parancsot, ezért egy többlépéses ellenőrzés az első hibánál megáll; emiatt `start_bg` nem hívható `check`-en belül, és a fő shellen kívül hibát ad (döntött: agent, 2026-11-22).
- 2. szakasz: a `start_bg` saját folyamatcsoportba indít (`set -m`), és a csoportot állítja le, így a parancs gyerekfolyamatai sem maradnak futva; a kimenet a `$SDD_TMP/NAME.log` fájlba megy (döntött: agent, 2026-11-22).
- 2. szakasz: a `live_only` előtagként használható (`live_only check ...`), argumentum nélkül csak igaz/hamis értéket ad (döntött: agent, 2026-11-22).
- 2. szakasz: az `assert_absent` a `--proof-file FILE` alakot is elfogadja, és hiányzó célfájlnál bukik; a `check_url` opcionális `--host HOST` paraméterrel a végső hostot is ellenőrzi; az `sdd_finish` akkor is bukik, ha egy ellenőrzés sem futott (döntött: agent, 2026-11-22).
- 2. szakasz: az `export_main` második, opcionális paramétere a ref (alapértelmezés `main`), a kicsomagolást `tar` helyett `python3` végzi, hogy a függőséglista ne bővüljön; a `prove_red` ideiglenes munkafa helyett ilyen exportban fut, így nem marad `git worktree` bejegyzés (döntött: agent, 2026-11-22).
- 2. szakasz: a `probe_copy` másolata `<másolat>/repo` és (ha a `probe_base` lefutott) `<másolat>/sample`; a `SDD_PROBE_ROOT` kötelező, abszolút és a repón kívüli; a `probe_base` az alapmásolatot akkor építi újra, ha a minta tartalma változott (döntött: agent, 2026-11-22).
- 2. szakasz: a `snapshot_status` a pillanatképet a `.git/` alá menti, hogy a próba előtti és utáni hívás külön futás lehessen; a `git status` sorait veti össze, így egy már előtte módosított fájl újabb módosítását nem látja (döntött: agent, 2026-11-22).
- 2. szakasz: a `suite_lock` csak a scripteket tartja távol egymástól; a subagent-próbát az agent indítja, nem script, ezért a „próbakör nem fut a `validate.sh` alatt” szabály szövegként maradt a `validate-sh.md`-ben (döntött: agent, 2026-11-22).
- 2. szakasz: a megbízáson túl az `implement.md` (`prove_red`) és a `validate-feature/finish.md` (`full_once` az archiválás után) is rövidült, mert ezek is a lib által kiváltott szabályt tartalmaztak; a `Plans/README.md` 2 sorral nőtt, a minta `validate.sh` a `validate-sh.md`-be került, és egy teszt le is futtatja (döntött: agent, 2026-11-22).
- 2. szakasz, a friss agent `validate.sh`-próbája után: az új `check_http` nem követi az átirányítást (így a pontos `--status` egy 3xx-et is ellenőrizhet), `--status` nélkül bármely 2xx-et elfogad, csak GET-et küld, és a `--body-equals` a záró sortöréseket figyelmen kívül hagyja; a `check_url` változatlanul a végső státuszt és hostot nézi (döntött: agent, 2026-11-22).
- 2. szakasz: az `assert_absent --allow-empty` csak az üres célt engedi; a hiányzó cél továbbra is mindig bukik, mert az többnyire rossz útvonal (döntött: agent, 2026-11-22).
- 2. szakasz: a korai kilépés (errexit `check`-en kívül, `exit`, jel) mellett az is `FAIL  EXIT` sor, összegzés és nem nulla kilépési kód, ha a script `sdd_finish` nélkül, 0-val ér véget (döntött: agent, 2026-11-22).
- 2. szakasz: a `stop_bg` SIGTERM után 5 másodperccel SIGKILL-t küld, mint az EXIT trap; a minta szerver `python3 -u`-val fut, mert a SIGTERM a pufferelt stdout-ot elveszíti (döntött: agent, 2026-11-22).
- 2. szakasz: a `Plans/README.md` döntéssor-formátuma mindenhol `(döntött: owner | agent, ÉÉÉÉ-HH-NN)`; ugyanígy a `felváltva` jelölés dátuma is `ÉÉÉÉ-HH-NN` lett (döntött: agent, 2026-11-22).
- 2. szakasz, friss subagent-próba (M fokozatú spec és `validate.sh` a könyvtárral, egy HTTP-végpont feature-re), két kör (döntött: agent, 2026-11-22):
  - 1. kör: 3 lényeges hiány (nem volt törzs- és pontos státusz-ellenőrzés; a mintában a `wait_port` korai kilépése néma volt; az `assert_absent` üres vagy még író naplón is átment); regressziós tesztekkel javítva (`ed58fa2`, `817127c`).
  - 2. kör: nincs lényeges hiány; a két körben is előjött apróságok (Roadmap- és Branch-sor a `spec.md` sablonban, a check azonosítójának megnevezése) javítva.
- 3. szakasz: az `sdd` parancs Python script a `.claude/bin/sdd` alatt (`preflight`, `new`, `handover`, `archive`, `commit`); az őrt és a lintet importálja, így az útvonalszabályok egy helyen maradnak (döntött: agent, 2026-11-22).
- 3. szakasz: az `sdd commit` a projekt saját `.claude/check.sh` scriptjét futtatja (lint, típus, teszt, 0 kilépés, ha minden zöld); a `/constitution` írja meg a tech-stackből, az `install.sh --update` nem nyúl hozzá; hiányában az `sdd commit` megáll és megmondja, mit kell írni (döntött: agent, 2026-11-22).
- 3. szakasz: a pre-commit hook a `sdd_lint.py --staged` hibájára megállítja a commitot; merge és squash-merge commitnál nem lintel, és ha a lint hiányzik (régi telepítés), csak figyelmeztet (döntött: agent, 2026-11-22).
- 3. szakasz: a lógó útvonalak ellenőrzése csak `--final` módban fut (a `/validate-feature` 3. lépésében), mert egy friss spec még nem létező fájlokat nevez meg; csak a branchen változott Markdownt és a törölt vagy átnevezett fájlok említéseit nézi, és csak olyan útvonalat, amelynek az első mappája létezik (így a branchnevek és a `<dir>` minták kimaradnak) (döntött: agent, 2026-11-22).
- 3. szakasz: a kalibrálás eredményét csak a `--final` mód követeli meg; a „Kalibrálás” alszakaszok mezősorrendjét mindig ellenőrzi (döntött: agent, 2026-11-22).
- 3. szakasz: a Döntések-sorokat a lint a `main`-nel veti össze (a `main`-en a `HEAD`-del): az ott meglévő sor nem törölhető és nem fogalmazható át, csak `(felváltva ÉÉÉÉ-HH-NN, lásd …)` jelölést kaphat (döntött: agent, 2026-11-22).
- 3. szakasz: a lefedettség-ellenőrzés alól a friss subagent-próba sora kivétel; a lint a `subagent`, `próba`, `probe` szóról ismeri fel (döntött: agent, 2026-11-22).
- 3. szakasz: a méretkeret új eleme a `.claude/project.md` legfeljebb 60 sora; a lint a projekt saját skilljeire is a 100 soros keretet alkalmazza (döntött: agent, 2026-11-22).
- 3. szakasz: a terven túl a lint a bent maradt sablonhelyeket is jelzi (`<mit írj ide>`, `- …`), mert az `sdd new` a sablonokat másolja be (döntött: agent, 2026-11-22).
- 3. szakasz: a branchváltás tilalma csak jóváhagyott, még nem archivált spec mellett él; a fájl-visszaállító `checkout` (`git checkout -- <fájl>`, `git checkout main -- <fájl>`) és a `git worktree add` szabad (döntött: agent, 2026-11-22).
- 3. szakasz: a subagent-prompt ellenőrzéséhez a `.claude/settings.json` PreToolUse matchere `Agent|Task`-kal bővült; a saját settings.json-t használó projektekben ezt kézzel kell átvezetni (az `install.sh --update` diffje mutatja) (döntött: agent, 2026-11-22).
- 3. szakasz: a lint csak a helyi `shellcheck`-et használja (a pre-commit gyors marad); a Dockeres tartalék az `sdd handover`-ben van, és ha a Docker nem tud elindulni, az csak megjegyzés, nem hiba (döntött: agent, 2026-11-22).
- 3. szakasz: az átvilágítás „sdd parancs és az őr bővítései” listájából a terv 3. szakaszán kívül maradt a SubagentStop hook, a `commit-msg` hook és a `lint_validate_kept`; a zárolt fájlok emlékeztetője a státusz helyett az `sdd handover` kimenetébe került (döntött: agent, 2026-11-22).
- 3. szakasz, ellenőrzés: 155 teszt zöld (az őr 57, a lint 21, az `sdd` 13, a többi a korábbi szakaszoké); az új őrtiltások tesztjei a javítás előtt buktak; végpontig tartó próba egy friss telepítésen (`preflight`, `new`, `handover`, spec-commit a lint megállításával, `#spec-ok`, a tiltások, `sdd commit`, `--final` lint, `sdd archive`, branchváltás az archiválás után) (döntött: agent, 2026-11-22).
- 4. szakasz: a szótár, a döntésnapló és a kódolási szabályok formátuma a `specs/README.md`-be került (a projekt `docs/` mappájának nem zárolt fájljai, az első bejegyzéssel jönnek létre); a `CLAUDE.md` egy sorban mutat rájuk; a kódbeli név angol, a felület és a doksi magyar szót használ, ahogy a globális nyelvi szabály is mondja (döntött: agent, 2026-11-22).
- 4. szakasz: a döntésnapló helye a pii-pajzsban bevált `docs/decisions/NNNN-<slug>.md` (Matt `docs/adr/` helyett), Matt három feltételével; a formátum a pii-pajzs állapot- és dátumsorát tartja meg (döntött: agent, 2026-11-22).
- 4. szakasz: a kockázati mezők (`ajtó`, `hatósugár`) M és L fokozatnál kötelezők, a lint ellenőrzi; L-nél a `requirements.md` kapott „Kockázat és visszaút” szakaszt; a mély review egyirányú vagy nagy esetén alapból fut, kétirányú és kicsi esetén elmarad, a kézi ellenőrzések listája ugyanígy méreteződik (döntött: agent, 2026-11-22).
- 4. szakasz: az `architecture-review` globális skill a sablon repójában él (`claude-skill/architecture-review/`, mint az `sdd-init`), így verziókövetett; a `~/.claude/skills/` alá másolással települ; Matt két skilljének (MIT) átdolgozása, a licenc és a forrás-commit a mappában (döntött: agent, 2026-11-22).
- 4. szakasz: a riport HTML marad Tailwind és Mermaid CDN-nel (rögzített verzió, mindkettő 200-at adott), mert az előtte–utána ábra a skill fő értéke; az ábrákhoz hálózat kell (döntött: agent, 2026-11-22).
- 4. szakasz: a globális `grill` „Terms” szakaszában a szótártiltás helyére lusta bővítés került (SDD-projektben `docs/szotar.md`, egyébként a projekt saját szótára, vagy egyszeri ajánlat), és a döntésnapló csak a három feltétellel ajánlható; a régi szöveg mentése a session scratchpadjében volt, a `grill` nincs verziókövetve (döntött: agent, 2026-11-22).
- 4. szakasz, csak olvasó próba a pii-pajzson (a `git status` előtte és utána azonos) (döntött: agent, 2026-11-22):
  - szótár-kivonat: 15 fogalom, 16 eltérés fájl:sor bizonyítékkal; a 13 formátumjegyzet alapján a szótár formátuma kapott „Nyitott” sort, a szót az owner választja, a „Kódban” sor a fő azonosító (vagy „még nincs”, vagy „ma: …”), a meglévő fogalomtár átkerül, listás alak; az élettartam és az állapot szándékosan kimaradt (spec-ügy) (`fb79172`).
  - kódszerkezet-riport az `engine/`-en: 5 jelölt (2 Erős), 2 valószínű hiba kódolvasásból, nem futtatva; a 14 skilljegyzetből 13 alapján javítva a hatókör, a hiányzó szótár, a valószínű hibák külön szakasza, a függőségi kategóriák, a sorrend, a fő ajánlás elve, a feltételes megnyitás és a hiányzó magyar szavak (`d667800`); az `api/` mappanév ütközése nem hiba.

