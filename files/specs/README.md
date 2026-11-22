# specs/: a projekt constitutionje

A constitution azokat a döntéseket tartalmazza, amelyekre minden feature
épül. Az owner és az agent közötti interjúban készül (`/constitution`), és az
owner kezeli.

| Fájl | Mire válaszol | Mikor változik |
|---|---|---|
| `mission.md` | Miért létezik, kinek, mi van a hatókörben és mi nincs? | Ritkán |
| `tech-stack.md` | Milyen technológiák és korlátok, és miért? | Újratervezéskor |
| `roadmap.md` | Milyen kis, szállítható fázisokban jutunk el oda? | Minden újratervezéskor |
| `backlog/` | Kutatás és ötletek, amelyek még nincsenek a roadmapen | Bármikor (nem zárolt) |

## mission.md

```markdown
# Mission

## Vízió
<egy bekezdés: a probléma és a változás, amit a projekt hoz>

## Célközönség
- <ki>: <mire van szüksége tőle>

## Hatókör
- <hatókörben>

## Nem célok
- <kifejezetten hatókörön kívül>

## Érintettek igényei
- <név / szerep>: <mit kért>
```

## tech-stack.md

```markdown
# Tech stack

## Áttekintés
<két-három mondat>

## Stack
| Réteg | Választás | Verzió | Indoklás |
|---|---|---|---|
| Nyelv | ... | rögzített | ... |

## Korlátok
- <céges szabványok, hosting, biztonság, licencek>

## Tesztelés és validáció
- <tesztkeretrendszer, hogyan futnak az ellenőrzések: parancsok>

## Ismert hiányosságok
- <ami tudatosan hiányzik egyelőre>
```

## roadmap.md

Minden fázis egy legfelső szintű checkbox sor. Az SDD őr az első nyitottat
olvassa következő fázisként, és egy doboz kipipálása (`[ ]` → `[x]`) az
egyetlen roadmap-módosítás, amelyet az agent feloldás nélkül elvégezhet.

```markdown
# Roadmap

A fázisok szándékosan kicsik: mindegyik szállítható szelet, önállóan
review-zható és tesztelhető.

- [ ] Fázis 1: <cím>
  - <mi készül el>
  - <honnan tudjuk, hogy működik>
- [ ] Fázis 2: <cím>
  - ...
```

## backlog/

Témánként egy fájl: `backlog/YYYY-MM-DD-<topic>.md`, benne a kérdés, a
megállapítások, a javaslat és a döntés. Backlog-elem csak újratervezésen
keresztül kerülhet a roadmapre, a fájljára mutató hivatkozással.

A cím alatt, az első 20 sorban egy állapotsor áll, egy rögzített szóval
kezdve, utána szabad szöveggel:

```markdown
Állapot: nyitott | ütemezve | kész | elvetve: <részletek, például: Fázis 18; a 3. pont még nyitott>
```

`nyitott`, amíg bármelyik pontjáról nem született döntés. Az `sdd preflight`
a nyitott és az állapotsor nélküli tételeket listázza, a `/replan` ezekkel
kezd; a lint jelzi a hiányzó állapotsort.

# A projekt közös nyelve és döntései (`docs/`)

Két, nem zárolt fájl a constitution mellett. Egyiket sem kell előre megírni:
az első bejegyzéssel jönnek létre (a kikérdezés, a spec-interjú vagy a
kódszerkezet-felmérés közben).

## docs/szotar.md

A projekt saját fogalmai: a felület, az üzenetek, a specek és a doksi
ugyanazt a magyar szót használja, a kód pedig mindig ugyanazt az angol nevet.
Általános programozási fogalom (időkorlát, hibatípus) csak akkor kerül bele,
ha ebben a projektben mást jelent, vagy két jelentésben fut. Megvalósítási
részlet, élettartam és állapot nem kerül bele: az a specbe tartozik. Nincs
létszámkorlát; először a félreérthető szavak kerülnek be.

```markdown
# Szótár: <projekt>

<1–2 mondat: miről szól a projekt nyelve.>

## <fogalomcsoport: a felhasználó útjának lépései szerint, ha van ilyen>

- **<fogalom>**: <1–2 mondat: mi ez; műveletnél: mit ér el a felhasználó szemével.>
  - Kódban: `<a fő angol azonosító>` (vagy: még nincs; ha a kód ma mást használ: „ma: `<régi név>`”)
  - Kerülendő: <szinonimák, amelyeket nem használunk>
  - Nyitott: <ütközés, amelyről az owner még nem döntött> (csak amíg nyitott)
```

- Egy fogalomra egy szó; a többi a „Kerülendő” sorba kerül. Ha a felület,
  a doksi és a kód eltérő szót használ, az agent javasol, az owner választ:
  addig a bejegyzés „Nyitott” sort kap. Ugyanez, ha egy szó két jelentésben
  fut.
- A „Kódban” sor a fő azonosító (osztály, függvény vagy mező, ami a fogalmat
  hordozza). Ha a kívánt név eltér a mostanitól, az átnevezés backlog-tétel,
  nem csendes kódváltozás.
- A magyar szó és a kódnév lehet azonos (`vault`).
- Ha a projektben már van fogalomtár (egy doksi „Fogalmak” szakasza), annak
  tételei átkerülnek ide, és a régi helyén egy mutató marad.

## docs/decisions/

Nehezen visszafordítható döntések, sorszámozva: `NNNN-<slug>.md` (a
legnagyobb sorszám plusz egy). Döntésnapló csak akkor készül, ha mind a
három igaz; ha egy hiányzik, a döntés a spec „Döntések” sorában marad:

1. **nehezen visszafordítható**: a meggondolás később érdemi költség;
2. **kontextus nélkül meglepő**: egy későbbi olvasó azt kérdezné, miért így;
3. **valódi mérlegelés eredménye**: volt komoly alternatíva.

```markdown
# NNNN – <a döntés rövid címe>

- Állapot: javasolt | eldőlt (ÉÉÉÉ-HH-NN) | felváltva: NNNN
- Dátum: ÉÉÉÉ-HH-NN

<1–3 mondat: a helyzet, a döntés és az oka.>

## Mérlegelt lehetőségek (ha az elvetés nem magától értetődő)
## Következmények (ha nem nyilvánvalók)
```

Jellemző tárgyak: a rendszer szerkezete, technológia bezáródással (adatbázis,
hitelesítés, hosting), hatókör-határok és a kifejezett nemek, a kézenfekvő
úttól való szándékos eltérés, a kódban nem látható korlát. A kódszerkezet-
felmérés nem javasolja újra, amit egy döntésnapló elvetett, csak ha a
súrlódás valódi.

## docs/kodolasi-szabalyok.md

A projekt kódolási szabályai, amelyek mérlegelést igényelnek (amit lint vagy
teszt el tud dönteni, az oda kerül, nem ide). Az implementáló agent nem
tölti be; a `/validate-feature` mély review-jának subagentjei kapják meg, és
a találatuk megnevezi a megsértett szabályt.

```markdown
# Kódolási szabályok

- <szabály egy mondatban>: <miért; egy rossz és egy jó példa, ha kell>
```
