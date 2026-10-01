# Mitwirken (CONTRIBUTING)

> Grundlage: [`AGENTS.md`](AGENTS.md) (Gesetz). Dieses Dokument wiederholt nur,
> was dort und in den Projekt-Docs steht – keine Erfindungen.

## Grundregeln (aus AGENTS.md)

1. **Keine Erfindungen:** jede Aussage braucht eine verifizierte Quelle
   (Paper/Code mit Link). Erfundene Quellen/Scores → `rejected`.
2. **MD-first.**
3. **Human-Gate:** kein `self_update` ohne `approved`.
4. **Externe Verifikation:** kein Compare ohne verifizierbares Signal
   (Grader / Code-Run / DB).
5. **Provenienz:** jede Iteration → `ergebnisse/rekursion/NNN-*.md` mit Quelle.
6. **Interface-Stabilität:** keine Format-/Schnittstellenänderung ohne Freigabe.
7. **Stufen-Disziplin:** keine Stufe überspringen (kein Handeln ohne
   Beobachten, kein Revise ohne Compare-Beleg).

## Ablauf einer Änderung (Rekursion)

1. **Ziel `g` + Task-Input** definieren (Prinzip 2: „Aufgabe = Du").
2. **Proposal** nach [`ergebnisse/proposal-template.md`](ergebnisse/proposal-template.md):
   Score-Änderung, Diff, Drift (Δ zur Baseline), Quellen.
3. **Gate prüfen** (`AGENTS.md` §9 / §9.1):
   - Score ≥ 95 % + alle 8 Stufen „sicher" → automatisch (allow)
   - Score 70–94 % → Human-Gate (ask)
   - Score < 70 % → blockiert (deny)
   - neue Quelle / Interface-Änderung / `self_update` / Drift > Bound → Human-Gate (ask)
4. **Ergebnis + Freigabe** in `ergebnisse/rekursion/NNN-*.md` dokumentieren:
   `pending | approved:<wer, wann> | rejected:<grund>`.
5. **Versionierung:** Änderungen an `AGENTS.md` und `data/memory/tier1-base/`
   versionieren (Git **und** `tier1-base/versions/vN/`); Rollback als Einzeiler
   — Details in [`ergebnisse/versionierung.md`](ergebnisse/versionierung.md).

## Neue Inhalte anlegen

- **Connector:** Datei in `connectors/` (Quellen-Link angeben) und in der
  Connector-Tabelle in `AGENTS.md` referenzieren.
- **Skill:** `skills/<name>/SKILL.md`.
- **Strukturiertes Wissen:** `knowledge/structured/`.
- **Recherche/Test/Analyse:** `ergebnisse/`.

## Status-Konvention

- **`Belegt`** = mit Quelle (Paper/Code, Link).
- **`Auftrag`** = gesetzte Betriebsregel, **kein** wissenschaftlicher Claim.

## Lizenz

MIT (Copyright (c) 2026 batnini). Beiträge stehen unter derselben Lizenz.
