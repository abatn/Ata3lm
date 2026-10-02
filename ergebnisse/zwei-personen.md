# Zwei-Personen-Verifikation für den approved-Flow

> Datum: 2026-10-01
> Status: **Belegt** (Zwei-Personen-Prinzip) + **Auftrag** (Anwendung)
> Prinzip: Keine Erfindungen (§6).
> Code: `data/memory/approval.py` · Gesetz: `AGENTS.md` §9.3

## 0. Quellen-Präzisierung

Der Auftrag nennt „EU-KI-VO Art. 14 (Hochrisiko-Szenarien)". Präzise:
- **Art. 14(1)–(4)** = **menschliche Aufsicht** (Human Oversight) allgemein für
  High-Risk-Systeme.
- **Art. 14(5)** enthält die **Zwei-Personen**-Pflicht — **aber nur** für
  High-Risk-Systeme nach **Annex III Punkt 1(a)** (Remote-Biometrie-Identifikation),
  mit **Ausnahme** (Law Enforcement, Migration, Grenzkontrolle, Asyl).

→ Das Zwei-Personen-Prinzip ist **belegt**, gilt laut Quelle aber **nicht** für
*alle* Hochrisiko-Szenarien. Die Anwendung auf **alle** Rekursionen ist
Projekt-Vorgabe (**Auftrag**).

## 1. Quelle (verifiziert, HTTP 200)

| Quelle | Kernaussage (wörtlich) | Link |
|---|---|---|
| **EU-KI-VO Art. 14(5)** | „no action or decision is taken … unless that identification has been **separately verified and confirmed by at least two natural persons** with the necessary competence, training and authority" (Ausnahme: Law Enforcement/Migration/Grenze/Asyl) | https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14 · https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| **EU-KI-VO Art. 14(1)–(4)** | menschliche Aufsicht: verstehen, Automation-Bias bewusst sein, interpretieren, überstimmen, stoppen | ebd. |

## 2. Flow

```text
pending ──(Person 1)──▶ first_approved ──(Person 2, distinkt)──▶ second_approved ──(finalize)──▶ approved
```

- **Mindestens zwei distinkte natürliche Personen** bestätigen.
- Dieselbe Person zählt nur **einmal** (distinkt erzwungen).
- `approved` erst nach **≥ 2** distinkten Personen.

## 3. Selbsttest (reale Ausgabe)

```text
=== Zwei-Personen-Verifikation (EU-KI-VO Art. 14(5)) ===
  Start          : {'state': 'pending', 'approvers': [], 'count': 0}
  approve(Batnini)     -> ok, state=first_approved
  approve(Batnini) x2  -> ok=False, "hat bereits bestätigt – zwei DISTINKTE Personen nötig"
  finalize (nur 1)     -> ok=False, "mind. 2 natürliche Personen erforderlich (aktuell 1)"
  approve(Verifier2)   -> ok, state=second_approved
  finalize (2 Personen)-> ok, state=approved
  Endstatus      : {'state': 'approved', 'approvers': ['Batnini','Verifier2'], 'count': 2}
```

**Ergebnis:** Flow `pending → first_approved → second_approved → approved`;
dieselbe Person kann nicht zweimal zählen; `approved` erst mit 2 Distinkten.

## 4. Status-Trennung

| Aussage | Status |
|---|---|
| „at least two natural persons" für Annex-III-1(a) | **Belegt** (Art. 14(5)) |
| Human Oversight allgemein | **Belegt** (Art. 14(1)–(4)) |
| Zwei-Personen für **alle** Rekursionen | **Auftrag** |
| State-Machine-Implementierung | **Auftrag** |

## 5. Dateien

| Artefakt | Art |
|---|---|
| `data/memory/approval.py` | neu (`TwoPersonApproval`) |
| `AGENTS.md` §9.3 | erweitert |
| `ergebnisse/zwei-personen.md` | neu (dieses Dokument) |
| `ergebnisse/rekursion/023-*.md` | Provenienz |

## 6. Quellen (HTTP 200, 2026-10-01)

- https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14
- https://eur-lex.europa.eu/eli/reg/2024/1689/oj

## 6. Nachtrag: Diff-Bindung fuer Verifier2 (2026-10-02)

Der Auftrag verlangt, dass **Verifier2 den Diff prueft und bestaetigt**. `approve()`
nimmt daher optional `diff_sha`:

```python
a.approve("Batnini",  diff_sha="abc123")   # first_approved
a.approve("Verifier2", diff_sha="abc123")  # second_approved (gleicher Diff)
a.finalize()                                # approved
```

- **Abweichender Diff** -> abgelehnt: "Diff stimmt nicht mit der ersten Freigabe ueberein".
- **Fehlender Diff** beim zweiten Verifizierer (erster hat einen) -> abgelehnt.
- `status()` liefert `diff_sha`; `history` protokolliert den Diff je Person (Evidence).

### Selbsttest (roh)

```text
make test -> 201 passed - 1753/1753 Statements - 396/396 Branches = 100,00 %

test_flow_zwei_verifizierer_mit_diff      : Batnini + Verifier2 (diff abc123) -> approved
test_diff_konflikt_wird_abgelehnt         : Verifier2 mit xyz999 -> ok=False, count=1
test_diff_fehlt_beim_zweiten_verifizierer : Verifier2 ohne Diff -> ok=False, count=1
```

### Quelle (HTTP 200, 2026-10-02)

https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689 -
https://artificialintelligenceact.eu/article/14/ -
https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-14
- woertlich: "separately verified and confirmed by at least two natural persons".
Scope-Kaveat unveraendert: Art. 14(5) gilt fuer Annex-III-1(a); die Anwendung auf alle
Rekursionen ist **Auftrag** (Abschnitt 0).
