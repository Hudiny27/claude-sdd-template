# Claude SDD sablon: spec-driven fejlesztés kikényszerítve

*English version: [README.en.md](README.en.md)*

Projektsablon Claude Code-hoz. Egyetlen paranccsal felépíti a **spec-driven
development (SDD)** munkafolyamatot egy új vagy meglévő projektben. Létrehozza
a szabályokat, a mappaszerkezetet és a workflow-skilleket. Hookokat is
telepít: ezek a lényeges szabályokat **ki is kényszerítik**, nem csak leírják.

A módszertan alapja a DeepLearning.AI × JetBrains kurzusa:
[Spec-Driven Development with Coding Agents](https://www.youtube.com/watch?v=hy8UstR2NEg).

---

## Mi az SDD?

A kódot egy verziókezelt markdown spec vezérli. A spec mondja meg, **mit** és
**miért** kell építeni; a **hogyan** az agent dolga. Te vagy az architekt, az
agent a kivitelező: *„az agent az izom, a spec az agy”*.

Három előnye van:

1. **Felerősítés.** Egy mondat a spec-ben több száz sor kódot határoz meg, ezért
   a spec-et módosítani olcsóbb, mint a kódot.
2. **Nincs kontextusvesztés.** Az agent sessionök között mindent elfelejt; a
   spec megmarad, és minden új session ebből indul.
3. **Pontosabb eredmény.** A problémát, a sikerkritériumokat és a korlátokat
   előre rögzíted, így az agent azt építi, amit akarsz.

## Hogyan működik?

```
/constitution → /feature-spec → #spec-ok → implementáció → /validate-feature → /replan → /feature-spec …
```

| Lépés | Mi történik | Eredmény |
|---|---|---|
| 1. **Constitution** (`/constitution`) | Interjú az agenttel a misszióról, a tech stackről és a roadmapről. Meglévő kódbázisnál az agent először a kódból fejti vissza. | `specs/mission.md`, `tech-stack.md`, `roadmap.md` |
| 2. **Feature spec** (`/feature-spec`) | A következő roadmap-fázishoz branch és interjú készül, majd 3 fájl. **Kód még nem.** | `Plans/ÉÉÉÉ-HH-NN-<slug>/plan.md, requirements.md, validation.md` |
| 3. **Jóváhagyás** | Átnézed a spec-et. Ha rendben van, egy sor elejére írod: `#spec-ok` | Ezen a branchen írható kód |
| 4. **Implementáció** | Az agent task groupról task groupra halad a `plan.md` alapján | Kód + commitok |
| 5. **Validáció** (`/validate-feature`) | Lefut a `validation.md` minden ellenőrzése, a spec és a kód eltérései javulnak, szükség esetén mély review indul subagentekkel | Roadmap-pipa, a spec a `Plans/done/` mappába kerül, merge |
| 6. **Újratervezés** (`/replan`) | A roadmap, a constitution és maga a munkafolyamat felülvizsgálata | Frissített terv a következő feature-höz |

### Kikényszerítés: mit csinálnak a hookok?

A `.claude/hooks/sdd_guard.py` egyetlen fájlban tartalmazza a szabályokat,
és három helyről fut: Claude Code-hookként, git pre-commit hookként és CI-ból.

| Szabály | Mi tiltja | Feloldás |
|---|---|---|
| A constitution (`specs/mission.md`, `tech-stack.md`, `roadmap.md`) csak a te engedélyeddel változik | PreToolUse hook | `#spec-szerkesztes`, visszazárás `#spec-zar`, vagy 12 óra után magától |
| Nincs kód a `main` branchen | PreToolUse hook + git pre-commit | – |
| Nincs kód jóváhagyott spec nélkül | PreToolUse hook (+ pre-commit: létező spec) | `#spec-ok` az adott branchen |
| A guard nem kapcsolható ki (hookok, `settings.json`, `settings.local.json`, `.githooks/`) | PreToolUse hook | `#spec-szerkesztes` |
| A git hookok nem kerülhetők meg (`--no-verify`, `core.hooksPath`) | PreToolUse hook | nincs |
| A PR-ben a kódváltozás mellett a spec is változott (opcionális) | GitHub Actions `sdd-check` | `no-spec-change` címke a PR-en |
| Az agent minden session elején ismeri az állapotot | SessionStart hook | – |

Mindig szabadon írható:
- `specs/backlog/`, `Plans/`, `docs/`;
- minden `*.md` fájl;
- a git által ignorált fájlok;
- a roadmap pipálása (`[ ]` → `[x]`).

Az olvasás soha nincs korlátozva.

### Kulcsszavak

Csak akkor számítanak, ha **a te üzeneted egy sorának elején** állnak. Így egy
agent-jelentésben idézett kulcsszó nem old fel semmit.

| Kulcsszó | Hatás |
|---|---|
| `#spec-szerkesztes` | Feloldja a constitutiont és a guard fájljait erre a sessionre |
| `#spec-zar` | Visszazárja (különben 12 óra után zár magától) |
| `#spec-ok` | Jóváhagyja az aktuális branch feature spec-jét, ettől kezdve írható a kód |

Példa: `#spec-szerkesztes a mission-ben egészítsd ki a célközönséget`

---

## Telepítés

### 1. A sablon és a `/sdd-init` parancs (gépenként egyszer)

```bash
git clone git@github.com:Hudiny27/claude-sdd-template.git ~/.claude/templates/sdd
mkdir -p ~/.claude/skills
cp -r ~/.claude/templates/sdd/claude-skill/sdd-init ~/.claude/skills/
```

Feltételek: `git`, `python3` (3.9+) és Claude Code. Más függőség nincs.

### 2. Projekt indítása

Üres (vagy meglévő) könyvtárban, Claude Code-ban:

```
/sdd-init
```

A skill megkérdezi, kell-e GitHub CI-ellenőrzés, lefuttatja a telepítőt,
megoldja az ütközéseket, és felajánlja a kezdő commitot.

Claude nélkül, shellből is működik:

```bash
bash ~/.claude/templates/sdd/install.sh [CÉLKÖNYVTÁR] [--with-ci]
```

### 3. Újraindítás és indulás

1. **Indítsd újra a Claude Code-ot** a projektben, mert a hookok és a skillek
   a session indulásakor töltődnek be. A session elején megjelenő
   *„SDD status”* jelzi, hogy aktívak.
2. Futtasd: `/constitution`

### A telepítő viselkedése

- **Nem ír felül semmit.** Ha már van `CLAUDE.md`, a szabályok
  `CLAUDE.sdd.md` néven kerülnek mellé. Ezt egy `@CLAUDE.sdd.md` sorral
  töltheted be.
- Ha még nincs git repó, létrehozza (`main` branch). Ha a cél egy **másik
  repón belül** van, nem fut le.
- Beállítja a `core.hooksPath=.githooks` értéket, és a `.gitignore` végére
  hozzáfűzi a helyi állapotfájlokat.
- A végén lefuttatja a guard 26 tesztjét a célprojektben.
- Újrafuttatva csak a hiányzó fájlokat pótolja.
- Ha már létezett `.claude/settings.json`, a hookokat **nem köti be
  automatikusan**. Ezt jelzi, és a `/sdd-init` felajánlja az összefésülést.

---

## Mit hoz létre a projektben?

```
CLAUDE.md                          # SDD-szabályok, workflow, kikényszerítés, kulcsszavak
specs/                             # constitution (hook-védett)
├── README.md                      # formátumok: mission, tech-stack, roadmap
└── backlog/                       # kutatások, ötletek (szabadon írható)
Plans/                             # feature spec-ek
├── README.md                      # formátumok és életciklus
└── done/                          # lezárt feature-ök
.claude/
├── settings.json                  # hookok bekötése
├── hooks/sdd_guard.py             # a guard
├── hooks/test_sdd_guard.py        # regressziós tesztek
└── skills/                        # constitution, feature-spec, validate-feature, replan
.githooks/pre-commit               # agent-független védőháló
.github/workflows/sdd-check.yml    # csak --with-ci esetén
```

Elnevezési szabály: a `feature/phase-2-agents` branch spec-je a
`Plans/ÉÉÉÉ-HH-NN-phase-2-agents/` mappa. A spec-et a guard, a pre-commit és a
CI is a branchnév utolsó tagja alapján találja meg.

## A repó tartalma

| Útvonal | Szerep |
|---|---|
| `install.sh` | Determinisztikus, idempotens telepítő |
| `files/` | A projektbe másolt fájlok |
| `files/gitignore` | A `.gitignore`-hoz fűzött sorok |
| `claude-skill/sdd-init/` | A globális `/sdd-init` skill (a `~/.claude/skills/` alá kell másolni) |

---

## Korlátok: mit nem tud garantálni?

- **A hook nem látja**, ha egy program magától ír fájlt (npm, kódgenerátor,
  formázó), és azt sem, ha az írás változók mögé van rejtve. Ezeket a git
  pre-commit hook a commitnál fogja meg.
- A Claude Code-hookok csak Claude Code-ban működnek. Más agentnél a
  pre-commit és a CI véd.
- **Helyben megkerülhetetlen garanciát** csak a szerveroldali CI ad, ha a
  GitHubon branch protectionnel kötelezővé teszed a `spec-sync` ellenőrzést.
- A minőségi szabályokat (az interjú alapossága, a spec részletessége, a
  review mélysége) a `CLAUDE.md` és a skillek írják le. Ezek betartását a te
  review-d biztosítja.

## Beépített tanulságok (egy korábbi PRD-guard üzemeltetéséből)

- Nincs Stop hook, mert az subagentek befejezésekor is lefut, és munka
  közben zárta vissza a feloldást.
- A kulcsszó nélküli üzenet soha nem változtat a záron.
- Az interpreter-ellenőrzés soronként vizsgál, így egy szkript, ami csak
  megemlít egy védett útvonalat, nem akad fenn.
- Kulcsszó csak sor elején számít, mert egy idézett kulcsszó egy
  agent-jelentésben különben feloldaná a zárat.
- A `settings.local.json` is védett, mert a `disableAllHooks` beállítással
  minden hook kikapcsolható volna.

## A sablon karbantartása

A `files/` alatti fájlokat szerkeszd, utána futtasd a teszteket:

```bash
cd ~/.claude/templates/sdd/files && python3 -m unittest discover -s .claude/hooks -p 'test_*.py'
```

A már telepített projektek **nem frissülnek maguktól**. Egy módosított
`sdd_guard.py`-t kézzel másolj át. A projektben ez a fájl zárolt, ezért előtte
oldd fel a `#spec-szerkesztes` kulcsszóval.
