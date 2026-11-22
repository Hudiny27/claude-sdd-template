# A sablon átvilágítása (2026-11-22)

Átvilágítottam a sablon hét szabályfájlját: `CLAUDE.md`, `Plans/README.md`, `specs/README.md` és a négy skill (`feature-spec`, `validate-feature`, `replan`, `constitution`), összesen 1127 sort. Minden fájlt szabályokra bontottam (egy utasítás vagy szorosan összetartozó mondatok), mindegyikhez egy kategóriát rendeltem, és a `git blame` alapján megkerestem, melyik commit hozta. Az őrt (`sdd_guard.py`) csak azért olvastam, hogy lássam, mit kényszerít ki már most. Összesen 231 szabály: 107 mag, 48 mechanizmus, 14 projektfüggő, 62 üres. A vágás után a mag becsült mérete kb. 600 sor a mostani 1127 helyett (CLAUDE.md kb. 120, `Plans/README.md` kb. 170, `specs/README.md` kb. 80, a skillek egyenként 45–90 sor); a mechanizmusok kb. 300 sor tesztelt kódba kerülnek.

Jelölések. Az `Eredet` oszlopban a dátum 2026-os. Az `alap` a kezdő sablon (`8536d02`, illetve a magyarra fordító `11576c6`, mindkettő 10-05). A `Hely` a fájl mostani sorszáma.

