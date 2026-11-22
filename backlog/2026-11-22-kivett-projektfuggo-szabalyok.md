# A sablonból kivett projektfüggő szabályok (2026-11-22)

Az átalakítás 1. szakasza (`2026-11-22-sablon-atalakitas-terv.md`) kivette a
sablonból azt a 14 szabályt, amelyet az átvilágítás
(`2026-11-22-sablon-atvilagitas.md`) projektfüggőnek sorolt be. A pii-pajzsban
élő megfelelőjük érintetlen marad; a projekt átállásakor ezek a projekt
bővítési pontjaira kerülnek (`.claude/rules/`, `.claude/project.md`, a projekt
saját scriptjei és tesztjei). A szöveg a sablon git-történetéből
visszanyerhető.

| # | Szabály (rövidítve) | Honnan | Hova tartozna |
|---|---|---|---|
| C28 | Amíg a tesztkör a háttérben fut, legfeljebb olvass és tervezz | `CLAUDE.md`, Implementáció | pii-pajzs `.claude/project.md` (hosszú tesztkör) |
| C41 | A prototípus scriptjei a `specs/backlog/prototype/` alá menthetők, a lint alól fájlszinten kivéve | `CLAUDE.md`, Prototípus | pii-pajzs `.claude/rules/` (`paths: specs/backlog/prototype/**`), a ruff-kivétellel együtt |
| P16 | Ha a mért érték constitution-beli számot változtat, a constitution ugyanabban a csoportban frissül | `Plans/README.md`, Kalibrálás | pii-pajzs `.claude/rules/` (`paths: Plans/**`) |
| P25 | A „tiltva” vagy hibaállapot teszt a megjelenő okot is ellenőrzi; a hibát nem újrapróbált válasszal váltja ki | `Plans/README.md`, validate.sh | webes felületű projekt `.claude/rules/` (a felület tesztjeire), vagy a `verify-web` skill |
| P26 | A „soha” állítás tesztje a művelet után azonnal, újrapróbálás nélkül mér, utána a végállapotot | `Plans/README.md`, validate.sh | webes felületű projekt `.claude/rules/` (Playwright auto-wait csapda) |
| P37 | A nehéz lépések memóriakorláttal futnak, ha a tech-stack előírja | `Plans/README.md` és `feature-spec` (F38), validate.sh | pii-pajzs `.claude/rules/` (`paths: Plans/**/validate.sh`), WSL memóriakorlát |
| P40 | Szándékos rontásra épülő próbánál a rontást és mellékhatásait előre le kell írni | `Plans/README.md`, Friss subagent-próba | video-tutorial vagy pii-pajzs `.claude/rules/` a próbákhoz |
| F15 | Meglévő felület másolásakor előbb a viselkedését és állapotait írd le, az eltéréseket az interjúba | `feature-spec`, 3. lépés | felületet másoló projekt `.claude/project.md`-je, vagy egy UI skill |
| F18 | Mért CI- vagy felhőkvóta (GitHub Actions perc, felhőszámla) ellenőrzése az interjú előtt | `feature-spec`, 3. lépés | GitHub Actionst használó projekt `.claude/rules/` (`paths: .github/workflows/**`) |
| F19 | `workflow_dispatch` csak a default branchen lévő fájllal indítható: korai merge vagy push-indítás a tervben | `feature-spec`, 3. lépés | GitHub Actionst használó projekt `.claude/rules/` (`paths: .github/workflows/**`) |
| F24 | A spec által rögzített mért érték (hash, cache-kulcs, darabszám) megnevezi a pontos bemenetét | `feature-spec`, 4. lépés | pii-pajzs `.claude/rules/` (`paths: Plans/**`) |
| F28 | Időkorlátot mérő teszt bukás előtt néhányszor újramér (terhelt vagy virtualizált gép) | `feature-spec`, 4. lépés | pii-pajzs tesztsegédje (kód), terhelt WSL/DGX gép |
| F29 | A „nem történik meg” ígéret OS-szintű nyomkövetéssel ellenőrizve, egy megengedett eseménnyel | `feature-spec`, 4. lépés | pii-pajzs tesztjei (strace, adatvédelmi ígéret) és `.claude/rules/` |
| F42 | A `validate.sh` `--live` részét spec-íráskor egyszer lefuttatni, ha csak olvassa a telepített példányt | `feature-spec`, 4. lépés | pii-pajzs `.claude/rules/` (`paths: Plans/**/validate.sh`), DGX tesztpéldány |
