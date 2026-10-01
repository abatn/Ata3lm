# Solver v4 Test 2: Einfacher Fall mit gebrochenem Ergebnis (sollte FAILEN)

## Eingabe

```python
[1, 2]
```

## Erwartete Ausgabe (korrekt, mit echter Division)

```python
1.5
```

## Tatsächliches Ergebnis des buggy Solvers

```python
1
```

## Kommentar

- Erwartet: Echter Durchschnitt (1.5)
- Aktuell: Integer Division (1) → Rundet ab!
- Bewerten: Prüfen Sie, ob das Ergebnis `sum(eingabe) / len(eingabe)` ist
- Pass: falls das Ergebnis exakt `1.5` ist (DER SOLVER WIRD DIESEN TEST NICHT BESTEHEN)
- Fail: falls das Ergebnis `1` ist (so wie aktuell)

## Test ausführen

```python
from solver_v4 import berechne_durchschnitt

input_data = [1, 2]
result = berechne_durchschnitt(input_data)
expected_correct = sum(input_data) / len(input_data)  # 1.5
expected_buggy = sum(input_data) // len(input_data)   # 1

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