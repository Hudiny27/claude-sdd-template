# specs/: a projekt constitutionje

A constitution azokat a döntéseket tartalmazza, amelyekre minden feature
épül. Az owner és az agent közötti interjúban készül (`/constitution`), és az
owner kezeli: amint mindhárom fájl létezik, az SDD őr blokkolja az agent
írásait, amíg az owner fel nem oldja őket a `#spec-szerkesztes` kulcsszóval
(lásd `CLAUDE.md`).

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
- <ki> — <mire van szüksége tőle>

## Hatókör
- <hatókörben>

## Nem célok
- <kifejezetten hatókörön kívül>

## Érintettek igényei
- <név / szerep> — <mit kért>
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

- [ ] Fázis 1 — <cím>
  - <mi készül el>
  - <honnan tudjuk, hogy működik>
- [ ] Fázis 2 — <cím>
  - ...
```

## backlog/

Témánként egy fájl: `backlog/YYYY-MM-DD-<topic>.md`, benne a kérdés, a
megállapítások, a javaslat és a döntés. Backlog-elem csak újratervezésen
keresztül kerülhet a roadmapre, a fájljára mutató hivatkozással.