## CLAUDE.md (249 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| C1 | A spec a mit és miért, a kód a hogyan; a globális szabályokat egészíti ki; az elutasítás stoptábla | 3–7 | mag | Marad | alap |
| C2 | Nyelv: a projekt Markdownja magyar, a kód, commit és skill angol, azonosítók nem fordítandók | 9–15 | mag | Marad, de telepítési paraméterként (lásd Bizonytalan) | 11576c6, 10-05 |
| C3 | Elsőbbség: `specs/` > aktuális spec > chat; ne támaszkodj korábbi session emlékére | 19–21 | mag | Marad | alap |
| C4 | Könyvtárfa a fájlok szerepével | 23–37 | mag | Marad | alap, 35. sor 6c42c83 |
| C5 | Formátumok helye és a branch ↔ spec-mappa névszabály | 39–41 | mag | Marad, itt az egyetlen helye; a `fix/` ág is ide kerüljön | alap |
| C6 | A hat lépés táblázata | 45–52 | mag | Marad | alap, 48. sor 9a7a6e9 |
| C7 | Az őr minden session elején kiírja a státuszt; aszerint járj el | 54–56 | mag | Marad | alap |
| C8 | Kikényszerítési táblázat (zárolt fájlok, kód csak jóváhagyott specnél, flagfájlok, `--no-verify`) | 60–69 | mag | Marad, ez írja le a kapukat | alap |
| C9 | Kulcsszó csak az owner sor eleji szövegében számít; subagent promptba ne írj sor elejére kulcsszót, és ne kérj tőle feloldást | 71–73 | mechanizmus | PreToolUse hook az `Agent` eszközre: tiltja a `#spec-` kezdetű sort a promptban | alap |
| C10 | Ha az őr elutasít: állj meg, mondd el, javasold a pontos változtatást, ne kerüld meg | 74–77 | mag | Marad, ez az egyetlen helye | alap |
| C11 | A pre-commit hook és a CI ellenőrzés leírása | 78–83 | mag | Marad, két sorra rövidítve | alap |
| C12 | Ismert rések részletei (önmagukat író programok, változó-behelyettesítés) | 84–88 | üres | Az őr belső működése, a `sdd_guard.py` docstringje már leírja | alap, 5fdedee 10-10 |
| C13 | Viselkedj úgy, mintha nem lennének rések | 89 | mag | Marad egy mondatként a C10 mellett | 5fdedee, 10-10 |
| C14 | Constitution: előbb interjú, brownfieldnél előbb levezetés, kis fázisok | 93–97 | üres | Duplikátum: `constitution/SKILL.md` 1–2. lépés | alap |
| C15 | Feature spec előfeltétele: tiszta állapot, előző branch mergelve, `main`, `/clear` | 99–101 | üres | Duplikátum: `feature-spec/SKILL.md` 22–27 (ott mechanizmus lesz) | alap |
| C16 | Fokozatok S/M/L, kockázatos terület legalább M, ha a fokozat nő, új `#spec-ok` | 101–106 | mag | Marad, ez az egyetlen helye; a többi előfordulás törlődik | 9a7a6e9, a4a777b 10-20 |
| C17 | S és M egy `spec.md`, L három fájl; S-nél nincs interjú, M/L-nél `grill` | 106–109 | üres | Duplikátum: `feature-spec/SKILL.md` 66–69, 113–115 | 9a7a6e9, 10-20 |
| C18 | A `validation.md` futtatható parancsokat és kézi ellenőrzést tartalmaz | 109–110 | üres | Duplikátum: `Plans/README.md` validation.md sablon | alap |
| C19 | LLM-nek szóló dokumentumhoz friss subagent-próba, legfeljebb 3 kör | 110–116 | üres | Duplikátum: `Plans/README.md` 232–290 | 4aa4298 10-09, f98324a 11-01 |
| C20 | Fizetős API-nál költségbecslés a `validation.md`-ben | 116–118 | üres | Duplikátum: `Plans/README.md` „Költség” szakaszai | ece3f7a, 10-09 |
| C21 | Valódi adattól függő számok „kalibrálandó” jelölést kapnak | 118–120 | üres | Duplikátum: `Plans/README.md` 130–133 | ece3f7a, 10-09 |
| C22 | A spec lépésben nincs kód | 120 | üres | Az őr kényszeríti ki | alap |
| C23 | Implementáció csak `#spec-ok` után, `plan.md` szerint, csoportonként | 122–123 | mag | Marad | alap |
| C24 | Biztonság, auth, adat, migráció: egy csoport, utána megállás; adatnál előre engedélyezhető | 123–126 | mag | Marad | alap, 5fdedee 10-10 |
| C25 | Ne menj túl a requirementsen; ha kétértelmű, kérdezz; ne dönts csendben | 126–127 | mag | Marad | alap |
| C26 | A kalibrálandó értéket a bevezető csoportban kell mérni | 127–129 | üres | Duplikátum: `Plans/README.md` 130–133 | ece3f7a, 10-09 |
| C27 | A következő csoport kódja csak az előző commitja után; minden commit egy csoport | 129–132 | mag | Marad | 160bc94, 10-13 |
| C28 | Amíg a tesztkör a háttérben fut, csak olvass és tervezz | 130–131 | projektfüggő | pii-pajzs szabályai (hosszú tesztkör) | 160bc94, 10-13 |
| C29 | A „javítás előtt bukik” próba csak az új tesztet futtatja, időkorláttal | 132–133 | mechanizmus | `prove_red` lib-függvény: régi kódon, ideiglenes munkafában, csak az új teszt, timeouttal | f98324a, 11-01 |
| C30 | Látható vagy hallható kimenetnél az owner élő mintát néz a bevezető csoportban; a próba utána fut | 134–138 | mag | Marad, a „hangszint” példa nélkül | 3394427, 10-22 |
| C31 | Validáció: minden ellenőrzés lefut, eredmény bizonyítékkal | 140–141 | üres | Duplikátum: `validate-feature/SKILL.md` 2. lépés és a globális „Evidence before claims” | alap |
| C32 | Fizetős API: tényleges felhasználás a becsléshez képest | 141–142 | üres | Duplikátum: `validate-feature/SKILL.md` 77–78 | ece3f7a, 10-09 |
| C33 | A `validate.sh` és a teljes tesztkör alatt nem fut párhuzamosan nehéz build, élő teszt, próba | 142–144 | mechanizmus | `suite_lock` (flock) a lib-ben: a tesztkör, az élő teszt és a próba ugyanazt a zárat kéri | 3394427, 10-22 |
| C34 | A review szintje: működik-e és megfelel-e a specnek; nem triviálisnál mély review | 144–146 | mag | A szint marad; a mély review ajánlása duplikátum (`validate-feature` 4.) | alap |
| C35 | A kész definíciója (ellenőrzések, szinkron, roadmap, `Plans/done/`) | 146–148 | mag | Marad | alap, a4a777b |
| C36 | Merge nyitott kézi ellenőrzéssel, ha az owner kéri; döntés rögzítve, `/replan` visszakérdez | 148–151 | üres | Duplikátum: `validate-feature/SKILL.md` 92–95 | 5fdedee, 10-10 |
| C37 | Újratervezés `replanning/` branchen; kis kódjavításhoz S spec; nagyobb munka új fázis | 153–156 | üres | Duplikátum: `replan/SKILL.md` 177–182; a spec kötelezőségét az őr kényszeríti | alap, 9a7a6e9 |
| C38 | Feature közbeni ötlet a `specs/backlog/` alá, nem a branchre; subagent promptba is | 156–158 | mag | Marad | alap, f98324a |
| C39 | Egy munkafában egy branch; másik branch külön worktree-ben; futó feature alatt nincs branchváltás | 160–165 | mechanizmus | Őr: tiltja a `git switch`/`checkout` másik branchre, ha jóváhagyott feature fut, és `git worktree add`-ot javasol | 5fdedee, 10-10 |
| C40 | Prototípus: scratchpadben, repón kívül, saját környezettel, kódja nem kerül át | 167–173 | mag | Marad, rövidítve | e660e1a, 10-06 |
| C41 | Prototípus scriptjei `specs/backlog/prototype/` alá menthetők, a lint alól kivéve | 173–175 | projektfüggő | pii-pajzs (ruff kivétel) | a41ce0d, 10-07 |
| C42 | A prototípus tanulságai ugyanabban a sessionben a backlogba, `replanning/` branchen | 177–179 | mag | Marad | e660e1a, 10-06 |
| C43 | Minden viselkedés- vagy döntésváltozás ugyanabban a változtatásban frissíti a specet | 183–185 | mag | Marad (a CI ellenőrzés részben kikényszeríti) | alap |
| C44 | Review-döntések a „Döntések” alá dátummal, indokkal, döntéshozóval; a kihagyás nem kudarc | 186–189 | mag | Marad elvként; a formátumot a `lint_decisions` ellenőrzi | e3146b8, 10-05 |
| C45 | Specmódosítás az agenten át, hogy a fájlok konzisztensek maradjanak | 190–191 | mag | Marad | alap |
| C46 | Átnevezés után minden említés frissül a specekben és a doksiban | 192–193 | mechanizmus | `lint_dangling_paths`: a backtickes útvonalak létezését ellenőrzi | alap |
| C47 | A specek részletessége (mi kerül bele, mi marad ki) | 197–200 | üres | Duplikátum: `Plans/README.md` 319–324 | alap |
| C48 | Owner döntés felugró ablakban; ide tartozik commit, push, merge, takarítás, következő lépés | 204–208 | üres | Duplikátum: globális „Questions and decisions” (lásd Bizonytalan) | 8961fae, 10-22 |
| C49 | Az ablak előtt a chatben ott az eredmény, bizonyíték, feltételezés, kockázat | 210–212 | mag | Marad | 8961fae, 10-22 |
| C50 | A javasolt opció első, „(Javasolt)”, egyszerű leírással | 213–214 | üres | Duplikátum: globális „Questions and decisions” | 8961fae, 10-22 |
| C51 | Független döntések egy ablakban; a záró teendők `multiSelect`-ben; csak a bejelöltek, sorrendben | 215–220 | mag | Marad, mert minden skill zárása erre épül | 8961fae, 10-22 |
| C52 | A „Más” mezőbe írt válasz utasítás | 221–222 | üres | Egy képes modell alapból így kezeli | 8961fae, 10-22 |
| C53 | A kulcsszó nem kattintható; a chat végén megmondja, mit kell begépelni | 224–227 | mag | Marad, ez az egyetlen helye | 8961fae, 10-22 |
| C54 | Amit az agent eldönthet vagy kinézhet, arról nem kérdez | 228–229 | üres | Duplikátum: globális „Questions and decisions” | 8961fae, 10-22 |
| C55 | Overnight módban nincs ablak | 230 | üres | Duplikátum: globális „Overnight mode” és az `overnight` skill | 8961fae, 10-22 |
| C56 | A globális „terv előbb” szabályt a `plan.md` és a `#spec-ok` teljesíti | 234–235 | mag | Marad | alap |
| C57 | Kivétel a globális „egy kérdés” szabály alól | 236–237 | üres | Elavult: a globális szabály már a kérdések csoportosítását kéri | alap |
| C58 | A globális „angol dokumentáció” helyett a Nyelv szakasz érvényes | 238–239 | üres | Duplikátum: C2 (a Nyelv szakaszba olvad) | 11576c6, 10-05 |
| C59 | Globális git-szabályok érvényesek; commit csak jóváhagyással | 240–241 | üres | Duplikátum: globális „Ask first” és „Git” | alap |
| C60 | A `#spec-ok` jóváhagyja a csoportonkénti commitot zöld teszt, lint, típus után; S/M egy commit | 241–246 | mag | Marad | ece3f7a 10-09, a4a777b |
| C61 | Az ellenőrzés és a commit `&&`-vel kapcsolódik, soha `;`-vel | 246–247 | mechanizmus | `sdd commit` wrapper: lefuttatja a projekt ellenőrző parancsát, és csak zöldnél commitol | 84ddad1, 11-20 |
| C62 | Soha ne pusholj és ne mergelj kérdezés nélkül | 247 | üres | Duplikátum: globális „Ask first” és a `safety_guard.py` | 84ddad1, 11-20 |
| C63 | Commit scope-ok: `docs(specs)`, `docs(plans)` | 248–249 | mechanizmus | `commit-msg` hook: csak `specs/` vagy csak `Plans/` változásnál ellenőrzi a scope-ot | alap |

