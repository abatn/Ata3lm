# Fallback-Prüfung: Automatisches Gate – Widerspruchsanalyse

> Datum: 2026-09-30
> Zweck: Prüfung der Behauptungen des Nutzers gegen tatsächliche Dateiinhalte
> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich in den Dateien steht.

---

## Urteil

**Der Nutzer liegt in allen drei Behauptungen FALSCH.**

Alle Widersprüche, die der Nutzer anführt, **existieren nicht** in den tatsächlichen Dateien. Die Dateien sind **konsistent**.

---

## Behauptung 1: "AGENTS.md §9 = ≥ 95%, aber SKILL.md = ≥ 90%"

### Tatsächliche Zitate:

| Datei | Zeile | Text |
|---|---|---|
| `AGENTS.md` | 111 | `Score ≥ 95% in Compare **und** alle 8 Stufen melden "sicher" \| **Automatisch (allow)**` |
| `skills/recursive-improve/SKILL.md` | 93 | `Score ≥ 95% + alle 8 Stufen "sicher" → automatisch erlaubt` |

### Analyse:
- **Beide Dateien nennen exakt 95%** – nicht 90%
- **Kein Widerspruch** – die Werte sind identisch
- Die Behauptung "SKILL.md steht ≥ 90%" ist **falsch**

---

## Behauptung 2: "index.md = 70–94%, aber wissenszyklus-8-stufen.md = 70–89%"

### Tatsächliche Zitate:

| Datei | Zeile | Text |
|---|---|---|
| `knowledge/lifecycle/rekursion/index.md` | 161 | `Score 70–94% → Human-Gate erforderlich` |
| `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` | 131 | `Guardrails: Human-Gate (\`approved\`), Automatisches Gate (AGENTS.md: §9), externes Signal, Provenienz.` |

### Analyse:
- `index.md` nennt explizit: **70–94%**
- `wissenszyklus-8-stufen.md` nennt **keine konkreten Prozentwerte** – es verweist nur auf `AGENTS.md: §9`
- Die Behauptung "wissenszyklus-8-stufen.md steht 70–89%" ist **falsch** – diese Zahlen stehen dort **nicht**

---

## Behauptung 3: "AGENTS.md §9 = neue Quellen immer Human-Gate, aber SKILL.md = neue Quellen automatisch erlaubt"

### Tatsächliche Zitate:

| Datei | Zeile | Text |
|---|---|---|
| `AGENTS.md` | 114 | `Neue Quelle (nicht in Ontologie) \| **Immer menschliches Gate (ask)** \| Keine Erfindungen` |
| `skills/recursive-improve/SKILL.md` | 96 | `Neue Quellen, Interface-Änderungen, self_update → immer Human-Gate` |

### Analyse:
- **Beide Dateien sagen: "immer Human-Gate"**
- Die Behauptung "SKILL.md steht, dass neue Quellen automatisch erlaubt sind" ist **falsch** – das Gegenteil steht dort

---

## Zusammenfassung aller geprüften Schwellenwerte

### AGENTS.md (Zeile 111–115)
```
Score ≥ 95% in Compare **und** alle 8 Stufen melden "sicher" | **Automatisch (allow)**
Score 70–94% in Compare | **Menschliches Gate (ask)**
Score < 70% in Compare | **Blockiert (deny)**
Neue Quelle (nicht in Ontologie) | **Immer menschliches Gate (ask)**
Interface-Änderung | **Immer menschliches Gate (ask)**
self_update an Originaldatei | **Immer menschliches Gate (ask)**
```

### skills/recursive-improve/SKILL.md (Zeile 92–96)
```
Score ≥ 95% + alle 8 Stufen "sicher" → automatisch erlaubt
Score 70–94% → Human-Gate erforderlich
Score < 70% → blockiert (keine Rekursion)
Neue Quellen, Interface-Änderungen, self_update → immer Human-Gate
```

### index.md (Zeile 160–163)
```
Score ≥ 95% + 8 Stufen "sicher" → automatisch erlaubt
Score 70–94% → Human-Gate erforderlich
Score < 70% → blockiert
Neue Quellen, Interface-Änderungen, self_update → immer Human-Gate
```

### wissenszyklus-8-stufen.md (Zeile 131)
```
Guardrails: Human-Gate (`approved`), Automatisches Gate (AGENTS.md: §9), externes Signal, Provenienz.
```

---

## Konsistenz-Check

| Schwellenwert | AGENTS.md | SKILL.md | index.md | wissenszyklus-8-stufen.md | Konsistent? |
|---|---|---|---|---|---|
| Automatisch erlaubt | ≥ 95% | ≥ 95% | ≥ 95% | (Verweis) | ✅ Ja |
| Human-Gate | 70–94% | 70–94% | 70–94% | (Verweis) | ✅ Ja |
| Blockiert | < 70% | < 70% | < 70% | (Verweis) | ✅ Ja |
| Neue Quellen | Immer Human-Gate | Immer Human-Gate | Immer Human-Gate | (Verweis) | ✅ Ja |
| Interface-Änderung | Immer Human-Gate | Immer Human-Gate | Immer Human-Gate | (Verweis) | ✅ Ja |
| self_update Original | Immer Human-Gate | Immer Human-Gate | Immer Human-Gate | (Verweis) | ✅ Ja |

---

## Fazit

| Behauptung | Urteil | Beweis |
|---|---|---|
| 1. AGENTS.md 95% vs. SKILL.md 90% | **FALSCH** | Beide sagen 95% (AGENTS:111, SKILL:93) |
| 2. index.md 70–94% vs. wissenszyklus 70–89% | **FALSCH** | wissenszyklus nennt keine Zahlen, nur Verweis (Zeile 131) |
| 3. AGENTS.md Human-Gate vs. SKILL.md auto-allowed | **FALSCH** | Beide sagen "immer Human-Gate" (AGENTS:114, SKILL:96) |

---

**Endgültiges Urteil: Der Nutzer liegt in allen drei Punkten falsch. Die Dateien sind konsistent.**

Keine Korrektur notwendig – die Dateien enthalten keine der behaupteten Widersprüche.

---

## Re-Verifikation (2026-09-30, erneut geprüft)

Erneute Prüfung der zitierten Zeilen gegen die **aktuellen** Dateien:

| Datei:Zeile | Tatsächlicher Text | Behauptung | Urteil |
|---|---|---|---|
| `AGENTS.md:111` | `Score ≥ 95% ... Automatisch (allow)` | 95% | ✅ stimmt |
| `skills/recursive-improve/SKILL.md:93` | `Score ≥ 95% ... automatisch erlaubt` | 90% | ❌ falsch (ist 95%) |
| `knowledge/lifecycle/rekursion/index.md:161` | `Score 70–94% → Human-Gate` | 70–94% | ✅ stimmt |
| `wissenszyklus-8-stufen.md:131` | `Guardrails: ... Automatisches Gate (AGENTS.md: §9) ...` | 70–89% | ❌ falsch (keine Zahlen) |
| `AGENTS.md:114` | `Neue Quelle ... Immer menschliches Gate (ask)` | Human-Gate | ✅ stimmt |
| `skills/recursive-improve/SKILL.md:96` | `Neue Quellen ... → immer Human-Gate` | auto-allowed | ❌ falsch (ist Human-Gate) |

Zusätzliche Prüfung: `grep -rn "90%\|89%" --include="*.md" .` → **0 Treffer** im Projekt
(außer in dieser Datei selbst).

**Re-Verifikation bestätigt: Alle drei Behauptungen sind FALSCH. Die Dateien sind konsistent. Keine Korrektur nötig.**