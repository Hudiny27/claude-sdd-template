# Calibration

A number the agent picks that depends on real data (a threshold, a time
limit, a rate) is marked „kalibrálandó” in its decision. `plan.md` measures
it on live samples in the task group that introduces it, not only in the
final manual check.

The result goes to the "Kalibrálás" section of `requirements.md` (S/M: of
`spec.md`), one subsection per value (or group of values that belong
together), always in this order:

```markdown
### <érték(ek)> (<n>. csoport)
- Minta: <min mért, milyen adaton, milyen beállítással>
- Söprés: | <paraméter> | <eredmény 1> | <eredmény 2> | (a kipróbált értékek és amit mértek)
- Választás: <érték>: <miért ez; mekkora a tartalék a határig>
- Ellenőrzés: <melyik teszt vagy élő teszt őrzi>
```
