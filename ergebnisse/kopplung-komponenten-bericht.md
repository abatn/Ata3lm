# Bericht: Entkoppelte Komponenten des Knowledge-Agenten — Problem & Lösung je Punkt (mit offiziellen Quellen)

> Datum: 2026-10-06 · Status: **Bericht** (keine Produktänderung). Basis-Revision für Laufbelege: **`c381fbd`** (letzte reproduzierte Prüfung).
> Grundlage: `AGENTS.md` §1–§11 · `ergebnisse/agent-aufbau-kompakt.png` (Stand 2026-10-04) · `ergebnisse/knowledge-agent-plan.md` ·
> `ergebnisse/e2e-pruefung-2026-10-05.md` · `ergebnisse/e2e-2026-10-05.md` · Audit B1–B8.
> Verfahren (§6): **Keine Erfindungen.** Jede Lösung ist **Belegt** (offizieller Standard/Paper, Link) **oder** **Auftrag** (Betriebsregel). Quellen in §5 (HTTP-200-geprüft).
> **Grenze (Korrektur):** „Quelle erreichbar" ≠ „Lösung belegt" — die Quellen stützen **Muster**, nicht die konkrete Implementierung; diese bleibt Auftrag + Implementierungsarbeit.

## 0. Ist-Komponenten — **die 4 Doku-Quellen sind KEINE vollständige Laufzeit-Beschreibung**

Belegt aus den Quellen: **21 Module**, 8-Stufen-Runner, 5-Phasen-Runner, 3-Tier-Memory + Shared + L4-Skills (14), 17 Connectors (9 Prozesse), MCP-Konfig, Governance. **Aber ehrlich (Korrektur):**
- Die Grafik ist vom **2026-10-04**; der ältere Live-Bericht (`e2e-2026-10-05`) beschreibt einen **Write bei `uncertain` als Erfolg** — der **später geprüfte Code blockiert** diesen Fall inzwischen (Artefakt ≠ aktueller Code).
- „**14/15 MCP-Server**" heißt dort **Handshake + `tools/list`**; derselbe Bericht nennt nur **10/15 erfolgreiche Werkzeug-Aufrufe** ⇒ **kein** Nachweis vollständiger fachlicher Integration.
- **Verbindlich** für Aussagen sind daher **Revision/Konfiguration konkrete Laufbelege** (zuletzt reproduziert: **`c381fbd`**), nicht die Doku allein.

## 1. Zielanforderung (aus AGENTS.md)

§3 (8-Stufen-Zyklus), §2/§7 (5-Phasen-Rekursion, Reflexion), §5 (`M(t)→M(t+1)`), §6 (Provenienz/keine Erfindung),
§9/§9.1–9.3 (Gate/Drift/HITL/Zwei-Personen), §10 (Fast Write Routing + Supersede), §11 (MCP über lokaler Basis).
**Kernziel:** EIN gemeinsamer, nachvollziehbarer Zustand über alle Stufen/Phasen/Tiers — nicht viele isolierte Prozesse.

## 2. Die Entkopplungen und ihre Lösungen (je Punkt mit offizieller Quelle)

