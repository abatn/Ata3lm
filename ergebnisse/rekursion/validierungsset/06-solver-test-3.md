# Solver-Test 3: Edge Cases (leere Liste und einzelne Element)

## Eingabe

```python
[]
```

## Erwartete Ausgabe (korrekt)

```python
[]
```

## Eingabe

```python
[42]
```

## Erwartete Ausgabe (korrekt)

```python
[42]
```

## Kommentar

- Erwartet: Sortierung von Edge Cases (leere Liste, einzelnes Element)
- Bewerten: Prüfen Sie beide Szenarien
- Pass: falls `solver.sortiere_zahlen([]) == []` UND `solver.sortiere_zahlen([42]) == [42]`
- Fail: falls eine der beiden Assertionen fehlschlägt

## Test ausführen

```python
from solver import sortiere_zahlen

# Test 1: Leere Liste
result1 = sortiere_zahlen([])
expected1 = []
assert result1 == expected1, f"Test 1 fehlgeschlagen: {result1} != {expected1}"

# Test 2: Einzelnes Element
result2 = sortiere_zahlen([42])
expected2 = [42]
assert result2 == expected2, f"Test 2 fehlgeschlagen: {result2} != {expected2}"

print("✅ Alle Edge-Case-Tests bestanden!")
```