## Plans/README.md (324 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| P1 | Minden fázis és kódot érintő újratervezés kód előtt specet kap | 3–4 | üres | Az őr kényszeríti; C6 is mondja | alap |
| P2 | A `Plans/` fája (L: négy fájl, S/M: `spec.md`, `done/`) | 6–16 | mag | Marad | alap, e660e1a, 9a7a6e9 |
| P3 | Fokozatok leírása és a jóváhagyás | 18–20, 22–23 | üres | Duplikátum: C16 | 9a7a6e9, 10-20 |
| P4 | M mellé is jöhet `validate.sh`, ha sok a gépi ellenőrzés | 20–22 | mag | Marad egy félmondatként | 84ddad1, 11-20 |
| P5 | Branch ↔ könyvtár névszabály, ezen talál rá az őr | 25–27 | üres | Duplikátum: C5; az őr kényszeríti | alap |
| P6 | Életciklus 1–3. és 5. lépése | 31–36, 44–45 | üres | Duplikátum: C6 | alap, e660e1a |
| P7 | Párhuzamos subagentek csak a saját fájljukat commitolják név szerint, soha `git add -A`/`.` | 37–40 | mechanizmus | Őr: tiltja a `git add -A`, `git add .`, `git commit -a` parancsot | f98324a, 11-01 |
| P8 | Az élő minta átadása felsorolja az agent saját, látható viselkedést érintő döntéseit | 41–43 | mag | A C30 mellé olvad | bb75f8e, 11-21 |
| P9 | `spec.md` sablon (frontmatter `szint:`, szakaszok) | 49–82 | mag | Marad; a kötelező szakaszokat a `lint_spec` ellenőrzi | 9a7a6e9, a4a777b |
| P10 | S-nél elég a Cél, Kész, ha, Ellenőrzés | 84–85 | mag | Marad; `lint_spec` szintenként ellenőrzi | 9a7a6e9, 10-20 |
| P11 | Ha a munka nő, bővül a spec és új `#spec-ok` kell | 85–87 | üres | Duplikátum: C16; az őr kényszeríti (`level_rose`) | a4a777b, 10-20 |
| P12 | Roadmapen kívüli S javítás branchneve `fix/<slug>` | 87–88 | mag | A C5 névszabályba olvad | a4a777b, 10-20 |
| P13 | `plan.md` sablon | 92–107 | mag | Marad | alap |
| P14 | `requirements.md` sablon | 111–128 | mag | Marad | alap, 5707b15 |
| P15 | Kalibrálandó jelölés, mérés a bevezető csoportban az élő mintákon | 130–133 | mechanizmus | `lint_calibrations`: minden „kalibrálandó” döntéshez kell Kalibrálás alszakasz, mielőtt a csoport commitol; az elv egy mondatban marad | ece3f7a 10-09, 3ae47d4 |
| P16 | Ha a mért érték constitution-beli számot változtat, a constitution ugyanabban a csoportban frissül | 133–135 | projektfüggő | pii-pajzs szabályai | bb75f8e, 11-21 |
| P17 | Kalibrálás alszakasz formátuma (Minta, Söprés, Választás, Ellenőrzés) | 135–146 | mechanizmus | `lint_calibrations` ellenőrzi a négy mezőt; a minta a sablonfájlba kerül | 5707b15, 10-20 |
| P18 | Döntéshozó: `owner` és `agent` jelentése; soronként egy döntéshozó | 148–153 | mag | Az elv marad; a sorformátumot a `lint_decisions` ellenőrzi | e3146b8, 10-05 |
| P19 | A felváltott döntés `(felváltva …)` jelölést kap, nem törlődik | 153–155 | mechanizmus | `lint_decisions`: a `main`-hez képest törölt Döntések-sor hiba, ha nincs felváltva-jelölés | bb75f8e, 11-21 |
| P20 | `validation.md` sablon | 159–175 | mag | Marad | alap, ece3f7a |
| P21 | A `validate.sh` a speccel készül, a spec-mappában él, nem kell hozzá `#spec-ok` | 179–181 | mag | Marad | e660e1a, 10-06 |
| P22 | A repó gyökeréből fut | 183 | mechanizmus | `sdd_init` a gyökérbe lép (`git rev-parse --show-toplevel`) | e660e1a, 10-06 |
| P23 | Ellenőrzésenként egy `PASS`/`FAIL` sor bizonyítékkal; bármely hiba nem nulla kilépés | 184–186 | mechanizmus | `check` és `sdd_finish` lib-függvény | e660e1a, 10-06 |
| P24 | A „nincs X” állítás csak akkor bizonyít, ha egyszer valódi X-en elbukott | 187–189 | mechanizmus | `assert_absent`: kötelező pozitív mintán előbb egyezést vár | 08dce78, 10-29 |
| P25 | A tiltva/hibaállapot teszt az okot is ellenőrzi; a hibát nem újrapróbált válasszal váltja ki | 190–193 | projektfüggő | A webes felületű projekt tesztszabályai (vagy a `verify-web` skill) | 84ddad1, 11-20 |
| P26 | A „soha” állítás a művelet után azonnal mér, újrapróbálás nélkül, aztán a végállapotot | 194–197 | projektfüggő | A webes felületű projekt tesztszabályai (Playwright auto-wait csapda) | 84ddad1, 11-20 |
| P27 | Elbukott tesztkörnél a bizonyíték megnevezi a teszteket (pytest `-rf`); egy futásban bukó teszt instabil | 198–201 | mechanizmus | `run_suite`: a bukott tesztek nevét kigyűjti, kétszer fut, a két futás eltérését instabilnak jelöli; a pytest kapcsoló a projekt beállítása | e501850, 10-20 |
| P28 | Saját ideiglenes könyvtár, a végén törölve | 202–203 | mechanizmus | `sdd_init` `mktemp -d` és `trap` | e660e1a, 10-06 |
| P29 | A háttérfolyamatokat a végén leállítja, hibánál is; fő shellben indít, nem `$(...)`-ben | 204–208 | mechanizmus | `start_bg`: PID-et regisztrál, az EXIT trap leállítja | 3ae47d4, 10-24 |
| P30 | Az indított szerver szabad portot kap | 209–211 | mechanizmus | `free_port` lib-függvény | bb75f8e, 11-21 |
| P31 | Leállítás PID-del, soha `pkill -f` | 212–214 | mechanizmus | `start_bg`/`stop_all` lefedi; az őr tilthatja a `pkill -f`-et | bb75f8e, 11-21 |
| P32 | Élő, fizetős, hálózati ellenőrzés csak kapcsolóval | 215–216 | mechanizmus | `live_only`: kihagyja az ellenőrzést `--live` nélkül | e660e1a, 3ae47d4 |
| P33 | A saját mappáját `$(dirname "$0")`-val találja, nem írja be a `Plans/<dir>`-t | 217–218 | mechanizmus | `sdd_init` adja a mappát; `lint_spec_paths` tiltja a beírt útvonalat | a41ce0d, 10-07 |
| P34 | `main`-nel összevetésnél `git archive main` a repóból, és nem üres ellenőrzés | 219–222 | mechanizmus | `export_main` lib-függvény | f98324a, 11-01 |
| P35 | Helyi ignorált beállítások dokumentált fájlból; kulcs környezetből vagy kulcstárból | 223–225 | mechanizmus | `sdd_init --live` egy rögzített nevű helyi fájlt tölt be; a kulcstár neve projektfüggő | a4a777b, 10-20 |
| P36 | `--live` maga tölti a beállításokat és állítja az élő kapcsolót | 226–229 | mechanizmus | `sdd_init` kapcsolóelemzése | 5707b15, 10-20 |
| P37 | Nehéz lépések memóriakorláttal, ha a tech-stack előírja | 229–230 | projektfüggő | pii-pajzs (WSL memóriakorlát) | 5707b15, 10-20 |
| P38 | LLM-nek szóló dokumentumhoz friss subagent-próba, módonként, párhuzamosan | 234–237 | mag | Marad, ez az egyetlen helye | 4aa4298, 10-09 |
| P39 | Körönként és próbánként friss, teljes projektmásolat; a generált doksik újragenerálva | 239–244 | mechanizmus | `probe_copy` lib-függvény, a projekt `probe_regen` horgával | e501850, 5707b15 |
| P40 | Szándékos rontásra épülő próbánál a rontást előre le kell írni | 244–248 | projektfüggő | video-tutorial vagy pii-pajzs próbaszabályai | 5707b15, 3ae47d4 |
| P41 | Régi állapotú mintaprojektet egyszer naprakészre hozni egy alapmásolatban | 249–253 | mechanizmus | `probe_base`, a projekt `probe_upgrade` horgával | 3394427, 10-22 |
| P42 | Az előkészítést `prepare-probe.sh` végzi a spec-mappában | 254–259 | mechanizmus | A közös `sdd_probe.sh` váltja ki; a projekt csak a horgokat adja | 55b66ad, 10-22 |
| P43 | Ha csak a követett fájlok másolódnak, az új fájlokat a próba előtt `git add` | 259–262 | mechanizmus | `probe_copy` a `git ls-files -co --exclude-standard` listát másolja, így nincs kézi `git add` | 08dce78, 10-29 |
| P44 | A próba scratch-mappába ír a repón kívül; utána a `git status` tiszta | 263–265 | mechanizmus | `snapshot_status` és `assert_no_new_files`; SubagentStop hook | ad4252a, 11-06 |
| P45 | A próba feladata a mintaprojekt valódi tartalmából készül | 266–269 | mag | Marad, ez az egyetlen helye | 55b66ad, 10-22 |
| P46 | A `validation.md` megnevezi a próbakörnyezet korlátait, a sikerfeltétel ehhez igazodik | 270–273 | mag | Marad | f98324a, 11-01 |
| P47 | Értékelés: valódi és felállításból adódó hiány; lényeges és apró hiány mércéje | 274–282 | mag | Marad | 5707b15, c8344a4 10-27 |
| P48 | Ismétlés, amíg nincs új lényeges hiány, legfeljebb 3 kör, utána megállás | 283–287 | mag | Marad, ez az egyetlen helye | 5707b15, c8344a4, f98324a |
| P49 | A körök eredménye a Döntések alá, az ötletek a backlogba | 288–290 | mag | Marad | 5707b15, 10-20 |
| P50 | A próba promptváza | 292–317 | mag | Marad, de külön sablonfájlba (`Plans/probe-prompt.txt`) | 5707b15, bb75f8e |
| P51 | Részletesség: mi kerül a specbe, mi marad ki | 321–324 | mag | Marad, ez az egyetlen helye | alap |

