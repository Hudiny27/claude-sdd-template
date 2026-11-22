# Workflow-napló

A projekt helyi munkafolyamat-javításai. Minden javítás egy sort kap; a
`/replan` írja. A javítás a szabályhely-sorrend első működő fokára kerül:
`kód` (kód vagy ellenőrzés), `szabály` (`.claude/rules/`, útvonalhoz kötve),
`segédfájl` (egy lépés segédfájlja), `project.md` (mindig betöltve). A
sablon fájljai (`CLAUDE.md`, skillek, README-k, hookok) a projektben nem
változnak.

Az SDD-státusz számolja az utolsó `review:` sor óta felvett tételeket, és
10-nél review-t kér: a cél helyben rendet tenni. Minden tételről döntés
születik: kóddá vagy ellenőrzéssé alakítható-e, összevonható-e egy másikkal,
törölhető-e; az eredmény jellemzően kevesebb szöveg. A sablonba csak
szigorú kapun át kerülhet valami (lásd `/replan`). A review végén egy
`review: ÉÉÉÉ-HH-NN` sor kerül a lista végére, onnan indul újra a számolás.

Formátum: `- ÉÉÉÉ-HH-NN | fok | fájl | a szabály egy mondatban | eredet`

## Tételek
