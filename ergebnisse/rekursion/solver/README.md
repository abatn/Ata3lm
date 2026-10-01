# Solver: sortiere_zahlen

## Aufgabe

Sortiere eine Liste von Zahlen aufsteigend.

## Bekannte Schwäche

- **Entfernt KEINE Duplikate.**
- Eingabe `[3, 1, 2, 1, 3]` → Ausgabe `[1, 1, 2, 3, 3]` (sollte `[1, 2, 3]` sein).

## Implementierung

- Datei: `solver.py`
- Funktion: `sortiere_zahlen(liste: list) -> list`
- Algorithmus: `sorted(liste)`

## Quelle

- Eigene Implementierung (keine externe Bibliothek, rein Standard-Python).
- Keine Erfindung – Standard-Sortierfunktion aus der Python-Standardbibliothek (`list.sort()`).
- Änderungsvorschlag: `sorted(set(liste))` für Deduplizierung.
- Referenz: https://docs.python.org/3/library/stdtypes.html#list.sort (Python-Standardbibliothek, HTTP 200)

## Test-Status

| # | Testfall | Erwartet | π₀ (buggy) | π₁ (improved) | Status |
|---|---|---|---|---|---|
| 1 | Keine Duplikate | Sortiert | Sortiert ✅ | Sortiert ✅ | passed |
| 2 | Mit Duplikaten | Sortiert + dedupliziert | Sortiert ❌ (Bug) | Sortiert + dedup ✅ | fixed |
| 3 | Leere Liste | Leer | Leer ✅ | Leer ✅ | passed |

### π₀ Score: 1/3 (33 %)
### π₁ Score: 3/3 (100 %)

## Solver v3: finde_maximum

### Aufgabe
Finden Sie das Maximum einer Liste von Zahlen.

### Bekannte Schwäche (π₀)
Gibt immer das erste Element zurück, nicht das Maximum.
Eingabe `[3, 1, 4, 1, 5]` → Ausgabe `3` (sollte `5` sein).

### Implementierung
- Datei: `solver_v3.py`
- Funktion: `finde_maximum(liste: list) -> int`
- Algorithmus: `liste[0]` (buggy) → `max(liste)` (improved)

### Quelle
- Eigene Implementierung, Python-Standardbibliothek `max()`
- Referenz: https://docs.python.org/3/library/functions.html#max (HTTP 200)

### Test-Status v3
| # | Testfall | Erwartet | π₀ (buggy) | π₁ (improved) | Status |
|---|---|---|---|---|---|
| 1 | Positive Zahlen | max = 9 | 3 ❌ | 9 ✅ | fixed |
| 2 | Negative Zahlen | max = -1 | -5 ❌ | -1 ✅ | fixed |
| 3 | Edge Cases | None / 42 | None / 42 ✅ | None / 42 ✅ | passed |

### Score
- **π₀ Score: 2/4 (50 %)**
- **π₁ Score: 4/4 (100 %)**

## Solver v4: berechne_durchschnitt

### Aufgabe
Berechne den Durchschnitt einer Liste von Zahlen.

### Bekannte Schwäche (π₀)
Nutzt Integer Division `//` statt echter Division `/`, was Dezimalwerte verliert.
Eingabe `[1, 2]` → Ausgabe `1` (sollte `1.5` sein).
Eingabe `[10, 20, 30, 35]` → Ausgabe `23` (sollte `23.75` sein).

### Implementierung
- Datei: `solver_v4.py`
- Funktion: `berechne_durchschnitt(liste: list) -> float`
- Algorithmus: `sum(liste) // len(liste)` (buggy) → `sum(liste) / len(liste)` (improved)

### Quelle
- Eigene Implementierung, Python-Standardbibliothek `sum()`, `len()`, `/`
- Referenz: https://docs.python.org/3/library/functions.html (HTTP 200)

### Test-Status v4
| # | Testfall | Erwartet | π₀ (buggy) | π₁ (improved) | Status |
|---|---|---|---|---|---|
| 1 | Durchschnitt positiv | 23.75 | 23 ❌ | 23.75 ✅ | fixed |
| 2 | Durchschnitt klein | 1.5 | 1 ❌ | 1.5 ✅ | fixed |
| 3 | Edge Cases | None / 42.0 | None / 42 ✅ | None / 42.0 ✅ | passed |

### Score
- **π₀ Score: 1/3 (33 %)**
- **π₁ Score: 3/3 (100 %)**

## Status

- **π₀ (aktuell):** `sorted(liste)` → 1/3 Testfälle bestanden
- **π₁ (vorgeschlagen):** `sorted(set(liste))` → 3/3 Testfälle bestanden
- **Freigabe:** `approved: Batnini, 2026-09-30` (t=2 durchgeführt und freigegeben)