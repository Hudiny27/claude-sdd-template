---
szint: L
allapot: tervezet
---
# Terv: kötegelt üzemmód

Állapot: nyitott: a terv kész, az építésről az owner dönt.

Cél: az owner napi részvétele három rövid ablakba sűrűsödjön. Aktív ablak:
több feature kikérdezése és specje, egy köteg-jóváhagyás. Építő ablak:
felügyelet nélkül (éjjel) építés és validálás merge-kész állapotig. Döntési
ablak: reggel egy döntés feature-enként a mergéről. Az állomások (spec,
jóváhagyás, kapuk, review, merge-döntés) a mostani SDD-é maradnak; a mostani,
egyenkénti folyamat változatlanul megmarad mellette.

## Napi ritmus

1. **Aktív ablak** (az owner jelen van, kb. 1–2 óra): köteg-fájl, közös
   kikérdező kör, feature-enként `grill` és spec a saját worktree-jében,
   időbecslés, `#spec-ok köteg <név>`, az éjszakai megbízás (benne: kér-e
   artifact jelentést), majd `#éjszaka`.
2. **Építő ablak** (felügyelet nélkül): feature-enként `execute-plan`,
   egyszerre legfeljebb kettő, a függők egymásra épülve; minden feature
   merge-kész állapotig (lásd Döntések), éjjel se merge, se push.
3. **Döntési ablak** (reggel, kb. 15–30 perc): jelentés feature-enként
   (zöld, sárga, piros, bizonyíték, éjjeli agent-döntések felülbírálásra, a
   kézi ellenőrzések), majd egy többválasztós ablak: merge, javítás (a
   következő köteg elejére), elvetés. A merge és a push a kattintás után.

## 1. szakasz: köteg-fájl és őr

1. Köteg-fájl formátum a `Plans/README.md`-ben: `Plans/kotegek/ÉÉÉÉ-HH-NN-<név>.md`
   (feature-ök, branch, spec-mappa, sorrend, függés, időbecslés, időkeret,
   artifact-kérés, állapot feature-enként).
2. `sdd batch new <név>`, `sdd batch add <branch> --level S|M|L` (branch és
   spec-mappa egy `.claude/worktrees/<slug>` worktree-ben, a `main`-ről vagy
   a függés branchéről), `sdd batch status`.
3. Őr: a `#spec-ok köteg <név>` a köteg-fájlban felsorolt minden branchet
   jóváhagy, a specet a saját worktree-jében keresve; a fokozat-emelkedés
   szabálya feature-enként él. A worktree a projektmappán kívül nem
   használható a kötegben.
4. Lint: a köteg-fájl formátuma; auth- vagy biztonsági feature (a spec
   kockázati területei szerint) nem lehet a kötegben.

Ellenőrzés: az őr regressziós tesztjei (jóváhagyás kötegre, worktree-ben,
fokozat-emelkedés egy köteg-tagban), a lint és az `sdd batch` tesztjei.

## 2. szakasz: az aktív ablak (`/batch` skill)

1. A közös kör: sorrend, függések, közös fájlok, közös fogalmak, időbecslés.
2. Feature-enként a `feature-spec` lépései, a teljes `grill`-lel.
3. A jóváhagyás előtt a futásidő-becslés és a kimaradók kérdése; utána az
   `overnight` megbízása a köteg egészére (artifact: igen vagy nem).

## 3. szakasz: az építő ablak

1. Köteg-napló a repón kívül (`~/.claude/execute/<projekt>/köteg-<név>/`),
   amelyből egy megszakadt futás folytatható.
2. Feature-enként az `execute-plan`, egyszerre legfeljebb kettő; a
   `validate-feature` ablakok nélküli, merge-kész módja (archiválással,
   merge nélkül).
3. Parkolás: fokozat-emelkedés, a specen túli döntés, 3 sikertelen javítási
   kör, őr-elutasítás; csak az érintett feature és a ráépülők állnak meg.

## 4. szakasz: a döntési ablak

1. `sdd batch report`: a jelentés váza a köteg-fájlból és a naplókból.
2. A reggeli jelentés (chat, `jelentes.md`, opcionálisan artifact), majd a
   merge-ablak; a függő párok együtt mergelhetők.
3. A javítás kérése a spec „Döntések” szakaszába, a feature a következő
   köteg első tétele; az el nem döntött feature branche vár.

Ellenőrzés: egy próba-köteg egy mintaprojekten (két független feature és
egy függő pár) egy felügyelet nélküli futással; az owner értékeli a
jelentést és a merge-ablakot.

Kockázat: egy rossz éjszaka több feature-t visz rossz irányba. Ellenszer:
alapos aktív ablak, a parkolási szabályok, a reggeli felülbírálás, és hogy
éjjel semmi nem kerül a `main`-be. Visszaút: a köteg csak brancheket hoz
létre; az egyenkénti folyamat változatlan.

## Tények (kritikus kör, 2026-11-22)

