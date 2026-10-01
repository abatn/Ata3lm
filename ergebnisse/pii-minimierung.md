# PII-Minimierung: PII löschen statt markieren

> Datum: 2026-10-01
> Status: **Belegt** (Datenminimierung) + **Auftrag** (Implementierung)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/trust.py`

## 0. Quellen-Korrekturen (wichtig)

Der Auftrag nennt zwei Quellen, die die Sache **nicht** belegen:

1. **„EU-KI-Verordnung Artikel 5 (Datenminimierung)" — falsch.**
   Art. 5 der EU-KI-VO (VO (EU) 2024/1689) regelt **verbotene Praktiken**
   (subliminale Manipulation, Social Scoring, biometrische Kategorisierung …),
   **nicht** Datenminimierung. Datenminimierung steht in **DSGVO Art. 5(1)(c)**
   („adequate, relevant and limited to what is necessary … (data minimisation)").
   Die EU-KI-VO verlangt Minimierung/Löschung personenbezogener Daten in
   **Art. 10(5)** („minimising personal data by using synthetic and anonymous
   data … an obligation to delete the data if the purpose … is fulfilled").

2. **„SAVANT … zur feineren Isolation sensibler Informationen" — nicht belegt.**
   SAVANT (Sousa, 2026, Zenodo-Preprint): „Sparse Adaptive Vector Alignment for
   **Continual Learning and Persistent Agent Safety**" — behandelt
   Continual-Learning-Sicherheit / Poisoning (CALMS-SAVANT: geometrische
   Validierung, Byzantine-robuste Initialisierung, Cognitive Diode, PPP-Bench),
   **nicht** PII-Isolation. → Wird **nicht** als PII-Mechanismus ausgegeben.

## 1. Quellen (verifiziert, HTTP 200)

| Quelle | Kernaussage | Link |
|---|---|---|
| **DSGVO Art. 5(1)(c)** | „adequate, relevant and **limited to what is necessary** … (**data minimisation**)" | https://gdpr-info.eu/art-5-gdpr/ |
| **EU-KI-VO Art. 10(5)** | personenbezogene Daten **minimieren** (synthetisch/anonym, Pseudonymisierung) + **löschen**, wenn der Zweck erfüllt ist | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| **EU-KI-VO Art. 5** | *verbotene Praktiken* (nicht Datenminimierung) – zur Abgrenzung | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| **SAVANT** (Sousa 2026) | Continual-Learning-/Poisoning-Sicherheit (nicht PII) – zur Abgrenzung | Zenodo-Preprint 2026-05-18 |

## 2. Umsetzung: Löschen statt markieren

- **Vorher:** `anonymize()` ersetzte PII durch `[PII:<typ>]` (Markierung).
- **Nachher:** `minimize()` **entfernt** den PII-Span vollständig; der übrige
  Text bleibt („sparse": nur sensible Spans). `anonymize` = Alias (löscht ebenfalls).
- Begründung (belegt): Datenminimierung = nur das Nötige halten (DSGVO 5(1)(c));
  Löschen, wenn nicht nötig (EU-KI-VO 10(5)).

## 3. Selbsttest (reale Ausgabe) — 3 PII-Fälle

```text
=== [1] Privacy: PII-Minimierung – PII wird GELÖSCHT (DSGVO Art. 5(1)(c)) ===
  vorher : Kontakt: max.mustermann@example.com bitte melden
  erkannt: ['email']  -> nachher: 'Kontakt: bitte melden'
  vorher : Ruf mich an: +49 30 1234567
  erkannt: ['phone']  -> nachher: 'Ruf mich an:'
  vorher : IBAN DE89370400440532013000 überweisen
  erkannt: ['iban', 'phone']  -> nachher: 'IBAN überweisen'
```

**Ergebnis:** In allen 3 Fällen wird PII **gelöscht** (kein `[PII:…]`-Marker);
der Kontext bleibt erhalten.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| Datenminimierung: nur Nötiges halten | **Belegt** (DSGVO Art. 5(1)(c)) |
| Personenbezogene Daten minimieren/löschen | **Belegt** (EU-KI-VO Art. 10(5)) |
| „EU-KI-VO Art. 5 = Datenminimierung" | **widerlegt** (Art. 5 = verbotene Praktiken) |
| „SAVANT = PII-Isolation" | **nicht belegt** (SAVANT = Continual-Learning-Sicherheit) |
| `minimize()`-Implementierung (Regex, sparse) | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/trust.py` | erweitert (`minimize`, Löschung) |
| `ergebnisse/pii-minimierung.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/022-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://gdpr-info.eu/art-5-gdpr/ (DSGVO Art. 5(1)(c))
- https://eur-lex.europa.eu/eli/reg/2024/1689/oj (EU-KI-VO Art. 5 / Art. 10(5))
