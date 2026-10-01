# ERFAHRUNG — Stufe 1 des 8-Stufen-Zyklus

> Lab-Prinzip MD-first. Legende: `[Auftrag]` = per Auftrag / AGENTS.md gesetzt,
> nicht quellenbelegt. `[Quelle]` = aus den unten genannten Quellen belegt.
> Es werden NUR die unter „Quellen" genannten Quellen zitiert.

## 1. Definition [Auftrag]

ERFAHRUNG sammelt Rohdaten aus offiziellen Quellen und legt sie unverändert ab.

Das umfasst: aufnehmen, ablegen, mit Provenienz versehen. Keine Deutung,
keine Wertung, keine Zusammenfassung.

## 2. Verfahren [Auftrag]

Aufnehmen ohne zu deuten — keine Wertung.

Die Bewertung ist nicht Teil dieser Stufe. Bewertung ist Compare
(Stufen-Disziplin per Auftrag: keine Stufe überspringen).

Schritte (Auftrag-Reihenfolge, keine Quellen-Aussage):

1. Quelle identifizieren (offizielle Quelle).
2. Rohdaten einholen.
3. Unverändert ablegen.
4. Provenienz festhalten (Quellen-Link).
5. An Working Memory übergeben (siehe Abschnitt 5).

## 3. AgentO-Mapping [Quelle]

AgentO ist eine OWL/RDF-Ontologie plus Knowledge Graph für agentische
Workflows [Quelle].

Für Stufe 1 relevant ist das standardisierte Vokabular für Agents, Tasks,
Workflows und Ressourcen-Abhängigkeiten [Quelle].

Erfahrungs-Rohdaten können mit diesem Vokabular etikettiert werden
(Ablage-Konvention, Status: [Auftrag]); das Vokabular selbst stammt aus
AgentO (Status: [Quelle]).

## 4. ARIADNE-Mapping [Quelle, als Spezifikation kennzeichnen]

ARIADNE wird hier als Spezifikation behandelt (Einordnung als Spezifikation:
Status: [Auftrag]; Inhalte: Status: [Quelle]).

Tier 1 Episodic Memory: rohe Interaktionen — Conversations, Dokumente,
API-Responses — mit Transaktionszeit-Immutabilität [Quelle].

Mapping auf ERFAHRUNG (Status: [Auftrag]): Stufe 1 entspricht Tier 1 in der
Funktion „Rohes unverändert festhalten". Über Tier 2 / Tier 3 wird in dieser
Datei keine Aussage getroffen.

## 5. Rekursionsschnittstelle [Auftrag]

Stufe 1 schreibt Rohdaten + Provenienz nach Working Memory.

Dieser Working-Memory-Eintrag ist das Signal für den nächsten Durchlauf /
die nächste Stufe.

Es wird nichts gedeutet und nichts bewertet; Deutung und Bewertung liegen
außerhalb von Stufe 1.

## 6. Input / Output [Auftrag]

Input:

- Auftrag mit Ziel `g` + Task-Input.
- Benannte offizielle Quellen (mit Link).

Output:

- Unveränderte Rohdaten in `knowledge/raw/`.
- Je Einheit: Quellen-Link + Datum + Hash (Pflichtfelder per Auftrag).
- Working-Memory-Eintrag mit Verweis auf Ablage + Provenienz.

## 7. Guardrails [Auftrag]

1. Unverändert speichern — kein Editieren, kein Kürzen, kein Paraphrasieren.
2. Jede Einheit mit Quellen-Link ablegen.
3. Keine Deutung — keine Wertung, keine Zusammenfassung, keine Kategorisierung
   über das Quellen-Vokabular hinaus ohne Freigabe.
4. Ohne Beleg-Trace + Quellen-Link + menschliche Freigabe keine neue
   Schema-/Aktions-/Interface-Behauptung (bei Verstoß: `rejected`).
5. Keine Stufe überspringen: kein Handeln ohne Beobachten, kein Revise ohne
   Compare-Beleg.

## 8. Quellen

NUR diese Quellen (keine weiteren behauptet):

- AgentO — OWL/RDF-Ontologie + Knowledge Graph für agentische Workflows;
  Vokabular: Agents, Tasks, Workflows, Ressourcen-Abhängigkeiten;
  66 Workflows aus 4 Frameworks per LLM-Verfahren;
  Use Cases: deklarative Rekonstruktion, Cross-Kontext-Reuse, Audit.
  - http://eprints.cs.univie.ac.at/8749/
  - https://ucrisportal.univie.ac.at/en/publications/agento-an-ontology-for-modeling-agentic-ai-systems/
- ARIADNE — DAEDALUS-Projekt, Univ. Oradea; 3-Tier:
  Tier 1 Episodic = rohe Interaktionen mit Transaktionszeit-Immutabilität;
  Tier 2 Semantic = Entities + Edge-Nodes mit bi-temporalen Feldern;
  Tier 3 Community = Leiden-Cluster; hier als Spezifikation behandelt.
  - https://exa.ai/library/publication/khfxyt54hk1
- Optional erwähnt: AriGraph / Ariadne IJCAI 2025
  (semantisches + episodisches Memory-Graph).
  - https://www.ijcai.org/proceedings/2025/0002.pdf
