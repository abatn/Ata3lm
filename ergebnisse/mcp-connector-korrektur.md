# MCP-Connector-Korrektur

> Datum: 2026-09-30
> Zweck: Korrektur der fehlenden/defekten Connector-Quellen (404) im Knowledge-Agenten
> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich in den Dateien steht
> oder durch offizielle, erreichbare Quellen belegt ist.
> Methode: `grep`, `curl -L -A "Mozilla/5.0"` (HTTP-Status)

---

## Aufgabe 1: 404-Links durch funktionierende Alternativen ersetzen

### 1.1 Gefundene 404-Links (aktiv in Kern-Dateien)

| Connector | 404-URL | Vorkommen |
|---|---|---|
| HTAC | https://github.com/htac/htac | AGENTS.md:213, index.md:216, wissenszyklus-8-stufen.md:121 |
| SEAA | https://github.com/Paparare/SEAA | AGENTS.md:212, index.md:215, wissenszyklus-8-stufen.md:94 |

### 1.2 Verifizierte Alternativen (aus den Connector-Dateien)

Die korrekten Quellen standen bereits in den Connector-Dateien
(`connectors/htac-agentdice.md`, `connectors/mars-seaa.md`) – sie waren
nur in den Connector-Tabellen der Kern-Dateien falsch eingetragen.

| Connector | Korrekte Quelle (aus Connector-Datei) | HTTP-Status |
|---|---|---|
| HTAC | https://icml.cc/virtual/2026/poster/63033 (ICML 2026 Poster) | **200** ✅ |
| SEAA | https://arxiv.org/abs/2609.17331 (arXiv, 15. Sep 2026) | **200** ✅ |

> **Titel-Verifikation:**
> - HTAC: `connectors/htac-agentdice.md` §2.1 → „Quelle: HTAC (ICML 2026 Poster)"; §5 → ICML-Poster-Link.
> - SEAA: `connectors/mars-seaa.md` Identität → „SEAA (arXiv 15. Sep 2026)".

### 1.3 Durchgeführte Ersetzungen

| Datei | Zeile | Vorher | Nachher |
|---|---|---|---|
| `AGENTS.md` | 212 | `https://github.com/Paparare/SEAA` | `https://arxiv.org/abs/2609.17331` |
| `AGENTS.md` | 213 | `https://github.com/htac/htac` | `https://icml.cc/virtual/2026/poster/63033` |
| `knowledge/lifecycle/rekursion/index.md` | 215 | `https://github.com/Paparare/SEAA` | `https://arxiv.org/abs/2609.17331` |
| `knowledge/lifecycle/rekursion/index.md` | 216 | `https://github.com/htac/htac` | `https://icml.cc/virtual/2026/poster/63033` |
| `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` | 94 | `https://github.com/Paparare/SEAA` | `https://arxiv.org/abs/2609.17331` |
| `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` | 121 | `https://github.com/htac/htac` | `https://icml.cc/virtual/2026/poster/63033` |

**Ergebnis:** Keine 404-Links mehr in den Kern-Dateien.

---

## Aufgabe 2: Platzhalter-URL ersetzen

### 2.1 Befund

| Datei | Zeile | Platzhalter-URL | HTTP |
|---|---|---|---|
| `ergebnisse/gesamtpruefung.md` | 155 | https://jisem-journal.com/.../12473 | 404 |

### 2.2 Echte Quelle (bereits in den Kern-Dateien verwendet)

Die echte URL stand bereits in `wissenszyklus-8-stufen.md:110` und in der
Connector-Tabelle (Affective Computing):

- **Echte URL:** https://jisem-journal.com/index.php/journal/article/view/12473
- **HTTP-Status:** **200** ✅ (verifiziert via curl)

> **Titel/Quelle:** JISEM 2025 – Emotions-Modul + Valenz als intrinsisches
> Feedback (vgl. `connectors/affective-signals.md`, `AGENTS.md` Prinzip 8).
> Der Platzhalter `.../12473` war nur eine Abkürzung, kein defekter Link.

### 2.3 Durchgeführte Ersetzung

| Datei | Zeile | Vorher | Nachher |
|---|---|---|---|
| `ergebnisse/gesamtpruefung.md` | 155 | `https://jisem-journal.com/.../12473` | `https://jisem-journal.com/index.php/journal/article/view/12473` |

---

## Aufgabe 3: Zählung korrigieren

### 3.1 Verifizierte Zahlen (mit `find`)

```bash
$ find skills/ -name "SKILL.md" | wc -l
14
$ find connectors/ -name "*.md" | wc -l
15
```

