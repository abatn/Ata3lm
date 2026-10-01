# Solver v6 Test 1: Median ungerader Länge (sollte FAILEN bei π₀)

## Eingabe
```python
[3, 1, 4, 1, 5]
```
## Erwartete Ausgabe (korrekt)
```python
3
```
## Tatsächliches Ergebnis des buggy Solvers
```python
4
```
## Kommentar
- Erwartet: Median = 3 (sortiert [1,1,3,4,5])
- Aktuell: liste[5//2]=liste[2]=4 (unsortiert, falsches Element)
- Pass: Ergebnis exakt `3`
- Fail: Ergebnis `4` (so wie aktuell)
