# Javaslat: tanulságok Matt Pocock munkafolyamatából

Forrás: NetworkChuck, „How to Actually Code with AI (ft. Matt Pocock)”,
2026, https://www.youtube.com/watch?v=mU8WKII1gpk (a percjelölések a videóra
utalnak). Állapot: javaslat, még semmi nincs bevezetve. A döntés az owneré.

## Kiinduló megállapítás

Matt folyamatának gerince nálunk már megvan: kikérdezés (`grill`), méret
szerinti út (`size-up`), spec, feladatcsoportok, review, `retro`. Matt fő
tétele: az AI jó a taktikai programozásban, és gyenge a stratégiaiban (5. és
44. perc). A stratégiai réteg, vagyis hogy a kód hosszú távon könnyen
változtatható maradjon, nálunk a leggyengébb. A másik tanulság a saját
utasításaink mérete: a tanulságokat eddig többnyire egy-egy mondatként írtuk
egy MD-fájlba, ahelyett hogy a hibát lehetetlenné tettük volna.

Bizonyíték: a pii-pajzs `.claude/workflow-log.md` 17 tételéből 14 egy mondat
egy MD-fájlban. A sablon `feature-spec` skillje 223 sor, a `Plans/README.md`
324 sor, a projekt CLAUDE.md-je 249 sor (a hivatalos ajánlás 200 sor alatt).

## 0. A sablon szerepe: mag, nem tanulsággyűjtemény (owner kérése, 2026-11-22)

**Probléma.** A 10 tételenkénti review eddig a sablonba ültette vissza a
helyi tanulságokat. Hét hét alatt (2026-10-05 → 2026-11-21) öt ilyen
visszaültetés volt, és a sablon így nőtt: `feature-spec` 62 → 223 sor,
`Plans/README.md` 86 → 324 sor, `CLAUDE.md` 130 → 249 sor. A tételek nagy
része egy-egy projekt (főleg a pii-pajzs) konkrét csapdája, mondatként
leírva. Más projektben vagy nem releváns, vagy kóddal kellett volna
megoldani.

**Cél.** A sablon egy kicsi, stabil **mag**: a szemlélet, a kapuk és az a
mechanizmus, amellyel minden projekt magától javul. A sablonhoz csak
kivételes esetben nyúlunk vissza.

**Javaslat.**

1. **Mag és projekt szétválasztása.** A sablon fájljai a projektben nem
   szerkeszthetők helyben (a skillek, a `CLAUDE.md` magrésze, a lib-ek). A
   projekt saját bővítési pontokba ír: `.claude/rules/*.md` (útvonalhoz
   kötve), a projekt saját segédscriptjei és tesztjei, egy rövid
   `CLAUDE.local-rules` szakasz vagy fájl. Így egy sablonfrissítés nem ütközik
   a helyi tanulságokkal, és a `Template:` sor az SDD-státuszban valódi
   eltérést jelez, nem helyi kiegészítést.
2. **A helyi tanulás a projektben marad.** A `workflow-log.md` megmarad, de a
   10 tételenkénti review célja megváltozik: nem a sablonba emel, hanem helyben
   rendet tesz. Minden tételről döntés: kóddá vagy ellenőrzéssé alakítható-e
   (az 1. fok szerint), összevonható-e egy másikkal, törölhető-e. A review
   eredménye jellemzően **kevesebb** szöveg, mint előtte.
3. **Szigorú kapu a sablonhoz.** Egy tanulság csak akkor kerül a sablonba, ha
   mind igaz:
   - mechanizmus, nem mondat (lib-függvény, hook, teszt, egy lépés
     szerkezete), vagy a szemléletet érinti;
   - legalább két különböző projektben, egymástól függetlenül előjött;
   - nem oldható meg a projekt bővítési pontjain.
   A sablonmódosítás külön javaslatfájl ebben a `backlog/` mappában, és az
   owner hagyja jóvá.
