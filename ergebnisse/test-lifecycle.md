# Test: Lifecycle & Skills

> Datum: 2026-09-30
> Zweck: Prüfung aller Lifecycle-Dateien und Skills (Existenz, Zeilen, Quellen-Links)
> Lab-Prinzip: Keine Erfindungen – nur tatsächliche Dateiinhalte.

---

## 1. Lifecycle-Dateien (`knowledge/lifecycle/*.md`)

| # | Datei | Existiert | Zeilen | Quellen-Links |
|---|---|---|---|---|
| 1 | `experience.md` | ✅ | 104 | 4 |
| 2 | `wissen.md` | ✅ | 87 | 3 |
| 3 | `gedaechtnis.md` | ✅ | 117 | 8 |
| 4 | `kognition.md` | ✅ | 118 | 6 |
| 5 | `nicht-kognition.md` | ✅ | 125 | 4 |
| 6 | `denken.md` | ✅ | 148 | 8 |
| 7 | `handeln.md` | ✅ | 112 | 3 |
| 8 | `wissen-plus.md` | ✅ | 117 | 4 |

**Ergebnis: 8/8 Lifecycle-Dateien vorhanden.** ✅

---

## 2. Skills (`skills/**/SKILL.md`)

> **Korrektur:** Die Aufgabe nennt „8 Skills". Tatsächlich gibt es **14 SKILL.md**
> (9 Haupt-Skills + 5 Sub-Skills unter `recursive-improve/`).

### Haupt-Skills (9)

| # | Datei | Existiert | Zeilen | Quellen-Links |
|---|---|---|---|---|
| 1 | `skills/act/SKILL.md` | ✅ | 52 | 3 |
| 2 | `skills/cognize/SKILL.md` | ✅ | 89 | 3 |
| 3 | `skills/collect-experience/SKILL.md` | ✅ | 55 | 4 |
| 4 | `skills/expand-knowledge/SKILL.md` | ✅ | 69 | 4 |
| 5 | `skills/non-cognitive/SKILL.md` | ✅ | 78 | 2 |
| 6 | `skills/recursive-improve/SKILL.md` | ✅ | 152 | 5 |
| 7 | `skills/reflect/SKILL.md` | ✅ | 93 | 7 |
| 8 | `skills/store-memory/SKILL.md` | ✅ | 78 | 4 |
| 9 | `skills/structure-knowledge/SKILL.md` | ✅ | 66 | 3 |

### Sub-Skills (5, unter `recursive-improve/`)

| # | Datei | Existiert | Zeilen | Quellen-Links |
|---|---|---|---|---|
| 1 | `skills/recursive-improve/akt/SKILL.md` | ✅ | 73 | 2 |
| 2 | `skills/recursive-improve/compare/SKILL.md` | ✅ | 67 | 2 |
| 3 | `skills/recursive-improve/konstrukt/SKILL.md` | ✅ | 98 | 3 |
| 4 | `skills/recursive-improve/observe/SKILL.md` | ✅ | 68 | 2 |
| 5 | `skills/recursive-improve/revise/SKILL.md` | ✅ | 70 | 3 |

**Ergebnis: 14/14 SKILL.md vorhanden** (Soll „8" der Aufgabe ist ungenau). ✅

---

## 3. Zusammenfassung

| Kategorie | Soll (Aufgabe) | Tatsächlich | Status |
|---|---|---|---|
| Lifecycle-Dateien | 8 | **8** | ✅ |
| Skills (SKILL.md) | 8 | **14** (9+5) | ⚠️ Soll ungenau |
| Skills mit Quellen-Links | — | **14/14** | ✅ |
| Lifecycle mit Quellen-Links | — | **8/8** | ✅ |

**Fazit:** Alle Lifecycle-Dateien und Skills existieren und enthalten Quellen-Links.
Die von der Aufgabe erwartete Skill-Zahl (8) weicht ab – tatsächlich 14 (verifiziert
mit `find skills -name "SKILL.md" | wc -l`).
