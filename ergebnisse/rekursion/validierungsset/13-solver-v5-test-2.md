# Solver v5 Test 2: Minimum mit negativen Zahlen (sollte FAILEN bei π₀)

## Eingabe

```python
[-5, -2, -10, 0]
```

## Erwartete Ausgabe (korrekt)

```python
-10
```

## Tatsächliches Ergebnis des buggy Solvers

```python
-5
```

## Kommentar

- Erwartet: Echtes Minimum (-10)
- Aktuell: Erstes Element (-5) → vergleicht nicht
- Pass: falls Ergebnis exakt `-10` ist
- Fail: falls Ergebnis `-5` ist (so wie aktuell)
