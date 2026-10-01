# Solver v6 Test 2: Median gerader Länge (sollte FAILEN bei π₀)

## Eingabe
```python
[1, 2, 3, 4]
```
## Erwartete Ausgabe (korrekt)
```python
2.5
```
## Tatsächliches Ergebnis des buggy Solvers
```python
3
```
## Kommentar
- Erwartet: Median = 2.5 (Mittelwert der beiden mittleren 2 und 3)
- Aktuell: liste[4//2]=liste[2]=3 (kein Mittelwert)
- Pass: Ergebnis exakt `2.5`
- Fail: Ergebnis `3` (so wie aktuell)
