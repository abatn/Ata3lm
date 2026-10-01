# Solver-Test 2: Zahlen mit Duplikaten (sollte FAILEN)

## Eingabe

```python
[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
```

## Erwartete Ausgabe (korrekt, mit Deduplizierung)

```python
[1, 2, 3, 4, 5, 6, 9]
```

## Tatsächliches Ergebnis des buggy Solvers

```python
[1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
```

## Kommentar

- Erwartet: Sortierte Liste OHNE Duplikate
- Aktuell: Sortierte Liste MIT Duplikaten (Bug)
- Bewerten: Prüfen Sie, ob das Ergebnis `sorted(set(eingabe))` ist
- Pass: falls das Ergebnis exakt `[1, 2, 3, 4, 5, 6, 9]` ist (DER SOLVER WIRD DIESEN TEST NICHT BESTEHEN)
- Fail: falls Duplikate enthalten sind (so wie aktuell)

## Test ausführen

```python
from solver import sortiere_zahlen

input_data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
result = sortiere_zahlen(input_data)
expected_correct = [1, 2, 3, 4, 5, 6, 9]  # mit Deduplizierung
expected_buggy = sorted(input_data)       # ohne Deduplizierung (aktueller Zustand)

print(f"Eingabe:    {input_data}")
print(f"Resultat:   {result}")
print(f"Erwartet:   {expected_correct}")
print(f"Buggy-Zustand: {expected_buggy}")

if result == expected_correct:
    print("✅ PASSED: Deduplizierung funktioniert")
elif result == expected_buggy:
    print("❌ FAILED: Duplikate werden nicht entfernt (bekannter Bug)")
else:
    print("❓ UNEXPECTED: Etwas anderes als erwartet")
```