## specs/README.md (83 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| S1 | A constitutiont az owner kezeli, az őr zárolja | 3–7 | üres | Az őr kényszeríti; C8 is mondja | alap |
| S2 | A négy elem táblázata (mit tartalmaz, mikor változik) | 9–14 | mag | Marad | alap |
| S3 | `mission.md` sablon | 16–35 | mag | Marad | alap |
| S4 | `tech-stack.md` sablon | 37–58 | mag | Marad | alap |
| S5 | A roadmap legfelső szintű checkbox sorai; az őr az első nyitottat olvassa; csak a pipálás szabad | 62–64 | mag | Marad, ez a formátum, amelyet az őr olvas | alap |
| S6 | Roadmap sablon, kis fázisokkal | 66–77 | mag | Marad | alap |
| S7 | Backlog: témánként egy fájl; csak újratervezéssel kerül a roadmapre | 81–83 | mag | Marad | alap |

## .claude/skills/feature-spec/SKILL.md (223 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| F1 | Ebben a skillben nincs éles kód; az őr blokkol | 17–18 | üres | Az őr kényszeríti | alap |
| F2 | Előfeltételek: tiszta munkafa, előző mergelve, friss `main`, constitution létezik | 20–25 | mechanizmus | `sdd new` előfeltétel-ellenőrzése (`check_clean_start`) | alap |
| F3 | `/clear` ajánlása, ha a session mással foglalkozott | 26–27 | mag | Marad | alap |
| F4 | Alapból az első nyitott fázis; S javítás fázis nélkül; nagyobb roadmapen kívüli munka `/replan`-on át | 31–34 | mag | Marad | alap, a4a777b |
| F5 | Branch- és spec-mappanév képzése | 35–38 | mechanizmus | `sdd new <branch>`: létrehozza a branchet, a dátumos mappát és a sablont `szint:` sorral | alap, a4a777b |
| F6 | Spec előtt csak olvasva ellenőrizni, hogy a cél nem teljesül-e már | 39–41 | mag | Marad (lásd Bizonytalan) | 08dce78, 10-29 |
| F7 | Fokozatok leírása, kockázatos területek | 45–53 | üres | Duplikátum: C16 és a `size-up` skill | 9a7a6e9, 10-20 |
| F8 | Ködös nagy ötlet még nem spec: előbb `wayfinder` | 53–54 | mag | Marad | 9a7a6e9, 10-20 |
| F9 | Ha a fokozat menet közben nő: megállás, nagyobb spec, új `#spec-ok` | 55–57 | üres | Duplikátum: C16; az őr kényszeríti | a4a777b, 10-20 |
| F10 | A fokozatot felugró ablakban javasolja; nyilvánvaló S egy sorban; `szint:` rögzítése | 59–62 | üres | Duplikátum: globális popup-szabály; a `szint:` sort az `sdd new` írja | 9a7a6e9, 10-20 |
| F11 | S-nél nincs interjú; M és L a `grill` skill-lel | 66–69 | mag | Marad, ez az egyetlen helye | 9a7a6e9, 10-20 |
| F12 | Olvasd a mission, tech-stack és korábbi specek fájljait; interjú lemezre írás előtt | 71–73 | mag | Marad | alap |
| F13 | Az interjú három csoportja (hatókör, döntések, kontextus/validáció) | 75–79 | mag | Marad | alap |
| F14 | A constitutionnel való ütközést jelezd, ne oldd fel csendben | 81 | mag | Marad | alap |
| F15 | Meglévő felület másolásakor előbb a viselkedését és állapotait írd le | 83–87 | projektfüggő | A felületet másoló projekt szabályai vagy egy UI skill | 84ddad1, 11-20 |
| F16 | A „ma nem létezik” hatókörsort előbb a kódban ellenőrizni | 89–91 | üres | Duplikátum: globális „Never ask me for a fact you can look up” | 84ddad1, 11-20 |
| F17 | Külső API/SDK: a telepített SDK szignatúrájának olvasása az interjú előtt | 93–97 | üres | Duplikátum: globális „Current docs” | 160bc94, 10-13 |
| F18 | Mért CI vagy felhőkvóta ellenőrzése az interjú előtt | 99–103 | projektfüggő | A GitHub Actionst használó projekt szabályai | 646d95b, 10-22 |
| F19 | `workflow_dispatch` csak a default branchen lévő fájllal indítható | 105–109 | projektfüggő | A GitHub Actionst használó projekt szabályai | 646d95b, 10-22 |
| F20 | Formátumok a `Plans/README.md`-ben; S/M egy `spec.md`, M-hez opcionális `validate.sh` | 113–115 | mag | Marad | 9a7a6e9, 10-20 |
| F21 | `plan.md`: kis, egyenként review-zható csoportok; az utolsó a validáció | 117–118 | mag | Marad | alap |
| F22 | `requirements.md` tartalma, döntések dátummal, döntéshozóval, soronként egy | 119–121 | üres | Duplikátum: `Plans/README.md` 111–128, 148–153 | e3146b8, ece3f7a |
| F23 | Kalibrálandó jelölés és mérés | 121–126 | üres | Duplikátum: `Plans/README.md` 130–146 | ece3f7a, 5707b15 |
| F24 | A spec által rögzített mért érték megnevezi a pontos bemenetet | 127–129 | projektfüggő | pii-pajzs (hash, cache-kulcs a `main`-en; lásd Bizonytalan) | bb75f8e, 11-21 |
| F25 | `validation.md` tartalma: gépi és kézi ellenőrzés, kész definíciója | 130–131 | üres | Duplikátum: `Plans/README.md` validation.md sablon | alap |
| F26 | Subagent-próba felvétele, feladat a mintából, `prepare-probe.sh`, körök | 131–146 | üres | Duplikátum: `Plans/README.md` 232–290; egy mutató marad | 4aa4298, 5707b15, 55b66ad, f98324a, c8344a4 |
| F27 | Fizetős API: élő és kézi ellenőrzés költsége | 146–147 | üres | Duplikátum: `Plans/README.md` „Költség” | ece3f7a, 10-09 |
| F28 | Időkorlátot mérő teszt bukás előtt néhányszor újramér | 147–150 | projektfüggő | pii-pajzs tesztsegédje (terhelt WSL/DGX gép; lásd Bizonytalan) | 1c76429, 10-11 |
| F29 | „Nem történik meg” ígéret OS-szintű nyomkövetéssel, egy megengedett eseménnyel | 150–156 | projektfüggő | pii-pajzs (adatvédelmi ígéret, strace) | 08dce78, 10-29 |
| F30 | Minden gépi `validation.md` pont megnevezi a `validate.sh` ellenőrzést, amely lefedi | 157–161 | mechanizmus | `lint_coverage`: a pontok azonosítója szerepel egy `check` hívásban | f98324a, 11-01 |
| F31 | Teszt nem nevezi meg a spec-mappát; segédscript a gyökeret a git-ből veszi, nem `parents[n]`-ből | 161–165 | mechanizmus | `lint_spec_paths` és `sdd_init` | f98324a, ad4252a |
| F32 | PASS/FAIL sor, kilépési kód, ideiglenes mappa | 165–166 | üres | Duplikátum: `Plans/README.md` 184–186, 202–203 | e660e1a, 10-06 |
| F33 | Háttérfolyamatok leállítása, nem `$(...)`-ben | 167–169 | üres | Duplikátum: `Plans/README.md` 204–208 | 3ae47d4, 10-24 |
| F34 | Bukott tesztek neve a bizonyítékban | 170–171 | üres | Duplikátum: `Plans/README.md` 198–201 | e501850, 10-20 |
| F35 | `main` exportja `git archive`-val, nem üres ellenőrzés | 172–175 | üres | Duplikátum: `Plans/README.md` 219–222 | f98324a, 11-01 |
| F36 | `--quick` kapcsoló: kihagyja a teljes kört az archiválás utáni újrafuttatáskor | 176–178 | mechanizmus | `full_once`: a teljes kör kimarad, ha ugyanarra a tree hashre már zöld volt | ad4252a, 11-06 |
| F37 | A `validate.sh` a spec része: olvasd, mielőtt módosítod, bővítsd, a változás a Döntések alá | 179–180 | üres | Duplikátum: `validate-feature/SKILL.md` 20–22 | 08dce78, 10-29 |
| F38 | Élő ellenőrzés kapcsolóval, `--live` tölti a beállítást, memóriakorlát | 181–184 | üres | Duplikátum: `Plans/README.md` 215–230 | 5707b15, 10-20 |
| F39 | `$(dirname "$0")`, nincs beírt `Plans/<dir>`; helyi beállítás dokumentált fájlból | 184–188 | üres | Duplikátum: `Plans/README.md` 217–225 | a41ce0d, 5707b15 |
| F40 | Átadás előtt `bash -n` és `shellcheck`, Dockeres tartalékkal | 188–192 | mechanizmus | `lint_shell` a pre-commit hookban a `Plans/**/*.sh` fájlokra; a Docker tartalék projektfüggő | 646d95b, 08dce78 |
| F41 | Az offline részt egyszer lefuttatni: a hiányzó kód miatti FAIL várt, de minden eszköz fogadja a kapcsolóit | 192–195 | mechanizmus | `sdd handover`: egyszer lefuttatja a `validate.sh`-t, és a kimenetet az átadásba teszi | 08dce78, 10-29 |
| F42 | A `--live` részt is egyszer lefuttatni, ha csak olvassa a telepített példányt | 195–196 | projektfüggő | pii-pajzs (DGX tesztpéldány; lásd Bizonytalan) | bb75f8e, 11-21 |
| F43 | Minden használt élő URL-t egyszer megnyitni (státusz, végső host) | 196–198 | mechanizmus | `check_url` és az `sdd handover`, amely kigyűjti az URL-eket | bb75f8e, 11-21 |
| F44 | Az új végpontot hívó ellenőrzés a bevezető csoportban egyszer lefut | 198–200 | üres | Duplikátum: C60 (a csoport csak zöld tesztekkel commitol) | 08dce78, 10-29 |
| F45 | Két kimenet összevetése csak a stabil részen (szám, állapot), nem fájlnév vagy időbélyeg | 200–202 | üres | Egy képes modell alapból így ír összevetést | 08dce78, 10-29 |
| F46 | Átadás: összefoglaló, feltételezések `agent` döntésként | 206–207 | mag | Marad | e3146b8, 10-05 |
| F47 | Ha a spec zárolt fájlt módosít, ezt az átadás megnevezi; a `#spec-szerkesztes` az implementáció elején kell | 208–210 | mechanizmus | Őr: `#spec-ok`-kor a specben zárolt útvonalat keres, és a státuszban emlékeztet | ad4252a, 11-06 |
| F48 | A review-módosításokat maga végzi, a fájlok konzisztensek maradnak | 211–212 | üres | Duplikátum: C45 | e660e1a, 10-06 |
| F49 | Commit-kérdés felugró ablakban a többi nyitott teendővel | 213–216 | üres | Duplikátum: C51 | 8961fae, 10-22 |
| F50 | A chat végén: a `#spec-ok` begépelendő, utána `/clear` és az implementáló prompt | 217–220 | mag | Marad, rövidítve | alap, 8961fae |
| F51 | Biztonságnál egy csoport; a `#spec-ok` csoportonkénti commitot is jóváhagy; push és merge az owneré | 220–223 | üres | Duplikátum: C24, C60, C62 | alap, ece3f7a |

