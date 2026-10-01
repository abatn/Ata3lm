# Solver v5 Test 1: Minimum positiver Zahlen (sollte FAILEN bei π₀)

## Eingabe

```python
[3, 1, 4, 1, 5]
```

## Erwartete Ausgabe (korrekt)

```python
1
```

## Tatsächliches Ergebnis des buggy Solvers

```python
3
```

## Kommentar

- Erwartet: Echtes Minimum (1)
- Aktuell: Erstes Element (3) → vergleicht nicht
- Pass: falls Ergebnis exakt `1` ist
- Fail: falls Ergebnis `3` ist (so wie aktuell)