### K1 · Zwei Runner ohne gemeinsamen/persistenten Zustand
- **Problem:** `lifecycle_runner.run_cycle` und `recursion_runner.run_recursion` erzeugen je eigenen Zustand; WM/Graph/HMM sind in-memory (Audit §3: „geteilter persistenter Zustand offen").
- **AGENTS.md:** §3, §5 (`M(t)→M(t+1)`), §7 (episodische Reflexion).
- **Lösung (ergänzt nach Review):** `data/memory/runner_state.py` (Snapshot + `reconstruct()`); der Snapshot muss **mehr als WM-Schlüssel** enthalten: **Inhalte, Metadaten, Schema-/Revisionsstand, offene Freigaben**; **Nebenläufigkeit** (gleichzeitige Änderungen) + **Wiederherstellung nach Schreibabbrüchen** (Atomicität) müssen geregelt sein.
- **Offizielle Quelle (Belegt):** MemGPT — hierarchische Memory-**Tiers** + Interrupts (arXiv:2310.08560); Dual-Layer Θ+E (arXiv:2608.22215). **Abgrenzung (Review):** MemGPT stützt das *hierarchische Gedächtnis-Muster*, schreibt aber **dieses** `runner_state`-Interface **nicht** vor.
- **Status:** Muster **Belegt**; konkrete Schnittstelle **Auftrag** (Implementierungsarbeit).

### K2 · Kein einheitlicher Schreibpfad (Write-Gateway)
- **Problem:** `pipeline.route_and_store`, `fast_write_router.apply_write_action`, `skill_interpreter._run_memory_write`, MCP `write` schreiben je eigenständig → Supersede/Trust/PII/Provenienz greifen **nicht überall** (Audit B3/N5).
- **AGENTS.md:** §6, §9.2c (nur Verifiziertes), §10.7, §11.3.
- **Lösung (ergänzt nach Review):** **ein** `write_gateway.store(...)`; Reihenfolge **Mandat → FWR → Trust/PII → Poisoning → Human-/Zwei-Personen-Freigabe (§9.3) → Drift (§9.1c) → Supersede → Shared → Provenienz**; **Inhalt, Historie und Provenienz konsistent** speichern. **FWR entscheidet über Wissen**; **technische Checkpoints** (State, Archive) brauchen **eigene Operationsregeln**.
- **Offizielle Quelle (Belegt):** MCP-Spec 2025-06-18 — Tool Safety/Consent; MPBench/A-MemGuard (§9.2c). **Abgrenzung (Review):** MCP sagt selbst, das Protokoll **kann** diese Schutzprinzipien **nicht erzwingen** (Implementors **SHOULD**) ⇒ Schutz = Auftrag/Implementierung.
- **Status:** Muster **Belegt**; Gateway + Freigabe-/Drift-Einbau **Auftrag**.

### K3 · Provenienz nicht gebunden (je Fakt)
- **Problem:** Inhalt wird geschrieben, aber Quelle/Verifikation/Freigabe/Hash nicht einheitlich (Audit §3 „Knowledge/Provenienz … nicht einheitlich").
- **AGENTS.md:** §6 (Provenienz pro Iteration), §9.1d (Score/Diff/Drift).
- **Lösung:** **PROV-O-konforme** Records je Write: `prov:Entity`/`prov:Activity`/`prov:Agent`, `prov:wasGeneratedBy`, `prov:wasDerivedFrom`, `prov:wasAttributedTo`, `prov:invalidatedAtTime`.
- **Offizielle Quelle (Belegt):** **W3C PROV-O** (Recommendation 2013) — normativ (`wasGeneratedBy/wasDerivedFrom/wasAttributedTo/wasRevisionOf/invalidatedAtTime`). **Abgrenzung (Review):** PROV-O **garantiert weder** überprüfte Quellen noch unveränderliche Protokolle noch atomare Speicherung; **Bindung an Inhalt + Freigabe = Implementierungsarbeit**.
- **Status:** Datenmodell **Belegt**; Durchsetzung **Auftrag**.

### K4 · Skills nicht maschinell an Prozesse gebunden (L4)
- **Problem:** `skill_interpreter.DEFAULT_REGISTRY` = nur 2 Executoren; **14** `SKILL.md` deklarieren Prozesse nur in Prosa → Audit: nur 3/14 lauffähig.
- **AGENTS.md:** §3; `skills/README.md` (L4 first-class).
- **Lösung:** maschinenlesbares Feld `process:` im Frontmatter (per **JSON Schema** validiert), Registry vollständig; nicht-integrierbare klar `doc-only`.
- **Offizielle Quelle (Belegt):** Voyager — „ever-growing skill library of **executable code**" (arXiv:2305.16291); JSON-Schema-Spec. **Ergänzung (Review):** JSON Schema prüft nur die **Struktur**; **jeder Executor** muss mit passenden Eingaben/Berechtigungen/Ergebnissen **real getestet** werden. `doc-only` kennzeichnet fehlende Funktion ehrlich, **erfüllt aber keine geforderte Fähigkeit**.
- **Status:** Muster **Belegt**; Schema+Executor-Tests **Auftrag**.

### K5 · Tier1-Supersede/Versionierung nicht end-to-end
- **Problem:** Supersede nur im FWR-Pfad; andere Schreibwege umgehen es; Archivnamen kollidieren (B1/B-N3). §9.1b verlangt Versionierung (§-Konflikt mit CI-Drift = B8).
- **AGENTS.md:** §10.7 („invalidieren, NICHT löschen"), §9.1b.
- **Lösung (korrigiert nach Review):** Archiversatz über `prov:wasRevisionOf`/`prov:invalidatedAtTime`; **Archivdateien nicht pauschal von Prüfung ausnehmen**, sondern **eigener Integritäts-Check** (Änderung/Löschung historischer Archive erkennen); monotone Namen **allein verhindern keine parallelen Schreibkonflikte** ⇒ Lock/Compare-and-swap nötig.
- **Offizielle Quelle (Belegt):** **W3C PROV-O** (`wasRevisionOf`/`invalidatedAtTime`); Graphiti bi-temporal (§10/§11).
- **Status:** Muster **Belegt**; Archiv-Integrität/Concurrency **Auftrag**.

### K6 · Governance nicht über alle Stufen (Mandat/Drift/Compare)
- **Problem:** Graph-Mutation ohne Mandat (B4); Drift-Labelräume widersprüchlich + `revised=True` bei `ask` (B5); Revise ohne Compare-Beleg (B6).
- **AGENTS.md:** §9 (Gate), §9.1c (Drift-Bound), Guardrail 5 („kein Revise ohne Compare-Beleg").
- **Lösung (KORRIGIERT nach Review):** Mandat vor **jeder** Mutation (auch Graph); ein Labelraum; **`revised = ok AND gate == "allow"`** — **nicht** `gate != ask` (das ließe auch `deny` durch!). **`Compare.observed=True` genügt NICHT** (Beobachtungen können negativ/unzureichend sein) ⇒ Revision braucht eine **ausdrücklich zulässige Entscheidung + passende, zur Änderung gehörende Evidenz** (§9.1d).
- **Offizielle Quelle (Belegt):** **NIST AI RMF 1.0** (Governance/Manage; DOI 200) + **EU-KI-VO** Art. 14 (§9.3); Drift kalibriert (arXiv:2603.06333). Governance-Bedingungen selbst = **Auftrag**.
- **Status:** Problem belegt; Bedingungen **Auftrag** (nachgeschärft).

### K7 · MCP-/Connector-Integration + Beobachtbarkeit
- **Problem:** 6/17 Connector-Prozesse synthetisch („beispiel"); keine durchgängige Span-/Execution-Trace; MCP-Fallback schwächt Schutz (B3).
- **AGENTS.md:** §11 (MCP optional, lokale Basis Pflicht; Fallback ohne Datenverlust).
- **Lösung (abgegrenzt nach Review):** MCP-konforme Server — **stdio UND Streamable HTTP** (nicht nur stdio); **Transportausfall** darf den **geschützten lokalen** Fallback nutzen, **eine fachliche Ablehnung darf dadurch NICHT umgangen werden**; **OpenTelemetry-Spans** für Execution-Graph/Timeline; Spans **ersetzen kein dauerhaftes Auditprotokoll**; „beispiel" real anbinden **oder** dauerhaft als nicht-integriert kennzeichnen.
- **Offizielle Quelle (Belegt):** **MCP Spec 2025-06-18** (HTTP 200); **OpenTelemetry** (HTTP 200).
- **Status:** Standards **Belegt**; Integration + Audit **Auftrag**.

## 3. Zielarchitektur (die Kopplung schließen)

```text
   ┌──────────── Shared Runner State (§3/§5, K1) ────────────┐
   │ runner_state.json: WM · Graph · HMM · Drift-Checkpoint    │
   └──────────▲───────────────────────────────▲──────────────┘
 8-Stufen-Runner                               5-Phasen-Runner
              └───────────────┬───────────────┘
                              ▼
        ┌────── Write-Gateway (§6/§9/§10, K2) ──────┐
Aufrufer│ Mandat → FWR → Trust/PII → Poisoning →   │
(Skill, │ PROV-O-Record → Write(+Supersede) →      │
 MCP,   │ Tier3 → Shared → OpenTelemetry-Span      │
 Conn.) └───────────────────────────────────────────┘
```

## 4. Abnahme (testbar) + Reihenfolge

| Prio | Schritt | Abnahme |
|---|---|---|
| 1 | K1 Shared Runner State | 2. Prozess liest State; WM/Graph/HMM/Drift fortgesetzt (Restart-Test) |
| 2 | K2+K3 Write-Gateway + PROV-O | jeder Schreibpfad hat Provenienz + Trust geprüft; genau ein Gateway |
| 3 | K5 Supersede/Versionierung | Alpha→Beta→Gamma erhalten; CI-Drift-B8 Exit 0 |
| 4 | K4 Skills | 14/14 lauffähig **oder** explizit `doc-only` |
| 5 | K6+K7 Governance/MCP | B4/B5/B6 + MCP-Fallback fail-closed |
| 6 | Live | beide Modelle + echter E2E (§4), 100 % Coverage **mit** Key |

**Gate:** neue Interfaces (Gateway/State/Skill-Schema) ⇒ Guardrail 4 + §9 = `approved`; Änderungen an `AGENTS.md`/`tier1-base` ⇒ §9.1b `versions/vN`. Als Rekursion dokumentieren (§6/Guardrail 3).

## 5. Offizielle Quellen — **alle am 2026-10-06 real geprüft (HTTP 200)**

> §6-Verifikation: jeder Link unten wurde per HTTP-Request abgerufen; Ergebnis **200 OK** (kein toter Link). Vorher als „angenommen" markierte Quellen sind damit **verifiziert**.

| Quelle | Link | Status |
|---|---|---|
| W3C PROV-O (Recommendation 2013) | https://www.w3.org/TR/prov-o/ | 200 |
| MCP Specification 2025-06-18 | https://modelcontextprotocol.io/specification/2025-06-18 | 200 |
| W3C SHACL | https://www.w3.org/TR/shacl/ | 200 |
| W3C OWL 2 Overview | https://www.w3.org/TR/owl2-overview/ | 200 |
| JSON Schema Specification | https://json-schema.org/specification | 200 |
| OpenTelemetry Spec | https://opentelemetry.io/docs/specs/otel/ | 200 |
| RFC 2119 | https://www.rfc-editor.org/rfc/rfc2119 | 200 |
| RFC 8174 (BCP 14) | https://www.rfc-editor.org/rfc/rfc8174 | 200 |
| NIST AI RMF 1.0 (DOI) | https://doi.org/10.6028/NIST.AI.100-1 | 200 |
| NIST AI RMF (AIRC) | https://airc.nist.gov/airmf-resources/airmf/ | 200 |
| arXiv Generative Agents 2304.03442 | https://arxiv.org/abs/2304.03442 | 200 |
| arXiv Voyager 2305.16291 | https://arxiv.org/abs/2305.16291 | 200 |
| arXiv MemGPT 2310.08560 | https://arxiv.org/abs/2310.08560 | 200 |
| arXiv ReAct 2210.03629 | https://arxiv.org/abs/2210.03629 | 200 |
| arXiv Reflexion 2303.11366 | https://arxiv.org/abs/2303.11366 | 200 |
| arXiv Dual-Layer Memory 2608.22215 | https://arxiv.org/abs/2608.22215 | 200 |

**Nicht in-dieser-Session auf HTTP geprüft (aus `AGENTS.md` übernommen):** EU-KI-VO (VO (EU) 2024/1689) Art. 14, SEAA 2609.17331 — dort bereits gesetzlich zitiert.

## 6. Review-Korrekturen (übernommen am 2026-10-06)

Externe Prüfung bestätigte das Problembild **überwiegend**, mit verbindlichen Korrekturen — eingearbeitet in K1–K7:

1. **„Quelle erreichbar" ≠ „Lösung belegt":** Die Quellen rechtfertigen **Muster**, nicht jede Implementierungsentscheidung. MCP sagt ausdrücklich, das **Protokoll kann seine Schutzprinzipien nicht erzwingen** (Implementors *SHOULD*) ⇒ Durchsetzung = Auftrag/Implementierung.
2. **Die 4 Doku-Quellen sind keine vollständige Laufzeit-Beschreibung:** Grafik 2026-10-04; alter Live-Bericht (Write bei `uncertain` = Erfolg) widerspricht dem aktuell geprüften Code; „14/15 MCP" = nur Handshake/`tools/list`, echte Aufrufe nur 10/15 ⇒ verbindlich sind **Revision/Konfiguration/Laufbelege** (zuletzt **`c381fbd`**).
3. **K5:** `versions/**` pauschal auszunehmen ist unvollständig ⇒ **eigene Archiv-Integritätsprüfung**; monotone Namen lösen **keine** Parallelkonflikte.
4. **K6 (Fehler behoben):** `gate != ask` ließ auch `deny` passieren ⇒ jetzt **`gate == "allow"`**; `Compare.observed=True` ist **kein** ausreichendes Revisionskriterium.
5. **K7:** MCP auch **Streamable HTTP**; Transportausfall ≠ Umgehung fachlicher Ablehnung; Spans ≠ Auditprotokoll.

**Offen:** Die Rückmeldung war **abgeschnitten** („MCP erklärt ausdrücklich, dass das Protokoll die …"). Die 3. Meta-Korrektur ist unvollständig gelesen — vor endgültiger Bewertung nachreichen.
