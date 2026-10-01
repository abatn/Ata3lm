# Quellen-Test – HTTP-Status aller Links

> Datum: 2026-09-30
> Zweck: Vollständiger HTTP-Status-Check aller in den MD-Dateien referenzierten Quellen.
> Methode: `curl -L -A "Mozilla/5.0" --connect-timeout 8 --max-time 20` (Redirects gefolgt)

---

## 1. Zusammenfassung

> **Re-Test 2026-09-30 (nach MCP-Connector-Korrektur):** Die 2 aktiven
> 404-Links (HTAC, SEAA) wurden in den Kern-Dateien durch erreichbare
> Quellen ersetzt. Die verbleibenden 404-URLs erscheinen **nur noch in
> historischen `ergebnisse/`-Dokumenten** (Belege der alten Links).

| Kategorie | Anzahl |
|---|---|
| Eindeutige URLs (bereinigt) | 70 |
| HTTP 200 (OK) | 55 |
| HTTP 202 (Accepted, DOI/IEEE) | 2 |
| HTTP 403 (Zugriffsschutz/Bot-Block, nicht defekt) | 4 |
| HTTP 404 (Nicht gefunden) | 6 |
| Leer/ungültig (Markdown-Artefakt) | 2 |

---

## 2. HTTP 404 – Defekte Links

| # | URL | Datei(en) | Bewertung |
|---|---|---|---|
| 1 | https://github.com/htac/htac | `ergebnisse/quellen-test.md`, `ergebnisse/gesamtpruefung-final.md`, `ergebnisse/mcp-connector-korrektur.md` | ✅ **korrigiert** – nur noch in Doku |
| 2 | https://github.com/Paparare/SEAA | `ergebnisse/falle-zeilenangaben.md`, `ergebnisse/quellen-test.md`, `ergebnisse/gesamtpruefung-final.md`, `ergebnisse/mcp-connector-korrektur.md` | ✅ **korrigiert** – nur noch in Doku |
| 3 | https://github.com/agent-ontology/agent-o | `ergebnisse/falle-zeilenangaben.md`, `ergebnisse/quellen-404-korrektur.md`, `ergebnisse/quellen-test.md` | Nur historische Doku |
| 4 | https://github.com/awslabs/aws-semantic-layer | `ergebnisse/quellen-404-korrektur.md`, `ergebnisse/quellen-test.md` | Nur historische Doku |
| 5 | https://github.com/paparse/ARIADNE | `ergebnisse/quellen-404-korrektur.md`, `ergebnisse/quellen-test.md` | Nur historische Doku |
| 6 | https://jisem-journal.com/.../12473 | `ergebnisse/gesamtpruefung-final.md`, `ergebnisse/quellen-test.md`, `ergebnisse/mcp-connector-korrektur.md` | Platzhalter – echte URL ersetzt |

**Wichtig (Re-Test):** Die Links #1 (HTAC) und #2 (SEAA) sind **keine aktiven Referenzen mehr** in den Kern-Dateien. Sie wurden ersetzt durch:
- HTAC → https://icml.cc/virtual/2026/poster/63033 (HTTP 200)
- SEAA → https://arxiv.org/abs/2609.17331 (HTTP 200)

**Verifikation:** `grep -r "github.com/htac/htac\|github.com/Paparare/SEAA" AGENTS.md knowledge/` → **0 Treffer**.

---

## 3. HTTP 403 – Zugriffsschutz (nicht als defekt gewertet)

| # | URL | Bewertung |
|---|---|---|
| 1 | https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/ | Bot-Schutz (Paper existiert) |
| 2 | https://docs.aws.amazon.com/prescriptive-guidance/ | Verzeichnis-URL, Bot-Schutz |
| 3 | https://www.mdpi.com/2075-5309/16/1/196 | Bot-Schutz |
| 4 | https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents | Bot-Schutz |

> 403 bedeutet "Forbidden" (Zugriff verweigert), nicht "Not Found". Die Ressourcen existieren, blocken aber automatisierte Abrufe.

---

## 4. HTTP 200/202 – Erreichbare Links (Auszug der wichtigsten)

### arXiv
| URL | Status |
|---|---|
| https://arxiv.org/abs/2608.22215 (Fast Write Routing) | **200** |
| https://arxiv.org/abs/2410.04444 (Gödel Agent) | 200 |
| https://arxiv.org/abs/2007.09454 (AgentO) | 200 |
| https://arxiv.org/abs/2105.09864 (ARIADNE) | 200 |
| https://arxiv.org/abs/2210.03629 (ReAct) | 200 |
| https://arxiv.org/abs/2303.11366 (Reflexion) | 200 |
| https://arxiv.org/abs/2609.08832 (Consistency) | 200 |
| https://arxiv.org/abs/2609.24663 (EvoPathBench) | 200 |

### GitHub (erreichbar)
| URL | Status |
|---|---|
| https://github.com/Arvid-pku/Godel_Agent | 200 |
| https://github.com/ReinerBRO/HeLa-Mem | 200 |
| https://github.com/topoteretes/cognee | 200 |
| https://github.com/getzep/graphiti | 200 |
| https://github.com/Paparare/MARS | 200 |
| https://github.com/Wuzheng02/Agent-Dice | 200 |
| https://github.com/ShengranHu/ADAS | 200 |
| https://github.com/Kepler1908/TRACE | 200 |
| https://github.com/noahshinn/reflexion | 200 |

### ACL Anthology
| URL | Status |
|---|---|
| https://aclanthology.org/2026.acl-long.625/ (HeLa-Mem) | 200 |
| https://aclanthology.org/2025.acl-long.1354/ (Gödel) | 200 |
| https://aclanthology.org/2026.findings-acl.908/ | 200 |

### Python-Doku (Fast Write Routing Solver-Tests)
| URL | Status |
|---|---|
| https://docs.python.org/3/library/functions.html#min | 200 |
| https://docs.python.org/3/library/functions.html#max | 200 |
| https://docs.python.org/3/library/functions.html#sum | 200 |
| https://docs.python.org/3/library/functions.html#len | 200 |
| https://docs.python.org/3/library/functions.html#sorted | 200 |

---

## 5. Bewertung

| Kriterium | Ergebnis |
|---|---|
| Fast Write Routing Quelle (arXiv:2608.22215) | ✅ 200 – erreichbar |
| Kern-Quellen (arXiv, ACL, Cognee, Graphiti, HeLa) | ✅ erreichbar |
| **Aktive 404-Links in Kern-Dateien** | ✅ 0 (HTAC/SEAA korrigiert) |
| Historische 404-Links (nur in Doku) | ℹ️ 5 (AgentO, AWS-SL, ARIADNE, HTAC-alt, SEAA-alt) |
| Platzhalter-URL | ℹ️ 1 (jisem .../12473 – echte URL ersetzt) |

**Fazit (Re-Test):** Der Knowledge-Agent ist **quellenkonform** – es gibt **keine aktiven 404-Links** mehr in den Kern-Dateien. Die verbleibenden 404-URLs erscheinen ausschließlich in historischen `ergebnisse/`-Dokumenten als Belege der bereits korrigierten Links (Lab-Prinzip: keine Erfindungen → ehrlich dokumentieren).
