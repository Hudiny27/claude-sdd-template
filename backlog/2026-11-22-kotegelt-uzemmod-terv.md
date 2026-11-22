---
szint: L
allapot: tervezet
---
# Terv: kötegelt üzemmód

Állapot: nyitott: kikérdezés folyamatban.

Cél: az owner napi részvétele három rövid ablakba sűrűsödjön. Aktív ablak:
több feature kikérdezése és specje, egy köteg-jóváhagyás. Építő ablak:
felügyelet nélkül (éjjel) építés és validálás merge-kész állapotig. Döntési
ablak: reggel egy döntés feature-enként a mergéről. Az állomások (spec,
jóváhagyás, kapuk, review, merge-döntés) a mostani SDD-é maradnak; a mostani,
egyenkénti folyamat változatlanul megmarad mellette.

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
