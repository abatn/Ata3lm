# Solver v3 Test 3: Edge Cases (leere Liste, einzelnes Element - sollte für Edge Cases bestehen)

## Eingabe 1: Leere Liste

```python
[]
```

## Erwartete Ausgabe

```python
None
```

## Eingabe 2: Einzelnes Element

```python
[42]
```

## Erwartete Ausgabe

```python
42
```

## Kommentar

- Erwartet: Korrekte Behandlung von Edge Cases
- Bewerten: Prüfen Sie beide Szenarien
- Pass: falls `solver.finde_maximum([]) is None` UND `solver.finde_maximum([42]) == 42`
- Fail: falls eine der beiden Assertionen fehlschlägt

## Test ausführen

```python
from solver_v3 import finde_maximum

# Test 1: Leere Liste
result1 = finde_maximum([])
expected1 = None
print(f"Leere Liste: {result1} (erwartet: None) -> {\"✅ PASS\" if result1 is None else \"❌ FAIL\"}")

# Test 2: Einzelnes Element
result2 = finde_maximum([42])
expected2 = 42
print(f"Einzelnes Element: {result2} (erwartet: 42) -> {\"✅ PASS\" if result2 == 42 else \"❌ FAIL\"}")

if result1 is None and result2 == 42:
    print("✅ Alle Edge-Case-Tests bestanden!")
else:
    print("❌ Ein Edge-Case-Test fehlgeschlagen")
```