## .claude/skills/validate-feature/SKILL.md (123 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| V1 | A branchhez tartozó spec megkeresése; S/M-nél a `spec.md` szakaszai helyettesítik a fájlokat | 10–14 | mag | Marad; a mappát az `sdd spec-path` adja (az őr `find_spec_dir`-je) | alap, 9a7a6e9 |
| V2 | Minden csoport vagy „Kész, ha” sor kész-e; a hiányzók listája | 15–16 | mag | Marad | 9a7a6e9, 10-20 |
| V3 | A jóváhagyott `validate.sh`-t olvasni, bővíteni, nem lecserélni; a változás a Döntések alá | 20–22 | mechanizmus | `lint_validate_kept`: a `#spec-ok` kori `check` azonosítók megvannak, vagy a Döntések említi őket | 08dce78, 10-29 |
| V4 | Minden gépi ellenőrzés lefut a `validate.sh`-val (`--live`-val is), a lefedetlen kézzel, és a script javul | 24–27 | mag | Marad | alap, a4a777b |
| V5 | Első futás előtt minden gépi pontot egy `validate.sh` ellenőrzéshez rendelni | 27–29 | üres | Duplikátum: F30 (`lint_coverage`) | f98324a, 11-01 |
| V6 | A subagent-próba futtatása, körök, mérce, rögzítés | 29–38 | üres | Duplikátum: `Plans/README.md` 232–290; egy mutató marad | 5707b15, f98324a, c8344a4 |
| V7 | Eredménysor ellenőrzésenként; nincs hosszú napló; futtatás nélkül nincs „sikeres” | 38–40 | mag | Marad | alap, e660e1a |
| V8 | A teljes tesztkör kétszer fut; egy futásban bukó teszt instabil, oka megkeresendő | 41–43 | mechanizmus | `run_suite` kétszeri futtatása | 1c76429, 10-11 |
| V9 | Futási sorrend: előbb a próbák, javítási körben csak az érintett modulok, a teljes kör egyszer a végső commiton | 45–51 | mechanizmus | `full_once` tree hash alapján; a modulválasztás projektfüggő | f98324a, 11-01 |
| V10 | Diff a `main`-hez; követelményenként teljesül, részben, nem | 54–55 | mag | Marad | alap |
| V11 | Eltérés: kódjavítás vagy rögzítés a Döntések alá; valódi döntésnél előbb az owner | 56–59 | mag | Marad | alap, e3146b8 |
| V12 | Átnevezett fájl említéseinek frissítése | 60–61 | üres | Duplikátum: C46 (`lint_dangling_paths`) | alap |
| V13 | Mély review M/L-nél, 2–3 subagent fókuszokkal, csak jelentenek, minden találat ellenőrizve | 65–68 | mag | Marad | alap, 9a7a6e9 |
| V14 | A reviewer scratch-mappába ír; utána a `git status` tiszta | 69–71 | mechanizmus | SubagentStop hook vagy `assert_no_new_files` (ugyanaz, mint P44) | ad4252a, 11-06 |
| V15 | Indoklás: tiszta fő kontextus | 72 | üres | Magyarázat, nem szabály | alap |
| V16 | Átadás: eredménytábla, javított eltérések, nyitott találatok | 76 | mag | Marad | alap |
| V17 | Fizetős API: tényleges felhasználás a becsléshez képest | 77–78 | mag | Marad, ez az egyetlen helye | ece3f7a, 10-09 |
| V18 | Kézi ellenőrzések rövid listája az ownernek | 79 | mag | Marad | alap |
| V19 | Emlékeztető: az owner olvassa el a kulcsteszteket, hogy a változás az övé legyen | 80–81 | mag | Marad | alap |
| V20 | Záró `multiSelect` ablak a befejező lépésekkel és minden takarítással, útvonallal; nyitott kézi ellenőrzésnél plusz kérdés | 82–88 | mag | Marad | 8961fae, 10-22 |
| V21 | Merge nyitott kézi ellenőrzéssel: nyitva hagyni, rögzíteni, `/replan` visszakérdez | 92–95 | mag | Marad, ez az egyetlen helye | 5fdedee, 10-10 |
| V22 | Roadmap pipálása csak Edit eszközzel; az őr a shellt tiltja | 97–101 | mechanizmus | Az őr elutasító üzenete mondja meg, hogy Edit kell; a mondat törlődik | a4a777b, 646d95b |
| V23 | `CHANGELOG.md` frissítése, ha a projekt vezet ilyet | 102 | mag | Marad (lásd Bizonytalan) | alap |
| V24 | A sikeres ellenőrzések kipipálása, a spec-mappa a `Plans/done/` alá | 103–105 | mag | Marad | a4a777b, a41ce0d |
| V25 | Áthelyezés után az útvonalak javítása és `validate.sh --quick` újrafuttatás | 105–109 | mechanizmus | `sdd archive` script | a41ce0d, ad4252a |
| V26 | Az áthelyezés üres indexből indul, és külön commit | 110–112 | mechanizmus | `sdd archive` ellenőrzi az üres indexet, és maga commitol | 1c76429, 10-11 |
| V27 | Commit és merge a bejelöltek szerint; push nem kérdezés nélkül | 113–115 | mag | Marad; a push-rész duplikátum (C62) | alap, 8961fae |
| V28 | Push után felugró ablak a branchcsel, remote-tal, commitlistával; elutasítás stoptábla | 116–121 | mag | Marad, rövidítve (lásd Bizonytalan) | 4a74b2d, 10-22 |
| V29 | A push ablakban a `/replan` felajánlása | 122–123 | mag | Marad | 8961fae, 10-22 |

