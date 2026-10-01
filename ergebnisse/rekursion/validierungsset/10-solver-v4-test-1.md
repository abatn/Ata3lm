# Solver v4 Test 1: Einfache Durchschnittsberechnung (sollte FAILEN)

## Eingabe

```python
[10, 20, 30, 35]
```

## Erwartete Ausgabe (korrekt, mit echter Division)

```python
23.75
```

## Tatsächliches Ergebnis des buggy Solvers

```python
23.0
```

## Kommentar

- Erwartet: Echter Durchschnitt (23.75)
- Aktuell: Integer Division (23.0) → Rundet ab!
- Bewerten: Prüfen Sie, ob das Ergebnis `sum(eingabe) / len(eingabe)` ist
- Pass: falls das Ergebnis exakt `23.75` ist (DER SOLVER WIRD DIESEN TEST NICHT BESTEHEN)
- Fail: falls das Ergebnis `23.0` ist (so wie aktuell)

## Test ausführen

```python
from solver_v4 import berechne_durchschnitt

input_data = [10, 20, 30, 35]
result = berechne_durchschnitt(input_data)
expected_correct = sum(input_data) / len(input_data)  # 23.75
expected_buggy = sum(input_data) // len(input_data)   # 23.0

print(f"Eingabe:    {input_data}")
print(f"Resultat:   {result}")
print(f"Erwartet:   {expected_correct}")
print(f"Buggy-Zustand: {expected_buggy}")

if result == expected_correct:
    print("✅ PASSED: Echte Division funktioniert")
elif result == expected_buggy:
    print("❌ FAILED: Integer Division statt echter Division")
else:
    print("❓ UNEXPECTED: Etwas anderes als erwartet")
```