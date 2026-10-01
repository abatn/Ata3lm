# knowledge/expansion — Ablage für WISSEN+ (Stufe 8)

> Lab-Prinzip MD-first: keine Erfindungen. Regeln mit dem Zusatz
> `(Status: Auftrag)` sind gesetzte Betriebsregeln. Erlaubte Quellen stehen
> nur im Abschnitt `Quellen`.

## Status (Status: Auftrag)

- Status: angelegt, wartet auf t=1.
- Es liegt noch keine Erweiterung vor; diese Datei definiert nur die Konvention.

## Konvention: Erweiterungs-Format inkl. Invalidierungs-Historie (Status: Auftrag)

- Eine Erweiterung ist eine Markdown-Datei in diesem Verzeichnis.
- Neue Regeln und invalidierte Regeln werden in derselben Datei geführt,
  damit die Historie erhalten bleibt.
- Es wird invalidiert statt gelöscht: alte Einträge bleiben mit
  geschlossenem Gültigkeitsfenster lesbar.
- Point-in-Time-Abfragen müssen anhand der Fenster beantwortbar bleiben.

## Pflichtfelder (Status: Auftrag)

Jede Erweiterungs-Datei enthält:

1. `Titel`
2. `Datum`
3. `Compare-Beleg` (Referenz auf den Compare-Bericht)
4. `Quelle` (eine der Quellen aus `Quellen`)
5. `Neue Regel / Erweiterung`
6. `Gültigkeitsfenster (gültig-von / gültig-bis)`
7. `Invalidierungs-Historie` (welche Regel/Fakt wann warum invalidiert,
   mit vorherigem Gültigkeitsfenster, Gegen-Evidenz und Freigabe-Status)
8. `Freigabe-Status` (`approved` oder ausstehend — ohne `approved` kein
   Rückschrieb nach Working Memory / Ontologie)
9. `Rückschrieb` (Ziel in Working Memory / Ontologie als Input neuer
   Konstruktionen)

## Quellen

- https://aclanthology.org/2026.acl-long.625/
- https://github.com/ReinerBRO/HeLa-Mem
- https://github.com/getzep/graphiti
- https://arxiv.org/abs/2609.24663
