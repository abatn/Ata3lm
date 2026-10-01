# Public-APIs-Analyse (abatn/public-apis) für den Knowledge-Agenten

> Datum: 2026-09-30
> Quelle: https://github.com/abatn/public-apis („A collective list of free APIs", Fork von public-apis)
> Verifiziert: README.md, Branch `master` (HTTP 200, 198 KB), 51 Kategorien
> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich im Repository steht.

---

## Aufgabe 1: Relevante Kategorien

| Zweck | Kategorien | Für den Agenten nutzbar |
|---|---|---|
| **Wissen sammeln** | Books, Dictionaries, Documents & Productivity, Open Data, Patent, Science & Math, Government, Health, News | ✅ |
| **Wissen prüfen** | Data Validation, Security, Text Analysis | ✅ |
| **Wissen anwenden** | Calendar, Email, Finance, Jobs, Geocoding, Weather | ✅ |
| **Wissen erweitern** | Machine Learning, Programming, Development | ✅ |

**21 von 51 Kategorien** sind direkt nutzbar. (Die übrigen 30 betreffen Freizeit/Konsum und wurden nicht ausgewählt.)

---

## Aufgabe 2: APIs pro Kategorie (aus dem Repo, verifiziert)

### Wissen sammeln

| API | Beschreibung | Auth | HTTPS | CORS |
|---|---|---|---|---|
| **Gutendex** | Web-API für Project Gutenberg Bücher | No | Yes | Unknown |
| **Open Library** | Bücher, Cover und Daten | No | Yes | No |
| **Crossref Metadata Search** | Bücher- & Artikel-Metadaten | No | Yes | Unknown |
| **arXiv** | Research-Plattform (Physik, Mathe, …) | No | Yes | Unknown |
| **Free Dictionary** | Definitionen, Phonetik, Synonyme | No | Yes | Unknown |
| **GBIF** | Global Biodiversity Information Facility | No | Yes | Yes |
| **Wikidata** | Kollaborative Wissensbasis | OAuth | Yes | Unknown |
| **World Bank** | Weltdaten | No | Yes | No |

### Wissen prüfen

| API | Beschreibung | Auth | HTTPS | CORS |
|---|---|---|---|---|
| **Postman Echo** | Echo-Test für Requests | No | Yes | Unknown |
| **US Autocomplete** | Adress-Autovervollständigung | apiKey | Yes | Yes |
| **Cloudmersive NLP** | Natural Language Processing | apiKey | Yes | Yes |
| **Detect Language** | Spracherkennung | apiKey | Yes | Unknown |

### Wissen anwenden

| API | Beschreibung | Auth | HTTPS | CORS |
|---|---|---|---|---|
| **REST Countries** | Länderinfos via REST | No | Yes | Yes |
| **Brazil** (BrasilAPI) | Brasilianische offene Daten | No | Yes | Yes |
| **Arbeitnow** | Job-Board (offen) | No | Yes | Yes |
| **DevITjobs UK** | IT-Jobs UK | No | Yes | Yes |
| **Datamuse** | Wortfindungs-Engine | No | Yes | Unknown |

### Wissen erweitern

| API | Beschreibung | Auth | HTTPS | CORS |
|---|---|---|---|---|
| **Judge0 CE** | Online-Code-Ausführung | apiKey | Yes | Unknown |
| **KONTESTS** | Programmier-Wettbewerbe | No | Yes | Unknown |
| **Deepcode** | Code-Analyse | No | Yes | Unknown |
| **Codeforces** | Wettbewerbs-API | apiKey | Yes | Unknown |

---

## Aufgabe 3: Top-5-Empfehlungen

### 1. arXiv — `https://arxiv.org/help/api/user-manual`
- **Nützlich:** kuratierte Forschungspapiere (Wissen sammeln).
- **Stufe:** Erfahrung (1) → Wissen (2).
- **Connector:** `connectors/react.md` (Recherche-Tool).
- **Auth/HTTPS/CORS:** No / Yes / Unknown → **MCP-tauglich** (REST/JSON, HTTPS, kostenlos).

### 2. Crossref Metadata Search — `https://github.com/CrossRef/rest-api-doc`
- **Nützlich:** Bücher- & Artikel-Metadaten (Quellen-Provenienz).
- **Stufe:** Wissen (2).
- **Connector:** `connectors/observer-agent.md`.
- **Auth/HTTPS/CORS:** No / Yes / Unknown → **MCP-tauglich, kostenlos**.

### 3. Gutendex — `https://gutendex.com/`
- **Nützlich:** Project-Gutenberg-Bücher (Rohwissen).
- **Stufe:** Erfahrung (1).
- **Connector:** `connectors/agento-ariadne.md` (Rohdaten-Ablage, Tier 1).
- **Auth/HTTPS/CORS:** No / Yes / Unknown → **MCP-tauglich, kostenlos**.

### 4. GBIF — `https://www.gbif.org/developer/summary`
- **Nützlich:** Biodiversitätsdaten (strukturiertes Wissen).
- **Stufe:** Wissen (2) → Wissen+ (8).
- **Connector:** `connectors/observer-agent.md`.
- **Auth/HTTPS/CORS:** No / Yes / **Yes** → **MCP-tauglich, kostenlos, CORS offen**.

### 5. Free Dictionary — `https://dictionaryapi.dev/`
- **Nützlich:** Definitionen/Synonyme (Wissensprüfung, Begriffsklärung).
- **Stufe:** Kognition (4).
- **Connector:** `connectors/hela-semantic.md` (semantisches Wissen).
- **Auth/HTTPS/CORS:** No / Yes / Unknown → **MCP-tauglich, kostenlos**.

---

## Zusammenfassung

| # | API | Kategorie | Auth | HTTPS | Stufe |
|---|---|---|---|---|---|
| 1 | arXiv | Science & Math | No | Yes | Erfahrung/Wissen |
| 2 | Crossref Metadata Search | Documents & Productivity | No | Yes | Wissen |
| 3 | Gutendex | Books | No | Yes | Erfahrung |
| 4 | GBIF | Science & Math | No | Yes | Wissen/Wissen+ |
| 5 | Free Dictionary | Dictionaries | No | Yes | Kognition |

**Alle 5 sind kostenlos (kein apiKey), HTTPS, REST/JSON → MCP-tauglich.**
Links stammen wörtlich aus dem Repository (`README.md`, Branch `master`).

**Hinweis:** `Judge0 CE` (Code-Ausführung) wäre für den Gödel-Agent-Connector
(`connectors/goedel-agent.md`) relevant, benötigt aber einen `apiKey`.
