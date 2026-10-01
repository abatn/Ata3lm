# 022 – PII-Minimierung (Löschen statt Markieren)

> Datum: 2026-10-01
> Rekursionstiefe: System-Iteration (Trust/Privacy), nicht Solver-t
> Phase: Revise (trust.py erweitert)
> Auslöser: menschlicher Auftrag vom 2026-10-01.

## 1. Zustand vorher / nachher

| Aspekt | vorher | nachher |
|---|---|---|
| PII-Behandlung | `[PII:<typ>]` (Markierung) | **gelöscht** (`minimize`) |

## 2. Änderungen

- `data/memory/trust.py`: `PIIFilter.minimize()` löscht PII-Spans (sparse);
  `anonymize` = Alias; Demo auf 3 PII-Fälle + Löschung umgestellt.
- `ergebnisse/pii-minimierung.md`.

## 3. Compare-Beleg (externes Signal)

`python3 data/memory/trust.py` (reale Ausgabe):
- `max.mustermann@example.com` → entfernt (`'Kontakt: bitte melden'`).
- `+49 30 1234567` → entfernt (`'Ruf mich an:'`).
- `IBAN DE89…3000` → entfernt (`'IBAN überweisen'`).
Kein `[PII:…]`-Marker mehr.

## 4. Quellen (belegt, HTTP 200)

- DSGVO Art. 5(1)(c) – Datenminimierung: https://gdpr-info.eu/art-5-gdpr/
- EU-KI-VO Art. 10(5) – personenbezogene Daten minimieren/löschen:
  https://eur-lex.europa.eu/eli/reg/2024/1689/oj

## 5. Quellen-Korrekturen (nicht belegt im Auftrag)

- „EU-KI-VO Art. 5 = Datenminimierung" → falsch (Art. 5 = verbotene Praktiken).
- „SAVANT = PII-Isolation" → nicht belegt (SAVANT = Continual-Learning-/Poisoning-Sicherheit).

## 6. Guardrails

- `AGENTS.md` unverändert; kein Löschen von Nicht-PII (nur sensible Spans).

## 7. Freigabe

**Freigabe-Status für π₁:** `approved: Batnini, 2026-10-01`.