4. **Méretkeret a magnak.** `CLAUDE.md` 200 sor alatt (hivatalos ajánlás),
   minden SKILL.md 100 sor alatt, a lépések részletei segédfájlban. Egy új
   sor csak egy régi kiváltásával vagy összevonásával jöhet be. A keretet egy
   teszt ellenőrzi a sablon repójában, nem egy mondat.
5. **A szemlélet maga a mag.** A sablon a tanulságok helyett azt szállítja,
   ami miatt a projektek jó irányba fejlődnek: a szabályhely-sorrendet (1.),
   a közös lib-eket (2.), a szótárat (3.), a kódszerkezet-felmérést (4.) és a
   kockázat szerinti review-t (5.).

**A meglévő sablon visszavágása.** Egyszeri átvilágítás: a sablon minden
szabályáról egy döntés, táblázatban:
- *mag*: szemlélet vagy kapu, minden projektre igaz → marad;
- *mechanizmus*: kóddal kiváltható → a lib-be vagy egy tesztbe kerül, a
  szöveg törlődik;
- *projektfüggő*: egy projekt csapdája → visszakerül annak a projektnek a
  bővítési pontjára (a pii-pajzsnál `.claude/rules/` vagy saját script),
  vagy törlődik;
- *üres*: a modell magától is így tesz → törlődik.
A táblázatot az owner hagyja jóvá, utána jön a karcsúsítás.

**Kockázat.** A visszavágással elveszhet egy szabály, amely valódi hibát
előzött meg. Csökkentés: a *projektfüggő* tételek a pii-pajzsban
megmaradnak helyben; a *mechanizmus* tételeket a lib tesztje őrzi; minden
törölt szabály a táblázatban marad indoklással.

**Ellenőrzés.** A visszavágás után egy friss subagent-próba végigvisz egy M
fokozatú specet egy mintaprojekten csak a karcsúsított sablonnal. Sikeres, ha
nem akad el, és a `validate.sh` a lib-et használja.

## 1. Új szabályhely-sorrend (a többi javaslat alapja)

**Probléma.** Egy finding után a legolcsóbb lépés egy mondat valamelyik
MD-fájlban. Ez minden sessionben vagy minden spec-írásnál betöltődik, akkor is,
ha nem kell, és a betartása az agent figyelmén múlik.

**Matt elve (84–86. perc).** Ha választhatsz determinisztikus és nem
determinisztikus megoldás között, mindig a determinisztikusat válaszd. A
legtöbben nem is tudják, hogy van választásuk.

**Javaslat.** Egy tanulság ebben a sorrendben kap helyet, és az első
alkalmazható fokon áll meg:

1. kód vagy ellenőrzés, amely miatt a hiba el sem követhető (közös
   segédscript, teszt, lint-szabály, hook);
2. útvonalhoz kötött szabály: `.claude/rules/<téma>.md` `paths:` fejléccel,
   amely csak illeszkedő fájl olvasásakor vagy szerkesztésekor töltődik be;
3. egy lépés saját segédfájlja a skill mappájában, a lépés szövegéből
   hivatkozva („a `validate.sh` írása előtt olvasd el: `validate-sh.md`”);
4. CLAUDE.md, csak ha minden sessionre igaz.

A `@útvonal` import nem számít megtakarításnak: a hivatalos dokumentáció
szerint induláskor betöltődik (code.claude.com/docs/en/memory, „Import
additional files”).

**Hol.** A `/replan` 3. kérdéscsoportja és a `workflow-log.md` formátuma
(egy új oszlop: melyik fok, és ha nem az 1., miért nem). A `retro` skill már
ezt a sorrendet írja; a változás az, hogy a `/replan` is kötelezően
végigmegy rajta.

**Kockázat.** Az igény szerint betöltődő fájlt az agent kihagyhatja.
Csökkentés: a 2. fokon a kiváltó gépi; a 3. fokon a hivatkozás egy
konkrét lépésben áll, és a friss subagent-próba ellenőrzi, hogy a próba
megnyitja-e a fájlt.

**Ellenőrzés.** A következő 10 naplótételből legalább a fele az 1. vagy 2.
fokon landol.

## 2. Karcsúsítás

