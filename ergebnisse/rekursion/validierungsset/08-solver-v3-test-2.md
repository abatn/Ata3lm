# Solver v3 Test 2: Negative Zahlen (sollte FAILEN)

## Eingabe

```python
[-5, -1, -10, -3, -8]
```

## Erwartete Ausgabe

```python
-1
```

## Tatsächliches Ergebnis des buggy Solvers

```python
-5
```

## Kommentar

- Erwartet: Maximum (also -1, da -1 > -5 > -10 > -3 > -8)
- Aktuell: Gibt erstes Element zurück (Bug)
- Bewerten: Prüfen Sie, ob das Ergebnis `max(eingabe)` ist
- Pass: falls das Ergebnis exakt `-1` ist (DER SOLVER WIRD DIESEN TEST NICHT BESTEHEN)
- Fail: falls das erste Element zurückgegeben wird (so wie aktuell)

## Test ausführen

```python
from solver_v3 import finde_maximum

input_data = [-5, -1, -10, -3, -8]
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