| Kategorie | Soll (ursprünglich angenommen) | Tatsächlich (verifiziert) |
|---|---|---|
| Skills (`SKILL.md`) | 8 | **14** (9 Haupt + 5 Sub-Skills) |
| Connectoren (`*.md`) | 16 | **15** |

### 3.2 Skills im Detail (14)

```
Haupt-Skills (9):
  skills/act/SKILL.md
  skills/cognize/SKILL.md
  skills/collect-experience/SKILL.md
  skills/expand-knowledge/SKILL.md
  skills/non-cognitive/SKILL.md
  skills/recursive-improve/SKILL.md
  skills/reflect/SKILL.md
  skills/store-memory/SKILL.md
  skills/structure-knowledge/SKILL.md

Sub-Skills (5) unter skills/recursive-improve/:
  skills/recursive-improve/akt/SKILL.md
  skills/recursive-improve/compare/SKILL.md
  skills/recursive-improve/konstrukt/SKILL.md
  skills/recursive-improve/observe/SKILL.md
  skills/recursive-improve/revise/SKILL.md
```

### 3.3 Connectoren im Detail (15)

```
connectors/affective-signals.md      connectors/hela-evolution.md
connectors/agento-ariadne.md         connectors/hela-semantic.md
connectors/cca-framework.md          connectors/htac-agentdice.md
connectors/cognee-memory.md          connectors/mars-seaa.md
connectors/cognee-validation.md      connectors/observer-agent.md
connectors/consistency-gap.md        connectors/react.md
connectors/fast-write-routing.md     connectors/reflexion-trace.md
connectors/goedel-agent.md
```

### 3.4 Aktualisierung

Die korrigierten Zahlen wurden in `ergebnisse/gesamtpruefung-final.md`
dokumentiert (Tabelle 1.1, Abschnitt 5.5/5.6, Nachtrag).

---

## Aufgabe 4: quellen-404-korrektur.md korrigieren

### 4.1 Geänderte Zeilen

| Datei:Zeile | Vorher | Nachher |
|---|---|---|
| `ergebnisse/quellen-404-korrektur.md:75` | `| 9 | SEAA | https://github.com/Paparare/SEAA | 200 |` | `| 9 | SEAA | https://arxiv.org/abs/2609.17331 | 200 (korrigiert: github.com/Paparare/SEAA war 404) |` |
| `ergebnisse/quellen-404-korrektur.md:76` | `| 10 | HTAC | https://github.com/htac/htac | 200 |` | `| 10 | HTAC | https://icml.cc/virtual/2026/poster/63033 | 200 (korrigiert: github.com/htac/htac war 404) |` |
| `ergebnisse/quellen-404-korrektur.md` §5 Fazit | 3 Quellen korrigiert | 5 Quellen korrigiert (AgentO, ARIADNE, AWS-SL, SEAA, HTAC) |

### 4.2 Nachtrag in der Datei

Die Datei enthält jetzt einen „Nachtrag 2026-09-30 (MCP-Connector-Korrektur)"
mit den korrekten HTAC/SEAA-Quellen.

---

## Zusammenfassung

| Aufgabe | Ergebnis | HTTP-Status |
|---|---|---|
| 1. HTAC 404 → Alternative | https://icml.cc/virtual/2026/poster/63033 | 200 ✅ |
| 1. SEAA 404 → Alternative | https://arxiv.org/abs/2609.17331 | 200 ✅ |
| 2. JISEM-Platzhalter → echte URL | https://jisem-journal.com/index.php/journal/article/view/12473 | 200 ✅ |
| 3. Zählung | 14 SKILL.md, 15 Connectoren | verifiziert ✅ |
| 4. quellen-404-korrektur.md | HTAC/SEAA korrigiert | ✅ |

### Geänderte Dateien

1. `AGENTS.md` (L212, L213)
2. `knowledge/lifecycle/rekursion/index.md` (L215, L216)
3. `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (L94, L121)
4. `ergebnisse/gesamtpruefung.md` (L150–151, L155, L167–168)
5. `ergebnisse/quellen-404-korrektur.md` (L75, L76, Fazit + Nachtrag)
6. `ergebnisse/gesamtpruefung-final.md` (Zählung, Offene Punkte, Urteil)

### Lab-Prinzip-Konformität

- ✅ Keine Erfindungen: Alle Ersatz-Links stammen aus den bereits existierenden
  Connector-Dateien und wurden per `curl` auf HTTP 200 geprüft.
- ✅ Titel-Verifikation: HTAC = ICML 2026 Poster, SEAA = arXiv 2609.17331.
- ✅ Keine Quelle als „belegt" markiert, die nicht erreichbar ist.

**Ergebnis: Alle aktiven 404-Links in den Kern-Dateien sind korrigiert.**
