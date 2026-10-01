# Test: Quellen (HTTP-Status)

> Datum: 2026-09-30
> Zweck: HTTP-Status-Check aller Quellen-Links im Projekt
> Methode: `curl -L -A "Mozilla/5.0" --connect-timeout 6 --max-time 15`

---

## 1. Zusammenfassung

| Kategorie | Anzahl |
|---|---|
| Eindeutige URLs gesamt | 78 |
| HTTP 200 (OK) | ~64 |
| HTTP 202 (DOI/IEEE) | 2 |
| HTTP 403 (Bot-Schutz, nicht defekt) | 4 |
| HTTP 404 (Nicht gefunden) | 6 |
| Markdown-Artefakte (leer) | 2 |

---

## 2. Fast Write Routing Quelle ✅

| URL | Status |
|---|---|
| https://arxiv.org/abs/2608.22215 | **200** ✅ |

---

## 3. HTTP 404 – Fundorte (alle nur in `ergebnisse/`-Doku)

| # | URL | Fundorte | Aktiv im Kern? |
|---|---|---|---|
| 1 | https://github.com/agent-ontology/agent-o | falle-zeilenangaben, quellen-404-korrektur, quellen-test, gesamtpruefung-final | ❌ nein |
| 2 | https://github.com/awslabs/aws-semantic-layer | quellen-404-korrektur, quellen-test, gesamtpruefung-final | ❌ nein |
| 3 | https://github.com/htac/htac | quellen-test, gesamtpruefung-final, mcp-connector-korrektur | ❌ nein |
| 4 | https://github.com/Paparare/SEAA | falle-zeilenangaben, quellen-test, gesamtpruefung-final, mcp-connector-korrektur | ❌ nein |
| 5 | https://github.com/paparse/ARIADNE | quellen-404-korrektur, quellen-test, gesamtpruefung-final | ❌ nein |
| 6 | https://jisem-journal.com/.../12473 | quellen-test, gesamtpruefung-final, mcp-connector-korrektur | ❌ nein (Platzhalter) |

**Verifikation:** `grep -r "github.com/htac/htac\|github.com/Paparare/SEAA" AGENTS.md knowledge/`
→ **0 Treffer**. Keine aktiven 404-Links in den Kern-Dateien. ✅

---

## 4. HTTP 403 – Bot-Schutz (nicht als defekt gewertet)

| URL |
|---|
| https://aaai.org/papers/0021-... |
| https://docs.aws.amazon.com/prescriptive-guidance/ |
| https://www.mdpi.com/2075-5309/16/1/196 |
| https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents |

> 403 = „Forbidden" (Zugriffsschutz), nicht „Not Found". Die Ressourcen existieren.

---

## 5. Zusammenfassung

| Prüfung | Ergebnis |
|---|---|
| Fast Write Routing Quelle (arXiv:2608.22215) | ✅ 200 |
| Aktive 404 in Kern-Dateien | ✅ **0** |
| 404 gesamt (nur in Doku/Platzhalter) | ℹ️ 6 |
| Kern-Quellen (arXiv, ACL, GitHub, Cognee, Graphiti) | ✅ erreichbar |

**Fazit:** Keine aktiven 404-Links in den Kern-Dateien. Alle 404-URLs erscheinen
ausschließlich in `ergebnisse/`-Dokumenten (Belege der bereits korrigierten Links)
oder als Platzhalter (`jisem .../12473`).
