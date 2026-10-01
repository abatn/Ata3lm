# Validierungsset für Rekursions

> Erstellt: 2026-09-30
> Zweck: Externes Signal für Compare-Phase nach Gödel-Agent-Muster
> Aktualisiert: t=2 mit echten Solver-Testfällen

## Testfälle für t=1 (Struktur-Check)

| # | Datei | Beschreibung | Kriterium |
|---|---|---|---|
| 1 | `01-struktur-check.md` | Alle 8 Lifecycle-Phasen + 8 Skills existieren | 16/16 Dateien = passed |
| 2 | `02-connector-reference.md` | Alle 9 Connectoren in 3 Kern-Dateien | 3/3 Dateien = passed |
| 3 | `03-quellen-link-check.md` | Quellen-Links erreichbar (HTTP 200) | >= 80 % = passed |

## Testfälle für t=2 (Echte Solver-Tests)

| # | Datei | Beschreibung | Kriterium |
|---|---|---|---|
| 4 | `04-solver-test-1.md` | Einfache Sortierung ohne Duplikate | Sortiert = passed |
| 5 | `05-solver-test-2.md` | Sortierung + Deduplizierung | Dedupliziert = passed |
| 6 | `06-solver-test-3.md` | Edge Cases (leer, einzelnes Element) | Beider funktioniert = passed |

## Testfälle für t=3 (finde_maximum)

| # | Datei | Beschreibung | Kriterium |
|---|---|---|---|
| 7 | `07-solver-v3-test-1.md` | Maximum von positiven Zahlen | max = passed |
| 8 | `08-solver-v3-test-2.md` | Maximum von negativen Zahlen | max = passed |
| 9 | `09-solver-v3-test-3.md` | Edge Cases (leer, einzelnes Element) | Edge Cases = passed |

## Testfälle für t=4 (berechne_durchschnitt)

| # | Datei | Beschreibung | Kriterium |
|---|---|---|---|
| 10 | `10-solver-v4-test-1.md` | Durchschnitt von positiven Zahlen | echter Durchschnitt = passed |
| 11 | `11-solver-v4-test-2.md` | Durchschnitt mit kleinen Zahlen | echter Durchschnitt = passed |

## Ausführung

Jeder Testfall wird von der `Compare`-Phase gegen das aktuelle Modell (π) ausgeführt.
Das Ergebnis ist ein Score 0/3, 1/3, 2/3 oder 3/3.

## Guardrails

- Kein rein internes Scoring (Prinzip 6)
- Compare muss auf verifizierbares Signal zugreifen (Dateisystem, HTTP)
- Ergebnis wird in `008-t1-rekursion.md` dokumentiert