- Az építő ablak nagy része megvan: az `overnight` skill (megbízás,
  döntésnapló, reggeli jelentés, éjjel tiltott merge) és az `execute-plan`
  (feladatonként friss subagent, folytatható napló a repón kívül).
- A `#spec-ok` csak a session aktuális branchét hagyja jóvá
  (`sdd_guard.py`, `approve`); a jóváhagyás-flag a projekt `.claude/`
  mappájában, branchnév szerint él.
- Az őr csak a projektmappán belüli worktree-ket látja (`locate`); egy
  testvérmappában futó építést nem gátol. A köteg worktree-i ezért a
  `.claude/worktrees/` alatt legyenek (a sablon `gitignore`-ja már ignorálja).
- A `suite_lock` a közös git-mappában zárol, így a teljes tesztkörök a
  worktree-k között is sorban futnak; a `.claude/check.sh` nem zárol.
- A sablon `CLAUDE.md`-je: biztonsági és auth feature-nél minden csoport után
  megállás, előre nem engedélyezhető.

## Döntések

- Éjjel a független feature-ök egyszerre épülnek, egyszerre legfeljebb kettő; a közös fájlt érintők sorban (döntött: owner, 2026-11-22).
- Ha B az A-ra épül, B az A branchére épül ugyanabban az éjjelben; reggel együtt mergelhetők, A elvetésekor B újraépítendő, ezt a jelentés jelzi (döntött: owner, 2026-11-22).
- Biztonsági és auth feature nem kerülhet kötegbe; nappal, a mostani módon megy (döntött: owner, 2026-11-22).
- A köteget egy kulcsszó hagyja jóvá: `#spec-ok köteg <név>` sor elején; az őr a köteg minden specét jóváhagyja (döntött: owner, 2026-11-22).
- Eltörő subagent nem fut a kikérdezésben: a változás a munkafolyamatot érinti, nem adatot, és visszavonható (döntött: agent, 2026-11-22).
- Az aktív ablak egy közös körrel kezd az egész kötegre (sorrend, függések, közös fájlok, közös fogalmak), utána minden feature a teljes `grill`-t kapja (döntött: owner, 2026-11-22).
- A kötegnek nincs fix mérete: az agent a specek alapján megbecsli a futásidőt, és a jóváhagyás előtt szól, ha nem fér bele az éjszakába; a kimaradókról az owner dönt (döntött: owner, 2026-11-22).
- Ha reggel egy feature javítást kér, a kérés a specje „Döntések” szakaszába kerül, és a feature a következő köteg első tétele lesz (döntött: owner, 2026-11-22).
- A reggeli jelentés a chatben és a `jelentes.md`-ben jön (ahogy az `overnight` skillben); egy artifact oldal opcionális: a köteg indításakor az agent megkérdezi, kér-e az owner a végén artifactot (döntött: owner, 2026-11-22).
- Egy feature elakadása (fokozat-emelkedés, a specen túli döntés, 3 sikertelen javítási kör) csak azt és a ráépülőket parkolja, a többi folytatódik (döntött: agent, 2026-11-22).
- Éjjel nincs push, a feature branchek sem mennek fel; a merge és a push reggel, az owner kattintása után (döntött: agent, 2026-11-22).
- A párhuzamos worktree-k a `.claude/worktrees/` alatt vannak, mert az őr csak a projektmappán belül gátol (döntött: agent, 2026-11-22).
- Az építés az `overnight` és az `execute-plan` skillre épül; új a `/batch` skill (aktív és döntési ablak) és az `sdd batch` parancsok (döntött: agent, 2026-11-22).
- A köteg-fájl helye `Plans/kotegek/ÉÉÉÉ-HH-NN-<név>.md`; a kulcsszó az ott felsorolt brancheket hagyja jóvá (döntött: agent, 2026-11-22).
- Merge-kész: minden gépi ellenőrzés zöld, a `--final` lint tiszta, a review a kockázat szerint lefutott és a valós találatok javítva, a spec archiválva, a branch egy mergére a `main`-től; a kézi ellenőrzések listázva (döntött: agent, 2026-11-22).
- Éjjel a spec „Döntések” szakasza új agent-döntéssel bővülhet (reggel felülbírálható); a fokozat vagy a hatókör növekedése parkolás (döntött: agent, 2026-11-22).
- A reggel el nem döntött feature branche vár, a következő köteg nem nyúl hozzá, és a jelentés újra elé teszi (döntött: agent, 2026-11-22).
- Az owner a 8 agent-döntést a felülbíráló ablakban változtatás nélkül elfogadta (döntött: owner, 2026-11-22).
- 1. szakasz: a köteg-fájl sablonja a `Plans/README.md` „köteg.md” szakaszában él, onnan másolja az `sdd batch new`, ahogy az `sdd new` a spec-sablonokat; a sablonkereső ezért a címsor és a kódblokk közti szöveget is átugorja (döntött: agent, 2026-11-22).
- 1. szakasz: az `sdd batch add` a „Becslés” és az „Auth/biztonság” oszlopba `?`-et ír; a lint és az őr csak a kitöltött becslést és a kimondott `nem`-et fogadja el, így az auth-kizárás nyilatkozat, nem csendes alapérték (döntött: agent, 2026-11-22).
- 1. szakasz: az őr a köteg minden soránál ellenőrzi, hogy a worktree a projekten belül van, abban a branch van kivéve, és van spec; a hibás sort indoklással kihagyja, a többit jóváhagyja; a jóváhagyás-flag a köteg-fájlra is hivatkozik (döntött: agent, 2026-11-22).
- 1. szakasz: a `batch` és a `köteg.md` sablon a `main` checkoutban dolgozik (`sdd batch` csak `main`-en fut), a feature-ök a saját worktree-jükben (döntött: agent, 2026-11-22).
- 1. szakasz, ellenőrzés: 170 teszt zöld (őr 62, lint 27, `sdd` 17, a többi a könyvtárak és a telepítő tesztjei); az őr öt köteg-tesztje a javítás előtt bukott; végpontig tartó próba egy friss telepítésen (köteg, két feature egy függéssel, lint-megállítás `?`-nél, `#spec-ok köteg`, kód és commit a worktree-ben, `sdd batch status`) (döntött: agent, 2026-11-22).
- 2. szakaszra vár: a worktree-kben a specet a jóváhagyás előtt commitolni kell (a próbában commitolatlan spec mellett ment át a jóváhagyás); a `/batch` skill aktív ablaka ezt teszi meg (döntött: agent, 2026-11-22).
- 2. szakasz: a `/batch` skill a sablon skilljei közé került (`files/.claude/skills/batch/`, segédfájlok: `active.md`, `night.md`, `morning.md`), mert az `sdd batch`-re és az őr köteg-jóváhagyására épül; az éjszakai és a reggeli ablak ma az `overnight` és az `execute-plan` skillre támaszkodik, a 3. és a 4. szakasz ezeket finomítja (döntött: agent, 2026-11-22).
- 2. szakasz, friss subagent-próba (az aktív ablak egy háromfázisú mintaprojekten, valódi parancsokkal; 10 felugró ablak, 15 kérdés) (döntött: agent, 2026-11-22):
  - 7 jegyzet, mind javítva: S fokozatnál nincs interjú a kötegben sem; a `feature-spec` záró `#spec-ok` és `/clear` lépése kötegben elmarad; a közös fájlt érintő feature-ök egymásra épülnek (`--after`), így reggel nincs merge-ütközés; a közös szótár és döntésnapló a köteg-fájllal együtt a feature-ök előtt a `main`-re kerül, így minden worktree látja; az őr csak commitolt specet hagy jóvá (`fix(guard)`); az `sdd --help` a teljes súgót írja ki, a használati hiba 2-vel lép ki.
  - a javítás közben a saját lintünk a sorok nélküli köteg-fájlt hibának vette, ami az új sorrendet megakasztotta volna; javítva, teszttel.