**Probléma.** A `feature-spec` 4. lépése és a `Plans/README.md` „validate.sh”
szakasza kb. 20 szabályt hordoz a `validate.sh` csapdáiról (szabad port, PID
szerinti leállítás, `$(...)` kerülése, `pkill -f` tilalma, a saját mappa
megtalálása, `git archive main`, ideiglenes könyvtár). Ezek minden
spec-írásnál betöltődnek.

**Javaslat.**

- **Közös segédscript (1. fok).** A sablon kapjon egy tesztelt
  `Plans/lib/validate-lib.sh`-t: szabad port, szerverindítás a fő shellben
  PID-del, takarítás `trap`-pel kilépéskor, saját ideiglenes könyvtár,
  `PASS`/`FAIL` sor, `--quick` és `--live` kapcsoló, `main` exportja
  üresség-ellenőrzéssel. A `validate.sh` ezt használja; a szabályok helyére
  egy mondat kerül: „használd a `validate-lib.sh`-t; ha valami hiányzik
  belőle, bővítsd a lib-et”. Ugyanígy egy `prepare-probe-lib.sh` a
  subagent-próba előkészítésére.
- **Segédfájlok (3. fok).** A `feature-spec` lépésenként mutató legyen: a
  `validate.sh`, a subagent-próba, a kalibrálás és a fizetős API részletei
  külön fájlba kerülnek a skill mappájában, a lépés hivatkozik rájuk. Cél:
  SKILL.md 100 sor alatt.
- **CLAUDE.md 200 sor alá.** A lépésekhez kötött részek („Szabályok
  lépésenként”) a skillekbe költöznek; a CLAUDE.md-ben a munkafolyamat
  táblája, az őr szabályai és a mindig érvényes elvek maradnak.
- **Egyszeri tisztítás.** Minden szabályról döntés: lib-be, rule-ba,
  segédfájlba, CLAUDE.md-be, vagy törlés (ha a lib miatt már nem
  követhető el, vagy a modell magától is így tesz).

**Kockázat.** A lib maga is hibázhat, és minden projekt függ tőle. Ezért
saját tesztet kap a sablonban (`files/Plans/lib/test_validate_lib.sh` vagy
pytest), és a `install.sh` frissíti. A meglévő projektek régi `validate.sh`-i
érintetlenek maradnak.

**Ellenőrzés.** Friss subagent-próba: egy subagent csak a karcsúsított
`feature-spec`-et kapja egy mintaprojekttel, és megír egy `validate.sh`-t,
amely háttérszervert indít. Sikeres, ha a lib-et használja, és a szerver a
script után nem fut.

## 3. Közös szótár

**Probléma.** A `grill` skill most kifejezetten tiltja új szótárfájl
létrehozását. Matt szerint (14–24. perc) a közös nyelv a legelső stratégiai
lépés: ha a felület, az üzenetek és a kód ugyanazt a szót használja, az agent
rövidebben és pontosabban beszél, és a kód is olvashatóbb.

**Javaslat.**

- Projektenként egy `docs/szotar.md`: fogalom, egy mondatos jelentés, a kódban
  használt név, kerülendő szinonimák.
- Nem kell előre megírni. A `grill` minden körben felveszi az új fogalmat, és
  megkérdezi, ha egy szó két jelentésben fut. A `feature-spec` és a
  `validate-feature` hivatkozik rá; a mély review jelzi, ha a kód eltér tőle.
- Csak mutató kerül a CLAUDE.md-be (egy sor), maga a szótár igény szerint
  töltődik be.

**Kérdés az ownernek.** Mi legyen a kódban: a magyar szó, vagy egy rögzített
angol megfelelő? (Javaslat: a szótár mindkettőt rögzíti, a kód az angolt.)

**Ellenőrzés.** A pii-pajzsban egy próbakör: 10–15 fogalom (álnév,
visszaállítás, vault, detektor, …) és egy csak olvasó felmérés, hol tér el a
kód, a felület és a dokumentáció.

## 4. Kódszerkezet-felmérés (mély modulok)

