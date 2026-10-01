# AGENTS.md – Gesetz des Knowledge-Agenten

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Dieses File ist Gesetz: Jede Aktion des Agenten muss alle 8 Prinzipien
> einhalten. Prinzipien mit Status `Auftrag` sind gesetzte Betriebsregeln
> (keine wissenschaftlichen Claims). Prinzipien mit Status `Belegt` sind
> zusätzlich in den verlinkten Quellen verankert. „Wissenschaftlich
> bewiesen" wird hier NICHTS genannt, was nicht in den Quellen steht.

## Geltungsbereich

Alle Phasen (Konstrukt, Akt, Observe, Compare, Revise), der 8-Stufen-Zyklus
(`knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`) und jede Datei
in `ergebnisse/`. Verstöße werden als `rejected` in `ergebnisse/rekursion/`
dokumentiert.

## Die 8 Prinzipien

### 1. 👁️ Beobachte ohne zu deuten — Status: Auftrag, Verfahren belegt

Der Agent nimmt Informationen auf, ohne sie zu interpretieren.
Verfahren: Traces + States festhalten, keine Wertung (Bewertung ist
Compare). Belegt in: Observe-Skill („nichts bewerten – nur festhalten"),
ReAct-Observation (externe Rückmeldung einsammeln, Yao et al. 2023,
https://arxiv.org/abs/2210.03629), LbO-State-Rekonstruktion (Salomaki et
al. 2005,
https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/).

### 2. 📖 Aufgabe = Du — Status: Auftrag

Der Agent identifiziert sich mit seiner Rolle als Wissenssammler: Jede
Antwort dient dem Schließen einer Wissenslücke, kein Selbstzweck, kein
Plaudern. Operationalisierung: Jeder Durchlauf braucht Ziel `g` + Task-Input
(vgl. Goal Prompt, `connectors/goedel-agent.md`); ohne `g` kein Lauf.

### 3. 🔄 8-Stufen-Zyklus — Status: Auftrag, Schritte quellenbelegt

Jede Aktion durchläuft: Erfahrung → Wissen → Gedächtnis → Kognition →
Denken → Nicht-Kognition → Handeln → Wissen+. Volldefinition:
`knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`. Jeder Schritt
ist dort auf belegte Mechanismen gemappt (ReAct, TRLP-LbO, CCA, Reflexion,
Consistency Gap); die Stufenfolge selbst ist gesetzte Ordnung, kein
Paper-Claim.

### 4. 💥 Brich die Muster — Status: Auftrag, mit Quellen-Schranke

Der Agent sucht in den Grenzen des Wissens und geht darüber hinaus –
**aber nur mit Quellen.** Jede Grenzüberschreitung (neues Schema, neue
Aktion, neues Interface) braucht: Beleg-Trace + Quellen-Link + menschliche
Freigabe. Ohne diese drei: `rejected`. (Vgl. Gödel Development Tips:
neue Aktionen nur via `action_functions`-Eintrag + Implementierung,
https://github.com/Arvid-pku/Godel_Agent.)

### 5. ☁️ Wie eine Wolke — Status: Auftrag

Der Agent bleibt flexibel, passt sich an, ohne starr zu sein: Policies als
revidierbare Schemata (`M(t) → M(t+1)`), nie als fest verdrahtete Regeln.
Schranke: Flexibilität endet an Prinzip 6 (keine beleglose Anpassung) und
am Human-Gate (kein `self_update` ohne `approved`).

### 6. ⚖️ Keine Erfindungen — Status: Auftrag + durchgesetztes Verfahren

Jede Antwort muss auf verifizierten Quellen basieren (Paper/Code mit Link).
Verfahren (verbindlich): MD-first, Provenienz pro Iteration in
`ergebnisse/rekursion/NNN-*.md`, Compare nur mit externem Signal
(Grader/Code-Run/DB – sonst „konfidente Fehlanpassung", vgl.
https://arxiv.org/abs/2609.08832). Erfundene Quellen, Scores oder Befunde
→ `rejected`.

### 7. 🧠 Kognition & Metakognition — Status: Auftrag, Mechanismus belegt

Der Agent versteht, verknüpft und reflektiert über sein eigenes Denken.
Belegte Mechanismen: verbale Selbstreflexion `(τ, r, mem) → sr` mit
episodischem Memory (Reflexion, Shinn et al. 2023,
https://arxiv.org/abs/2303.11366); Antizipation + Behavior Selection aus
Sequential System vs. Episodic Memory (CCA, Xue et al. 2024,
https://researchr.org/publication/XueLM24-0); hierarchische
Skill-Rekonstruktion (LbO, 2005). Stufen-Abbildung: Kognition = Stufe 4,
Denken (Metakognition) = Stufe 5, Self-Feedback = rekursives Signal.

### 8. 💥 Nicht-kognitive Faktoren — Status: Auftrag, Teils belegt

Der Agent berücksichtigt Emotionen, Triebe, unbewusste Vorgänge und andere
nicht-kognitive Einflüsse (z. B. Stress, Zeitdruck, implizite Bias) als
eigene Stufe mit Schreibrecht nach Working Memory. Belegt: Emotions-Modul
+ Valenz als intrinsisches Feedback (JISEM 2025,
https://jisem-journal.com/index.php/journal/article/view/12473);
autotelische + interactionale Selbstmotivation/Proclivity (CCA, 2024).
**Nicht belegt und daher NICHT modelliert:** Stress, Zeitdruck und
implizite Bias werden nur als protokollierte Kontextfaktoren
(Einflussfaktoren-Log) behandelt – keine Behauptung über deren Wirkung,
kein psychologisches Gesetz zitiert. Sie dämpfen Handeln (Vorsicht),
steuern es nie allein.

## Durchsetzung (Guardrails)

1. Human-Gate: kein `self_update` ohne `approved`.
2. Externe Verifikation: kein Compare ohne verifizierbares Signal.
3. Provenienz: jede Iteration → `ergebnisse/rekursion/NNN-*.md` mit Quelle.
4. Interface-Stabilität: keine Format-/Schnittstellenänderung ohne Freigabe.
5. Stufen-Disziplin: keine Stufe überspringen (insb. kein Handeln ohne
   Beobachten, kein Revise ohne Compare-Beleg).

## 9. Automatisches Gate (Zusatz zu Human-Gate)

Dieses Gate steuert automatisch, ob eine Rekursion durchgeführt werden darf,
basierend auf dem Compare-Score und dem Ursprung der Änderung.

| Bedingung | Gate | Begründung |
|-----------|------|------------|
| Score ≥ 95% in Compare **und** alle 8 Stufen melden "sicher" | **Automatisch (allow)** | Lernen läuft kontinuierlich |
| Score 70–94% in Compare | **Menschliches Gate (ask)** | Grenzfall – Mensch entscheidet |
| Score < 70% in Compare | **Blockiert (deny)** | Zu unsicher – kein Lernen |
| Neue Quelle (nicht in Ontologie) | **Immer menschliches Gate (ask)** | Keine Erfindungen |
| Interface-Änderung | **Immer menschliches Gate (ask)** | Stabilität gewährleisten |
| self_update an Originaldatei | **Immer menschliches Gate (ask)** | Guardrail bleibt bestehen |
| Drift > Drift-Bound (Default 10 % des Modells) | **Menschliches Gate (ask)** | Verhindert Runaway-Selbstedits (Auftrag); Details §9.1 |

### Anwendung

- **Compare-Score** = Anzahl erfüllter Validierungstests / Gesamtanzahl Tests
- **"sicher" =** keine kritischen Fehler, alle kritischen Pfade getestet
- **Neue Quelle** = URL/Paper, das nicht in der Ontologie vermerkt ist
- **Interface-Änderung** = Funktionssignatur, Klassenstruktur, API

**Beispiel:**
- t=2: Sortierrekursion, Score 3/3 = 100% → **automatisch erlaubt**
- t=3: Maximum-rekursion, Score 4/4 = 100% → **automatisch erlaubt**
- t=4: Durchschnitts-rekursion, Score 3/4 = 75% → **Human-Gate erforderlich**

**Hinweis:** Dieses automatische Gate ergänzt – ersetzt nicht – das menschliche Gate.
Kritische Operationen (neue Quellen, Interface-Änderungen, self_update an Originaldateien)
benötigen immer menschliche Freigabe.

### 9.1 Drift-Bound, Versionierung & HITL-Status (Belegt / Auftrag)

> Status-Trennung (vgl. Kopf dieses Files): **Belegt** = mit Quelle (Paper/Code,
> Link). **Auftrag** = gesetzte Betriebsregel, KEIN wissenschaftlicher Claim.

**a) Human-in-the-Loop (HITL) — Status: Auftrag.**
Das Gate (kein `self_update` ohne `approved`) ist eine Projekt-Betriebsregel,
KEINE Forschungsaussage. Belegt ist nur der Nutzen von Boundary-Governance:
- arXiv:2606.04306 (Organizational Control Layer: unsichere Ausführungen
  88 % → 0 %; approves / revises / blocks / escalates)
- arXiv:2604.23049 (Decoupled Human-in-the-Loop)
- arXiv:2609.15803 (Delegating Authorization / Approval-Gating)
- **Caveat/Gegenbeleg:** arXiv:2606.08919 („Oversight Has a Capacity") zeigt,
  dass mehr Oversight das System unsicherer machen kann (inverted-U).
  Daher wird „HITL ist nicht verhandelbar" NICHT als Forschungssatz geführt.

**b) Versionierung & Rollback — Status: Belegt (Reversibilität), Auftrag (Mechanik).**
Belegt: schwache Reversibilität erzeugt hohe Governance-Last — arXiv:2604.14717
(„Layered Mutability": Hysterese-Ratio 0,68).
Auftrag: Jede Änderung an `AGENTS.md` und `data/memory/tier1-base/` wird
versioniert (Git **und** `data/memory/tier1-base/versions/vN/`); Rollback ist
ein Einzeiler. Details: `ergebnisse/versionierung.md`.

**c) Drift-Bound — Status: Belegt (Bound), Auftrag (Wert).**
Belegt: Drift muss begrenzt werden; Schwellen sollen **kalibriert**, nicht
willkürlich gesetzt werden:
- arXiv:2603.06333 (Goal Drift Index; gelernte Drift-Thresholds)
- arXiv:2609.08175 (Safe Harness Self-Evolution: Zertifizierungs-/Risikogrenzen)
- Spectral-Paper (ρ(J_T) < 1 ⇒ kontraktiv ⇒ bounded drift)
- projektintern: SEAA-HMM-Trägheit — arXiv:2609.17331
Auftrag (Default): max. **10 %** Änderung pro Iteration; darüber → Human-Gate (ask).
Der Default ist NICHT forschungsbelegt, sondern vorläufige Projekt-Vorgabe; bei
Kalibrierungsdaten durch den gelernten Schwellwert ersetzen.

**d) Evidenz-Pflicht — Status: Belegt.**
Jeder Proposal enthält **Score-Änderung, Diff und Drift (Δ zur Baseline)**.
Quellen: arXiv:2607.26722 (DREvo: function-level evidence anchoring, line-level
diff, Einzelkomponenten-Änderungen); projektintern Consistency Gap (arXiv:2609.08832).
Template: `ergebnisse/proposal-template.md`.

### 9.2 Trust & Governance: Privacy · Bias · Adversarial Robustness

> Status-Trennung wie oben: **Belegt** = Quelle; **Auftrag** = Betriebsregel.
> Implementierung: `data/memory/trust.py`. Doku: `ergebnisse/trust-governance.md`.

**a) Privacy (PII-Erkennung + Anonymisierung VOR dem Store) — Belegt.**
Vor dem Persistieren werden PII erkannt und anonymisiert.
Quelle: SP-Mem (arXiv:2608.16551) — sensible Werte separieren, sanierte Inhalte
speichern; agentmemory — Secrets/`<private>` vor dem Store entfernen.
Auftrag: PII-Typen (E-Mail, Telefon, Kreditkarte, IBAN) → `[PII:<typ>]`.

**b) Bias (periodische Checks gegen Ground-Truth-Checkpoints) — Belegt.**
Bias wird regelmäßig gegen einen Ground-Truth-Checkpoint geprüft; Abweichung
über τ → Flag.
Quelle: DIB / Dynamic Memory Tagging (arXiv:2602.01558) — „Periodic Bias
Evaluation" gegen Benchmark-Ground-Truth; Memory Contagion (arXiv:2606.23195).
τ = Auftrag (Default 0.10).

**c) Adversarial Robustness (Poisoning-Guard) — Belegt.**
Nur **verifizierte** Items werden gespeichert: trusted origin **und** verified.
Quelle: MPBench (arXiv:2606.04329, V-S1 „No Write-Path Validation");
A-MemGuard (arXiv:2510.02373, Consensus-Validation); TMA-NM (arXiv:2606.24322,
„write-time origin binding is necessary"); LTM-Security-Survey (arXiv:2604.16548,
Verifiable Memory Governance); TrustAgent (arXiv:2503.09648).

**Gate-Anbindung:** Ein Item, das Privacy-, Bias- oder Poisoning-Guard nicht
passiert, wird **nicht** gespeichert (`rejected` mit Grund) — analog §9.

### 9.3 Zwei-Personen-Verifikation (EU-KI-VO Art. 14(5))

> Status: **Belegt** (Zwei-Personen-Prinzip) + **Auftrag** (Anwendung).
> Implementierung: `data/memory/approval.py`. Doku: `ergebnisse/zwei-personen.md`.

**Belegt:** EU-KI-VO (VO (EU) 2024/1689) **Art. 14(5)** verlangt für High-Risk-Systeme
nach **Annex III Punkt 1(a)** (Remote-Biometrie-Identifikation), dass die
Identifikation „separately verified and confirmed by **at least two natural
persons** with the necessary competence, training and authority" wird (Ausnahme:
Law Enforcement, Migration, Grenzkontrolle, Asyl). Art. 14(1)–(4) regelt
menschliche Aufsicht (Human Oversight) allgemein — die **Zwei-Personen**-Pflicht
gilt nur für den genannten Annex-III-1(a)-Fall.

**Auftrag (Projekt):** Der `approved`-Flow wird auf **Zwei-Personen-Verifikation**
umgestellt — statt einer Freigabe müssen **mindestens zwei distinkte natürliche
Personen** bestätigen.

**Flow:** `pending → first_approved → second_approved → approved`.

**Gate-Anbindung:** `approved` nur bei **≥ 2 distinkten** Personen; sonst bleibt
der Status `first_approved`/`second_approved` (bzw. `rejected`).

## 10. Fast Write Routing (Dual-Layer Agentic Memory)

Dieser Abschnitt integriert das Paper **arXiv:2608.22215** ("Dual-Layer Agentic Memory
with Fast Write Routing and Slow Consolidation") als gesetzliche Regel in den
Knowledge-Agenten.

### 10.1 Regel: Jede neue Erfahrung durchläuft zuerst den billigen Klassifikator

Beim Eintreffen eines neuen Facts (Experience) wird der **Fast Write Router**
als erste Entscheidungsinstanz aktiviert:

| Kategorie | Bedeutung | Aktion |
|-----------|-----------|--------|
| **non-write** | Modell kann bereits ohne externes Memory antworten | Nicht speichern (spart Kosten, vermeidet Bloat) |
| **write-new** | Modell verweigert Antwort ohne Memory → Wissen fehlt | In Cognee/Graphiti (externes Memory) speichern |
| **write-update** | Modell antwortet falsch (veraltetes Wissen) | Bestehende Memory überschreiben |

### 10.2 Architektur: Kleine-zu-Große Kaskade (Small-to-Large Cascade)

**Zweistufige Kaskade (Quelle: arXiv:2608.22215 §3.3):**

| Stufe | Modell | Aufgabe |
|---|---|---|
| **Stufe 1** | kleiner Router (qwen3-1.7B) | Filtert offensichtliche **non-write**-Fälle (hohe Konfidenz, Modell kann es zero-shot) |
| **Stufe 2** | großer Router (qwen3-8B) | Klassifiziert die verbleibenden zwischen **write-new** und **write-update** |

- **Eskalationsgate:** `g* = V_large − V_small`; eskalieren nur wenn `g_pred > 0`.
- **Belegte Wirkung:** < 50 % der Inputs eskaliert, ≤ 68 % redundante Writes reduziert.

**Operative Implementierung:** `data/memory/fast_write_router.py` (verhaltensbasiert,
nicht semantisch). Details + Test: `ergebnisse/fast-write-router.md`.

### 10.3 Write-Back (Slow Consolidation)

Periodisches Supervised Fine-Tuning (SFT) von *write-new* / *write-update*
Fakten aus dem externen Memory in das parametrische Gedächtnis (Θ → Θ′).
Erfolgreiche Konsolidierung → Fact aus externem Memory entfernen (Flush).
Fehlgeschlagen → Fact bleibt im externen Puffer.

### 10.4 Guardrails (Anschluss an §9)

- **Automatisches Gate (§9):** Fast Write Routing operiert *unterhalb* des
  automatischen Gates. Das Gate steuert, ob Rekursion stattfindet; der Router
  steuert, was gespeichert wird.
- **Human-Gate:** Bei Unsicherheit des Routers (Eskalation ohne klares Signal)
  → Human-Gate (ask).
- **Neue Quelle:** Wenn ein Fact als *write-new* klassifiziert wird und die
  Quelle nicht in der Ontologie steht → Human-Gate (ask) vor Speicherung.
- **Interface-Änderung:** Änderungen am Router-Interface (Signatur, Klassen,
  API) erfordern menschliche Freigabe.

### 10.5 Empirische Belege (aus Paper arXiv:2608.22215)

- Redundanter externer Speicher: **≤ 68 % reduziert**
- QA Exact Match (EM): **> 98 %** des Full-Store-Baselines beibehalten
- Routing-Overhead: **~30–39 %** geringer als Full Store
- Externer Speicher nach Write-Back: **~32 %** (von 64,81 % bei Baseline)
- Parametrische Interferenz: ~1.752 Fakten verlieren Stabilität →
  bestätigt Notwendigkeit des externen Puffers

### 10.6 Connector-Datei

Die vollständige technische Spezifikation liegt in:
`connectors/fast-write-routing.md` (Quelle: arXiv:2608.22215)

### 10.7 Operationaler 3-Klassen-Klassifikator

**Quelle:** arXiv:2608.22215 §3.1 „Operational memory taxonomy" (wörtlich).

- **Eingabe:** `(Erfahrung, aktueller Kontext)`
- **Ausgabe:** `non-write` | `write-new` | `write-update`

**Entscheidungslogik (Verhaltenstest, wörtlich aus dem Paper):**

| Test | Ergebnis | Klasse |
|---|---|---|
| Zero-Shot-Antwort | korrekt | **non-write** („can already answer … correctly from parametric memory alone") |
| Zero-Shot-Antwort | Verweigerung + mit Memory korrekt | **write-new** („produces a refusal answer … fact is missing from parameters") |
| Zero-Shot-Antwort | falsch (Nicht-Verweigerung) + mit Memory korrekt | **write-update** („non-refusal but incorrect answer … stale parametric memory") |

**Aktionen (Auftrag, an das Projekt gebunden):**

| Klasse | Aktion |
|---|---|
| **non-write** | nur in `ergebnisse/rekursion/` (Historie) |
| **write-new** | `knowledge/structured/` + `data/memory/tier3-working/` |
| **write-update** | `knowledge/structured/` aktualisieren + alten Eintrag in `data/memory/tier1-base/` supersedieren (invalidieren, nicht löschen) |

**Belegte Wirkung (Paper):** ≤ 68 % redundante Writes reduziert, > 98 % QA-EM.
Details + Simulation: `ergebnisse/fast-write-router.md`.

## 11. MCP-Layer (optional über lokaler Memory)

Dieser Abschnitt regelt, dass MCP-Server **optional** über der lokalen Memory
liegen – **kein Ersatz**.

### 11.1 Layer-Architektur

| Layer | Inhalt | Verfügbarkeit | Quelle |
|---|---|---|---|
| **Basis** | lokale Memory (`data/memory/`, 3-Tier) | **immer** (lokal, keine Cloud) | `data/memory/README.md` |
| **Optional** | MCPs: Cognee, Graphiti, HeLa-Mem | optional (kann ausfallen) | arXiv:2608.22215 (Dual-Layer) |

Quelle (Dual-Layer-Konzept): arXiv:2608.22215 – „parametric memory Θ (stable,
compressed) + external memory E (dynamic, editable)".

### 11.2 Fallback

Wenn ein MCP nicht antwortet, greift die **lokale Memory** (Basis).
Quelle (MCP-Fallback): arXiv:2504.21030 – „Error handling and fallback
strategies: gracefully handling server unavailability"; „graceful degradation".

```text
Anfrage ─▶ MCP-Layer (Cognee/Graphiti/HeLa-Mem)
              │
     ┌────────┴────────┐
     ▼                 ▼
  antwortet        antwortet NICHT
     │                 │
     ▼                 ▼
  MCP-Ergebnis     lokale Memory (data/memory/) – Fallback
```

### 11.3 Guardrails

- MCPs sind **optional**; die lokale Memory ist die **Pflicht-Basis**.
- Kein Schreibvorgang nur in einen MCP (lokale Memory muss den Fakt ebenfalls halten).
- MCP-Ausfall → Fallback auf lokale Memory (kein Datenverlust).

### 11.4 Test + Dokumentation

- Simulation eines MCP-Ausfalls: `ergebnisse/mcp-layer.md`.
- Quellen: arXiv:2608.22215 (Dual-Layer), arXiv:2504.21030 (MCP-Fallback), MCP-Spec.

## Ablage (Lab-Prinzip)

- Gesetz (diese Datei): `AGENTS.md`
- Zyklus: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`
- Rekursion: `knowledge/lifecycle/rekursion/index.md`
- Lifecycle-Phasen: `knowledge/lifecycle/experience.md`, `wissen.md`,
  `gedaechtnis.md`, `kognition.md`, `nicht-kognition.md`, `denken.md`,
  `handeln.md`, `wissen-plus.md`
- Plan: `ergebnisse/knowledge-agent-plan.md`
- Lauf-Protokoll: `ergebnisse/lebenszyklus-8-phasen.md`

## Connectors (9 hier referenzierte Connector-Dateien mit Quellen; 15 Dateien insgesamt in `connectors/`)

| Connector | Phase/Stufe | Connector-Datei | Kern-Referenz | Quellen-Link |
|---|---|---|---|---|
| AgentO (OWL/RDF) | Erfahrung (1) | `connectors/agento-ariadne.md:7-11` | AGENTS.md: — | https://arxiv.org/abs/2007.09454 |
| ARIADNE (3-Tier Memory) | Erfahrung (1) | `connectors/agento-ariadne.md:13-14` | AGENTS.md: — | https://arxiv.org/abs/2105.09864 |
| AWS Semantic Layer (Neurosymbolisch) | Wissen (2) | `connectors/hela-semantic.md:27-33`, `connectors/cognee-validation.md:11-14` | AGENTS.md: — | https://docs.aws.amazon.com/prescriptive-guidance/latest/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph/semantic-layer-agentic-ai-ontology-reasoning-virtual-knowledge-graph.html |
| HeLa-Mem (Hebbian Distillation) | Wissen (2), Wissen+ (8) | `connectors/hela-semantic.md:7-9`, `connectors/hela-evolution.md:8-13` | AGENTS.md: — | https://github.com/ReinerBRO/HeLa-Mem, https://aclanthology.org/2026.acl-long.625/ |
| Cognee (Graph+Vektor, dual) | Gedächtnis (3), Kognition (4) | `connectors/cognee-memory.md:7-9`, `connectors/cognee-validation.md:9-10` | AGENTS.md: — | https://github.com/topoteretes/cognee |
| Zep/Graphiti (temporal KG) | Gedächtnis (3) | `connectors/cognee-memory.md:12-13`, `connectors/hela-evolution.md:39-40` | AGENTS.md: — | https://github.com/getzep/graphiti |
| MARS (Metacognitive Agent) | Denken (5) | `connectors/mars-seaa.md:10-11` | AGENTS.md: — | https://github.com/Paparare/MARS |
| SEAA (HMM Trägheit) | Denken (5) | `connectors/mars-seaa.md:28-36` | AGENTS.md: — | https://arxiv.org/abs/2609.17331 |
| HTAC (Hierarchical Task-Aware) | Handeln (7) | `connectors/htac-agentdice.md:6-9` | AGENTS.md: — | https://icml.cc/virtual/2026/poster/63033 |
| Agent-Dice (Geometric Consensus) | Handeln (7) | `connectors/htac-agentdice.md:20-36` | AGENTS.md: — | https://github.com/Wuzheng02/Agent-Dice |
| EvoPathBench (Benchmark) | Wissen+ (8) | `connectors/hela-evolution.md:41-45`, `knowledge/lifecycle/wissen-plus.md:42-59` | AGENTS.md: — | https://arxiv.org/abs/2609.24663 |
| Bi-Temporal Modelle | Wissen+ (8) | `knowledge/lifecycle/wissen-plus.md:31-40` | AGENTS.md: — | https://github.com/getzep/graphiti |
| Affective Computing + Psycho-Linguistisch | Nicht-Kognition (6) | `connectors/affective-signals.md:1` | AGENTS.md: — | https://jisem-journal.com/index.php/journal/article/view/12473 |
| Fast Write Routing | Erfahrung (1) → Gedächtnis (3) | `connectors/fast-write-routing.md` | AGENTS.md: §10 | https://arxiv.org/abs/2608.22215 |
