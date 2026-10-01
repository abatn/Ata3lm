# Knowledge-Agent (Repository: Ata3lm)

> Lab-Prinzip: **Projekt + Skills + Connectors + Knowledge. MD-first.**
> Gesetz des Projekts: [`AGENTS.md`](AGENTS.md). Dieses README fasst **nur
> zusammen, was in den Projekt-Dokumenten steht** – keine Erfindungen.

Der Knowledge-Agent ist ein wissenssammelnder Agent. Jede Aktion durchläuft
einen **8-Stufen-Zyklus** und eine rekursive Verbesserungsschleife
(Konstrukt → Akt → Observe → Compare → Revise). Jede Antwort muss auf
verifizierten Quellen (Paper/Code mit Link) basieren.

## Die 8 Prinzipien

1. 👁️ **Beobachte ohne zu deuten**
2. 📖 **Aufgabe = Du**
3. 🔄 **8-Stufen-Zyklus**
4. 💥 **Brich die Muster** (nur mit Quellen-Schranke)
5. ☁️ **Wie eine Wolke**
6. ⚖️ **Keine Erfindungen**
7. 🧠 **Kognition & Metakognition**
8. 💥 **Nicht-kognitive Faktoren**

Volldefinition: [`AGENTS.md`](AGENTS.md) (Abschnitt „Die 8 Prinzipien").

## Zyklus & Phasen

- **8 Stufen:** Erfahrung → Wissen → Gedächtnis → Kognition → Denken →
  Nicht-Kognition → Handeln → Wissen+ — `knowledge/lifecycle/`
- **5 Phasen:** Konstrukt · Akt · Observe · Compare · Revise —
  `knowledge/lifecycle/rekursion/`
- Volldefinition: `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md`

## Aufbau

```text
knowledge-agent/
├── AGENTS.md          # Gesetz (§1–§11; §9.1 Drift/Versionierung/HITL, §9.2 Trust, §9.3 Zwei-Personen)
├── README.md · CONTRIBUTING.md · LICENSE
├── knowledge/         # lifecycle/ (8 Stufen + rekursion/ 5 Phasen), structured/, cognition/
├── connectors/        # 15 Connector-Dateien (9 in AGENTS.md referenziert; Quellen je Phase/Stufe)
├── data/memory/       # Tier 1–3 (tier1-base/ +versions, tier2-index/, tier3-working/)
│                      #   + shared/ (SharedTier) + Prozesse (*.py)
├── skills/            # L4 Procedural: 14 SKILL.md + versions/vN/ (je Skill) + AUDIT.md
└── ergebnisse/        # Provenienz je Iteration (rekursion/), Analysen, Tests, Diagramme
```

## Gedächtnis (3-Tier + L4 Procedural + Shared Tier)

- **tier1-base/** — Identität, Ontologie, Kernbeziehungen, episodischer Graph
  (`episodic_graph.json`) + `versions/v1`–`v3`
- **tier2-index/** — concept-index, hub-index, evicted-index
- **tier3-working/** — Working Memory (`lru_cache.py`, max. 15; Default wertbewusste Eviction)
- **L4** — Prozeduren (`skills/`, versioniert) · **Shared** — Multi-Agent-Store (`data/memory/shared/`)

## Guardrails

- **Human-Gate:** kein `self_update` ohne `approved`.
- **Externe Verifikation:** kein Compare ohne verifizierbares Signal.
- **Provenienz:** jede Iteration → `ergebnisse/rekursion/NNN-*.md` mit Quelle.
- **Interface-Stabilität:** keine Format-/Schnittstellenänderung ohne Freigabe.
- **Stufen-Disziplin:** keine Stufe überspringen.
- **Automatisches Gate** (§9) + **Drift-Bound** (§9.1) in `AGENTS.md`.

## Mitwirken

Siehe [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Lizenz

MIT — siehe [`LICENSE`](LICENSE) (Copyright (c) 2026 batnini).
