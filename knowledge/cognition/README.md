# knowledge/cognition – Inferenz-Ablage der Kognition (Stufe 4)

> Lab-Prinzip, MD-first. Projekt-Doku: `knowledge/lifecycle/kognition.md`.
> Skill: `skills/cognize/SKILL.md`.
> Connector: `connectors/cognee-validation.md`.
> Auftrags-Begriffe sind als solche markiert (Auftrag, keine
> Quellen-Behauptung).

## Konvention: Inferenz-Format Prämissen → Konklusion

Jede Schlussfolgerung wird als eigene Datei (oder eigener Abschnitt mit
eindeutigem Titel) in diesem Verzeichnis dokumentiert:

```text
Prämissen:
  - P1: <Fakt/Kante> (Quelle: <Link>)
  - P2: <Fakt/Kante> (Quelle: <Link>)
Konklusion:
  - K: <neue Verknüpfung> (via: <Regel/Constraint, z. B. OWL/SHACL>)
Status: <belegt | rejected>
Grund (bei rejected): <fehlender Beleg / verletzter Constraint / ...>
```

## Pflichtfelder

1. `Prämissen` – mindestens eine belegte Prämisse mit Quellen-Link.
2. `Konklusion` – die abgeleitete Verknüpfung + Validierungsvermerk
   (Konsistenz/Constraints via OWL/SHACL).
3. `Quelle` – Link pro Prämisse (Datei, Commit, URL – keine erfundenen Links).
4. `Status` – `belegt` oder `rejected`.
5. Verwendete Schwelle dokumentieren (z. B. Fuzzy-Matching cutoff 0.80 –
   Vorgabe (Auftrag), keine Quellen-Behauptung; konfigurierbar).

Regel: Fehlen Prämissen-Beleg oder Quellen-Link → Status `rejected`.

## Status

- Angelegt, wartet auf t=1. (Auftrag)
- Noch keine Inferenzen dokumentiert; erste Iteration schreibt hierher.