**Probléma.** Nálunk semmi nem figyeli, hogy a kód könnyen változtatható
marad-e. Matt (54–68. perc) John Ousterhout „mély modul” fogalmára épít: sok
logika egy szűk felület mögött, a tesztek ezen a felületen át mennek, így a
belső átírás nem töri el őket. A sekély, szétszórt modulok és a megvalósítást
ismétlő tesztek a romló kód fő jelei.

**Javaslat.**

- Új globális skill (munkanév: `architecture-review`): csak olvas, a friss
  commitok környékén keresi a sekély modulokat, a duplikációt, a
  megvalósítást ismétlő teszteket és a rossz lokalitást (egy változás sok
  fájlt érint). Kimenete egy HTML-riport előtte–utána vázlattal és
  javaslatonként egy mondatos indoklással.
- Helye a folyamatban: a `/replan` felajánlja feature-ök között; a találatok
  a `specs/backlog/` alá mennek, és rendes specként valósulnak meg. Nincs
  automatikus PR, mert az őr és a `#spec-ok` ezt nem engedné, és a
  pii-pajzsban nem is kívánatos.
- A riport fogalmait a `teach` skill magyarázza el kérésre.

**Nyitott.** Matt saját skilljének (`improve-codebase-architecture`)
tartalmát még nem olvastam; a megírás előtt meg kell nézni
(aihero.dev/skills), és a licencét is.

**Ellenőrzés.** Egy csak olvasó futás a pii-pajzs `engine/` könyvtárán, a
riportot az owner értékeli: van-e benne legalább egy javaslat, amelyet
specként megcsinálna.

## 5. A review mélysége a kockázat szerint

**Probléma.** A kézi ellenőrzések mennyisége most a spec írásakor dől el, és
nem függ attól, mekkora a tényleges kockázat. Matt (40–42. perc) a
beolvasztás veszélye szerint dönt: egyirányú ajtó (nem vonható vissza:
adatvesztés, kiküldött levél) vagy kétirányú, és mekkora a hatósugár.
Kétirányú, kis hatósugarú változást alig néz meg; egyirányú, nagy
hatósugarút megpróbál eltörni.

**Javaslat.**

- A spec „Kockázat és visszaút” szakasza két mezőt kap: `ajtó: egyirányú |
  kétirányú` és `hatósugár: kicsi | közepes | nagy`, egy mondatos
  indoklással.
- A `validate-feature` átadása ebből számolja, mit kér az ownertől: kétirányú
  és kicsi esetén csak a bizonyítékot (képernyőkép, kimenet); egyirányú vagy
  nagy esetén a kézi ellenőrzéseket és a mély review-t alapértelmezettként.
- A projekt felülírhatja: a pii-pajzsban minden, ami kimenő adatot érint,
  automatikusan nagy hatósugarú.

**Ellenőrzés.** A következő két feature átadásában szerepel a két mező, és az
owner szerint a kért kézi munka arányos volt.

## Javasolt sorrend

1. A sablon szerepe (0.): a meglévő szabályok átvilágító táblázata, owner
   jóváhagyással. Ez dönti el, mi marad a magban.
2. Szabályhely-sorrend és karcsúsítás (1–2.), a lib-ekkel együtt: ez
   csökkenti a kontextust, és minden további szabály már az új rendbe kerül.
3. Kockázat szerinti review (5.): kicsi, gyorsan hasznos.
4. Szótár (3.): a pii-pajzson kipróbálva.
5. Kódszerkezet-felmérés (4.): a legnagyobb munka, Matt skilljének
   átolvasása után.

## Amit tudatosan nem veszünk át

- Párhuzamos subagentek külön munkafákban, egy nagy PR: nálunk egy munkafa
  egy branch, és a feladatcsoportok sorban jönnek. Egy owner mellett ez
  átláthatóbb.
- Napi cron-feladat automatikus PR-ekkel és mintavételes review-val: Matt
  maga mondja, hogy orvosi vagy pénzügyi alkalmazásnál ezt nem tenné.
- GitHub issue-k a `Plans/` helyett: a helyi specet az őr és a pre-commit
  hook is olvassa.