## .claude/skills/replan/SKILL.md (70 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| R1 | „Run slow to run fast”: a feature-ök között idő jut a tervre | 8–9 | mag | Marad | alap |
| R2 | Tiszta indulás: friss `main`, tiszta munkafa, előző mergelve | 13–14 | mechanizmus | `check_clean_start` (ugyanaz, mint F2) | alap |
| R3 | A korábbi feature-ök nyitott kézi ellenőrzéseinek listája | 15–16 | mechanizmus | Az őr státusza kiírja a `Plans/done/*/validation.md` nyitott sorainak számát | 5fdedee, 10-10 |
| R4 | A constitution, a `Plans/done/` és a backlog olvasása | 17–18 | mag | Marad | alap |
| R5 | Roadmap-kérdések az ownernek | 24–25 | mag | Marad | alap |
| R6 | Constitution-kérdések | 26 | mag | Marad | alap |
| R7 | Munkafolyamat: mi ismétlődött kézzel, ami skill vagy ellenőrzés lehetne | 27–28 | mag | Marad; a „mechanizmus a mondat helyett” elv ide kerüljön | alap |
| R8 | A `Template:` sornál felajánlja a sablonfájlok áthozását, diff után | 29–31 | mag | Marad; a mag és a helyi bővítés szétválasztásával egyszerűsödik | 8c1b902, 10-22 |
| R9 | Minden munkafolyamat-javítás helyben, egy sor a `workflow-log.md`-ben | 32–36 | mag | Marad, ez az önjavító mechanizmus | 6c42c83, 10-24 |
| R10 | Hely költség szerint; `CLAUDE.md` 2000 szó alatt; új szabály régit vált ki | 37–40 | mechanizmus | `lint_size` teszt: szó- és sorkeret a `CLAUDE.md`-re és a SKILL.md-kre | 6c42c83, 10-24 |
| R11 | Review 10 tételnél: sablonba, helyben marad, törlés, a feltételekkel | 41–48 | mag | Marad, de a cél átírandó: helyben rendet tenni, nem a sablonba emelni | 6c42c83, 10-24 |
| R12 | A saját megfigyeléseid is legyenek opciók | 50 | mag | Marad | alap |
| R13 | `replanning/<topic>` branchen dolgozz | 54 | mag | Marad, ez az egyetlen helye | alap |
| R14 | A constitution zárolt: előbb a pontos változtatás, aztán `#spec-szerkesztes` | 55–56 | üres | Duplikátum: C10 | alap |
| R15 | Kis kódjavításhoz saját spec; nagyobb új munka új fázis | 57–59 | mag | Marad, ez az egyetlen helye (a spec kötelezőségét az őr kényszeríti) | alap |
| R16 | Ha a constitution változása specet vagy kódot érint, ugyanazon a branchen frissül | 60–61 | mag | Marad | alap |
| R17 | Új munkafolyamat-skill a projektbe, hacsak az owner nem kér globálisat | 62–63 | mag | Marad | alap |
| R18 | Záró `multiSelect` ablak; a push külön kérdés | 67–70 | mag | Marad | 8961fae, 10-22 |