- 2. szakasz, ellenőrzés: 174 teszt zöld; a módosításokra még nem futott második próbakör (döntött: agent, 2026-11-22).
- 2. szakasz, második próbakör (új mintaprojekt, ugyanaz a feladat; 9 ablak, 15 kérdés; 2 lényeges és 15 apró jegyzet) (döntött: agent, 2026-11-23):
  - lényeges, javítva mechanizmussal: a worktree-kben a köteg-fájl régi pillanatkép; az őr mostantól a `Plans/kotegek/` alatti írást csak a fő checkoutban engedi (teszttel).
  - lényeges, javítva: a közös fájl miatti `--after` mindent egy láncba kötött; a `Függ` oszlop csak valódi függés (kód vagy adat), a közös fájlt érintő pár „nem egyszerre” jelölést kap a közös döntések között, mindkettő a `main`-ről épül, és éjjel az agent kipróbálja, hogy egymás után mergelhetők-e; csak valódi ütközésnél mergeli a korábbit a későbbibe, és ezt a `Függ` cellába írja.
  - apró, javítva: `sdd batch status` név nélkül a legújabb köteget mutatja; a jelöltek között a roadmap fázisai; a becslés formátuma (`1,5 óra`); S specnél a feltevés egy hozzáadott „Döntések” szakaszba kerül; `validate.sh` csak ha van; a köteg-fájl éjjel commit nélkül változik, reggel commitolódik; a `jóváhagyva` állapotot az éjszakai ablak állítja be; a közös kör backlog-tétele a nyitó commitba kerül; a megbízás minden worktree-t felsorol.
  - apró, nem kell változtatás: a break-it subagent ismétlése M feature-nél, a `handover` kimenetének egy sora, a törlés fokozat-határesete és a próba saját „ajánlott válasz” szabálya.
- 2. szakasz: a második próbakör lényeges jegyzeteire nem futott harmadik kör; a javításokat tesztek őrzik, és a 3. szakasz éjszakai próbafutása ezeket is végigjárja (döntött: agent, 2026-11-23).
