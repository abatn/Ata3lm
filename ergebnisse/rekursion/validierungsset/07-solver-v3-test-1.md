# Solver v3 Test 1: Positive Zahlen (sollte FAILEN)

## Eingabe

```python
[3, 1, 4, 1, 5, 9, 2, 6]
```

## Erwartete Ausgabe

```python
9
```

## Tatsächliches Ergebnis des buggy Solvers

```python
3
```

## Kommentar

- Erwartet: Maximum der Liste
- Aktuell: Gibt erstes Element zurück (Bug)
- Bewerten: Prüfen Sie, ob das Ergebnis `max(eingabe)` ist
- Pass: falls das Ergebnis exakt `9` ist (DER SOLVER WIRD DIESEN TEST NICHT BESTEHEN)
- Fail: falls das erste Element zurückgegeben wird (so wie aktuell)

## Test ausführen

```python
from solver_v3 import finde_maximum

input_data = [3, 1, 4, 1, 5, 9, 2, 6]
result = finde_maximum(input_data)
expected = max(input_data)

print(f"Eingabe:    {input_data}")
print(f"Resultat:   {result}")
print(f"Erwartet:   {expected}")

if result == expected:
    print("✅ PASSED: Maximum korrekt gefunden")
else:
    print("❌ FAILED: Gibt erstes Element zurück statt Maximum")
```