## .claude/skills/constitution/SKILL.md (55 sor)

| # | Szabály (rövidítve) | Hely (sor) | Kategória | Javaslat | Eredet |
|---|---|---|---|---|---|
| K1 | A formátumok a `specs/README.md`-ben, pontosan követendők | 9–10 | mag | Marad | alap |
| K2 | Kontextus: `CLAUDE.md`, README, TODO, érintettek jegyzetei | 14–15 | mag | Marad | alap |
| K3 | Greenfield vagy brownfield; brownfieldnél subagent tárja fel a kódot, csak a hiányokról interjú | 16–22 | mag | Marad | alap |
| K4 | Módosítás `replanning/<topic>` branchen | 23 | mag | Marad | alap |
| K5 | Interjú írás előtt, három csoportban | 27–31 | mag | Marad | alap |
| K6 | Saját javaslatok az opciókban; az owner dönt | 33–34 | mag | Marad | alap |
| K7 | Amíg bármelyik fájl hiányzik, írható (bootstrap) | 38–39 | üres | Az őr kényszeríti; C8 is mondja | alap |
| K8 | Zárolás után elutasításnál megállás, pontos javaslat, nincs megkerülés | 40–42 | üres | Duplikátum: C10 | alap |
| K9 | A roadmap soronként egy checkbox fázis | 43 | üres | Duplikátum: `specs/README.md` 62–72 | alap |
| K10 | Összefoglaló, feltételezések, review-módosítások, konzisztencia | 47–50 | mag | Marad | alap |
| K11 | Záró `multiSelect` ablak: commit, majd `/feature-spec` | 51–54 | mag | Marad | 8961fae, 10-22 |
| K12 | A `#spec-zar` begépelendő, nem kattintható | 55–56 | üres | Duplikátum: C53 | 8961fae, 10-22 |

## Közös lib-függvények

Javaslat: a mechanizmusok négy helyre kerülnek, mindegyik a sablon repójában tesztelve. A projekt nem szerkeszti őket; a projektfüggő részt horgokkal (hook-függvényekkel) adja meg. A zárójel azt mutatja, hány mostani szabályt vált ki.

`.claude/lib/sdd_check.sh` (a `validate.sh` forrásolja be; 19 szabály: C29, C33, P22, P23, P24, P27, P28, P29, P30, P31, P32, P33, P34, P35, P36, F36, F43, V8, V9; plusz a duplikátumaik, F32–F35, F38, F39 szövege):

- `sdd_init "$@"`: a repó gyökerébe lép, beállítja a szigorú módot, elemzi a `--live` és `--quick` kapcsolót, `--live`-nál betölti a rögzített nevű helyi beállításfájlt, ideiglenes mappát nyit `trap`-pel, és megadja a script saját mappáját.
- `check ID NAME CMD...`: lefuttat egy ellenőrzést, kiír egy `PASS`/`FAIL` sort az azonosítóval és rövid bizonyítékkal, és megjegyzi a hibát.
- `sdd_finish`: összesít, és bármely hibánál nem nulla kóddal lép ki.
- `live_only`: `--live` nélkül kihagyottnak jelöli az ellenőrzést.
- `start_bg NAME CMD...`: háttérfolyamatot indít a fő shellben, a PID-et regisztrálja; az EXIT trap PID szerint állítja le (soha `pkill -f`).
- `free_port`: szabad portot ad.
- `assert_absent PATTERN TARGET --proof SAMPLE`: a „nincs X” állítás előtt megköveteli, hogy a minta egy ismert pozitív példán egyezzen.
- `run_suite CMD`: kétszer futtatja a tesztkört, kigyűjti a bukott tesztek nevét (a minta projektbeállítás, pytestnél `-rf`), és a két futás eltérését instabilnak jelöli.
- `full_once CMD`: a teljes kört kihagyja, ha ugyanarra a tree hashre már volt zöld futás (ez váltja ki a `--quick`-et és a futási sorrend szabályát).
- `export_main DIR`: `git archive main` a repóból, és hibát ad, ha a másolat üres.
- `check_url URL`: HTTP státusz és végső host átirányítások után.
- `prove_red TEST_CMD --base REF --timeout S`: az új tesztet a régi kódon, ideiglenes munkafában, egyedül és időkorláttal futtatja, és bukást vár.
- `suite_lock`: `flock` zár, amelyet a tesztkör, az élő teszt és a próba egyaránt kér.

`.claude/lib/sdd_probe.sh` (5 szabály: P39, P41, P42, P43, P44, és a V14 duplikátum):

