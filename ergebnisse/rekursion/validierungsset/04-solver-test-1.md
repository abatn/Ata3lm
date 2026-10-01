# Solver-Test 1: Einfache sortierte Zahlen (sollte bestanden werden)

## Eingabe

```python
[5, 2, 8, 1, 9]
```

## Erwartete Ausgabe

```python
[1, 2, 5, 8, 9]
```

## Kommentar

- Erwartet: Standard-Sortierung ohne Duplikate
- Bewerten: Vergleichen Sie mit `solver.sortiere_zahlen([5, 2, 8, 1, 9])`
- Pass: falls die Ausgabe genau `[1, 2, 5, 8, 9]` ist
- Fail: sonst

## Test ausführen

```python
from solver import sortiere_zahlen

result = sortiere_zahlen([5, 2, 8, 1, 9])
expected = [1, 2, 5, 8, 9]
assert result == expected, f"Resultat {result} != Erwartet {expected}"
```