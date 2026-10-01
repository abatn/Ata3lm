# Knowledge-Agent-Plan (Lab-Prinzip: Projekt + Skills + Connectors + Knowledge)

> Ausgabe-Datei per Auftrag. MD-first, keine Erfindungen.
> Gesetz: `AGENTS.md`. Jede Quelle mit Link (Paper, GitHub).

## 1. Struktur (angelegt)

```text
knowledge-agent/
├── AGENTS.md                                        # GESETZ: 8 Prinzipien
├── knowledge/lifecycle/rekursion/
│   ├── index.md                                     # Rekursion als Kommunikationsstruktur (5 Phasen)
│   ├── wissenszyklus-8-stufen.md                    # 8-Stufen-Zyklus, eingebettet in Rekursion
│   ├── konstrukt.md | akt.md | observe.md           # Unterphasen-Doks
│   └── compare.md | revise.md
├── skills/recursive-improve/
│   ├── SKILL.md                                     # Parent-Loop
│   └── konstrukt/ akt/ observe/ compare/ revise/    # je SKILL.md
├── connectors/
│   ├── goedel-agent.md | cca-framework.md | react.md
│   └── observer-agent.md | consistency-gap.md | reflexion-trace.md
└── ergebnisse/
    ├── knowledge-agent-plan.md                      # diese Datei (Ausgabe)
    ├── rekursion-plan.md                            # Phasen-Plan (t=0)
    └── rekursion/                                   # Wissen: 000–007
```

## 2. Skills

- **Parent** `skills/recursive-improve/SKILL.md`: geschlossener
  Wahrnehmungs-Handlungs-Lern-Loop über `S = (π, I, M)`.
- **Sub-Skills**: `konstrukt` (Schemata aus `M` bauen), `akt`
  (DEFINE→EXPERIMENT→OBSERVE→RELATE), `observe` (Traces→Hierarchie, ohne
  Policy-Änderung), `compare` (Pass@k vs. Pass^k, nur externe Signale),
  `revise` (VALIDATE→REFLECT→PIVOT, nur mit Freigabe).
- Loop-Namen aus Auftrag sind als Auftrags-Phasen mit Mapping markiert
  (keine Paper-Behauptungen).

## 3. Connectoren

| Connector | Quelle (verifiziert) |
|---|---|
| Gödel Agent (Selbstreferenz, Monkey Patching) | https://arxiv.org/abs/2410.04444, https://github.com/Arvid-pku/Godel_Agent |
| CCA (Interaktions-Schemata-Hierarchie) | https://researchr.org/publication/XueLM24-0, https://doi.org/10.1109/cogmi62246.2024.00027 |
| ReAct + Microsoft-Rahmen | https://arxiv.org/abs/2210.03629, https://www.microsoft.com/de-de/microsoft-copilot/copilot-101/build-ai-agents |
| Observer/LbO (TRLP 2005) | https://aaai.org/papers/0021-fs05-07-021-learning-teleoreactive-logic-programs-by-observation/ |
| Consistency Gap (AppWorld) | https://arxiv.org/abs/2609.08832, https://huggingface.co/blog/ibm-research/altk-evolve-consistency |
| Reflexion + Closed-Loop | https://arxiv.org/abs/2303.11366, https://www.mdpi.com/2075-5309/16/1/196 |
| JISEM Konstruktivismus (Emotion/Valenz) | https://jisem-journal.com/index.php/journal/article/view/12473 |

Abgrenzungen (ehrlich): TRACE-Eval vs. TRACE-Repo getrennt;
„Curator-Agent" als Rolle definiert; CCA-Paper 2024 / JISEM-Paper 2025
getrennt belegt.

## 4. Die 8 Prinzipien (Gesetz, Kurzform – Volltext: `AGENTS.md`)

1. 👁️ Beobachte ohne zu deuten (Aufnahme ohne Wertung; Verfahren belegt).
2. 📖 Aufgabe = Du (jeder Lauf braucht Ziel `g`; Wissenslücke schließen).
3. 🔄 8-Stufen-Zyklus (gesetzte Ordnung, Schritte quellenbelegt).
4. 💥 Brich die Muster (nur mit Beleg-Trace + Quelle + Freigabe).
5. ☁️ Wie eine Wolke (revidierbare Schemata; Schranke: Prinzip 6 + Human-Gate).
6. ⚖️ Keine Erfindungen (MD-first, Provenienz, externes Compare-Signal).
7. 🧠 Kognition & Metakognition (Reflexion `(τ,r,mem)→sr`, CCA-Selektion).
8. 💥 Nicht-kognitive Faktoren (Emotion/Valenz + Proclivity belegt;
   Stress/Zeitdruck/Bias nur protokolliert, nicht modelliert).

Status-Markierung in `AGENTS.md`: `Auftrag` = Betriebsregel (kein
Wissenschafts-Claim), `Belegt` = zusätzlich quellenverankert. Es wird
kein „wissenschaftlich bewiesenes Gesetz" behauptet, das nicht in den
Quellen steht.

## 5. Der 8-Stufen-Zyklus (Volldefinition: `wissenszyklus-8-stufen.md`)

1. **Erfahrung (تجربة):** Rohdaten sammeln → schreibt Working Memory.
2. **Wissen (معرفة):** in `knowledge/` strukturieren → liest Working Memory.
3. **Gedächtnis (ذاكرة):** im Memory-Connector speichern → schreibt Ontologie.
4. **Kognition (إدراك):** verstehen/verknüpfen/schließen → liest Ontologie,
   schreibt Verknüpfungen.
5. **Denken (فكر):** Metakognition → schreibt Self-Feedback.
6. **Nicht-Kognition (لا-إدراك):** Emotionen/Triebe/Unbewusstes/Stress/
   Zeitdruck/Bias → schreibt Working Memory (dämpft Handeln).
7. **Handeln (فعل):** Wissen anwenden → schreibt Aktion in Working Memory.
8. **Wissen+ (معرفة+):** revidiertes Modell zurück → neue Konstruktionen.

## 6. Rekursions-Kommunikationsstruktur

- **Observe → Compare → Revise** = rekursive Selbstbeobachtungsschleife.
- **Revise → Konstrukt → Akt** = schließt den Kreis.
- **Geteilte semantische Repräsentationen** (Ontologie, Working Memory) =
  gemeinsame „Sprache" aller Phasen/Stufen.
- **Self-Feedback** = rekursives Signal für den nächsten Durchlauf.
- **Guardrail:** nur mit menschlicher Freigabe + externer Verifikation
  (Compare auf verifizierbare Signale – sonst „konfidente Fehlanpassung").

## 7. Wissen (Provenienz)

`ergebnisse/rekursion/`: 000 Template, 001 Bootstrap (approved),
002 Konstrukt, 003 Akt, 004 Observe, 005 Compare, 006 Revise,
007 Wissenszyklus (004–007 pending Freigabe).

## 8. Quellen (vollständig)

Siehe Connector-Tabelle (§3) plus:

- https://aclanthology.org/2025.acl-long.1354/ (Gödel ACL)
- https://github.com/ShengranHu/ADAS (Gödel-Eval-Basis)
- https://arxiv.org/abs/2609.05019 (TROVE)
- https://arxiv.org/html/2602.21230 (TRACE-Eval, Abgrenzung)
- https://cea.hal.science/cea-04761173/document (CCA-Volltext)