- `probe_base SAMPLE`: egyszer naprakész alapmásolat a scratchpadben, a projekt `probe_upgrade` horgával, fizetős lépés nélkül.
- `probe_copy ROUND NAME`: friss, teljes másolat körönként és próbánként (`git ls-files -co --exclude-standard`, így nem kell kézi `git add`, és az ignorált valódi adat kimarad), utána a projekt `probe_regen` horga.
- `snapshot_status` és `assert_no_new_files`: a próba vagy a reviewer előtt és után összeveti a `git status`-t.

`.claude/lib/sdd_lint.py` (a pre-commit hook és a `validate-feature` futtatja; 10 szabály: C46, P15, P17, P19, P33, F30, F31, F40, R10, V3, és részben P9, P10, P18):

- `lint_spec`: a `spec.md` `szint:` sora és a szinthez kötelező szakaszok.
- `lint_decisions`: minden Döntések-sorban dátum és pontosan egy `döntött: owner|agent`; a `main`-hez képest törölt sor csak felváltva-jelöléssel.
- `lint_calibrations`: minden „kalibrálandó” döntéshez Kalibrálás alszakasz a négy mezővel.
- `lint_coverage`: minden gépi `validation.md` pont azonosítója szerepel egy `check` hívásban.
- `lint_validate_kept`: a `#spec-ok` kori `check` azonosítók megvannak, vagy a Döntések említi az elhagyásukat.
- `lint_spec_paths`: tesztben és spec-mappás scriptben nincs beírt `Plans/ÉÉÉÉ-` útvonal és `parents[n]`.
- `lint_shell`: `bash -n` és `shellcheck` a `Plans/**/*.sh` fájlokra.
- `lint_dangling_paths`: a specekben, README-kben backtickbe tett útvonalak léteznek.
- `lint_size`: a `CLAUDE.md` és a SKILL.md-k méretkerete.

`sdd` parancs és az őr bővítései (14 szabály: C9, C39, C61, C63, P7, P31 második fele, F2, F5, F41, F47, R2, R3, V22, V25, V26):

- `sdd new <branch>`: előfeltétel-ellenőrzés (tiszta munkafa, friss `main`, előző mergelve, constitution megvan), branch, dátumos spec-mappa, sablon `szint:` sorral.
- `sdd handover`: az új spec `validate.sh`-jának egyszeri offline futása, `lint_shell`, a használt URL-ek `check_url`-ja; a kimenet az átadásba kerül.
- `sdd archive`: üres index ellenőrzése, áthelyezés a `Plans/done/` alá, útvonaljavítás, `validate.sh` újrafuttatás (`full_once`), külön commit.
- `sdd commit MSG`: a projekt ellenőrző parancsa (tech-stackből), és csak zöldnél commit.
- Őr, PreToolUse: tiltja a `git add -A`, `git add .`, `git commit -a`, `pkill -f` parancsot, a branchváltást futó feature alatt, és a `#spec-` kezdetű sort subagent promptban; a roadmap shelles írásakor az üzenet az Edit eszközt nevezi meg.
- Őr, session státusz: a nyitott kézi ellenőrzések száma; `#spec-ok` után emlékeztető, ha a spec zárolt fájlt érint.
- SubagentStop hook: figyelmeztet, ha a subagent fájlt hagyott a munkafában.
- `commit-msg` hook: `docs(specs)` és `docs(plans)` scope a csak spec-változásnál.

A 48 mechanizmus-szabályt és kb. 15 szöveges duplikátumukat négy tesztelt eszköz váltja ki. A `Plans/README.md` „validate.sh” szakasza (52 sor) ezzel kb. 8 sorra zsugorodik: „használd a `sdd_check.sh` függvényeit”.

## Bizonytalan esetek

| # | Szabály | Választott | A másik lehetőség |
|---|---|---|---|
| C2, C58 | Nyelvszabály | mag, telepítési paraméterként | projektfüggő: az owner minden projektje magyar, de a sablon MIT licencű és van angol README-je; ha mások is használják, a nyelv az `install.sh` kérdése legyen |
| C48, C50, C54, C55 | Felugró ablakos döntések | üres (a globális `~/.claude/CLAUDE.md` mondja) | mag: ha a sablont más is használja, a globális fájl nem jön vele, akkor egy rövid változat kell |
| C28 | Háttérben futó tesztkör alatt csak olvasás | projektfüggő | mag: a „csoportonként egy commit” része; minden lassú tesztkörű projektben igaz |
| C33 | Nincs párhuzamos terhelés a tesztkör alatt | mechanizmus (`suite_lock`) | projektfüggő: csak a terhelt WSL/DGX gépen volt gond |
| C30, P8 | Élő minta a bevezető csoportban, az agent látható döntéseinek listájával | mag | projektfüggő: csak felületet vagy hangot adó projektre igaz; mehet egy UI skillbe |
| P16 | Kalibrált érték constitution-frissítése ugyanabban a csoportban | projektfüggő | mag: a „spec és kód szinkronban” elv egy esete, és akkor C43 lefedi (üres) |
| P40 | Szándékos rontás leírása a próba előtt | projektfüggő | mag: minden próbára igaz, ahol a rontás része a feladatnak |
| F6 | Spec előtt ellenőrizni, hogy a cél nem teljesül-e | mag | üres: egy képes modell alapból megnézi |
| F15 | Meglévő felület viselkedésének leírása | projektfüggő | mag: minden „mint X-ben” kérésre igaz, nem csak felületre |
| F24 | Mért érték pontos bemenete | projektfüggő | mag: a reprodukálhatóság általános elv |
| F28 | Időkorlátos teszt újramérése | projektfüggő | mechanizmus: egy közös `retry_timing` tesztsegéd, de ez nyelvenként más, ezért inkább a projekt tesztkönyvtárába |
| F42 | `--live` rész egyszeri futtatása spec-íráskor | projektfüggő | mechanizmus: az `sdd handover --live` opció, ha a projektnek van telepített példánya |
| V23 | `CHANGELOG.md` frissítése | mag | projektfüggő: csak changelogot vezető projekt |
| V28 | Push ablak commitlistával | mag | üres: a globális „Ask first: git push” és a C51 együtt lefedi |
| V3 | A jóváhagyott `validate.sh` csak bővül | mechanizmus (`lint_validate_kept`) | mag: egy mondat elég, a lint túl merev lehet, ha egy ellenőrzés jogosan átalakul |

## Döntések

- A sablont csak az owner használja: a nyelvi (C2, C58) és a felugró ablakos szabályok (C48, C50, C54, C55) kikerülnek a sablonból, mert a globális `~/.claude/CLAUDE.md` tartalmazza őket (döntött: owner, 2026-11-22).
- Az átalakítás terv alapján, négy szakaszban halad, minden szakasz után owner-átnézéssel (döntött: owner, 2026-11-22).
- A `replan` és a `constitution` sorszámait az átvilágítás után javítottuk: az első változat az összefűzött fájlokból számolt (döntött: agent, 2026-11-22).
