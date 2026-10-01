# Automatisches Gate – Gesetz in AGENTS.md verankert

> Ergänzung zum Human-Gate, definiert in `AGENTS.md: §9`
> Erstellt: 2026-09-30
> Lab-Prinzip: Keine Erfindungen – nur was tatsächlich in den Dateien steht.

---

## 1. Neues Gesetz: §9 Automatisches Gate in `AGENTS.md`

### Vollständiger Text (in `AGENTS.md` nach §8 eingefügt)

| Bedingung | Gate | Begründung |
|---|---|---|
| Score ≥ 95% in Compare **und** alle 8 Stufen melden „sicher" | **Automatisch (allow)** | Lernen läuft kontinuierlich |
| Score 70–94% in Compare | **Menschliches Gate (ask)** | Grenzfall – Mensch entscheidet |
| Score < 70% in Compare | **Blockiert (deny)** | Zu unsicher – kein Lernen |
| Neue Quelle (nicht in Ontologie) | **Immer menschliches Gate (ask)** | Keine Erfindungen |
| Interface-Änderung | **Immer menschliches Gate (ask)** | Stabilität |
| self_update an Originaldatei | **Immer menschliches Gate (ask)** | Guardrail bleibt bestehen |

### Anwendung

- **Compare-Score** = Anzahl erfüllter Validierungstests / Gesamtanzahl Tests
- **"sicher" =** keine kritischen Fehler, alle kritischen Pfade getestet
- **Neue Quelle** = URL/Paper, das nicht in der Ontologie vermerkt ist
- **Interface-Änderung** = Funktionssignatur, Klassenstruktur, API

### Beispiel

- t=2: Sortierrekursion, Score 3/3 = 100% → **automatisch erlaubt**
- t=3: Maximum-rekursion, Score 4/4 = 100% → **automatisch erlaubt**
- t=4: Durchschnitts-rekursion, Score 3/4 = 75% → **Human-Gate erforderlich**

### Hinweis

- Dieses automatische Gate **ergänzt** – ersetzt nicht – das menschliche Gate.
- Kritische Operationen (neue Quellen, Interface-Änderungen, self_update an Originaldateien)
- benötigen immer menschliche Freigabe.

---

## 2. Alle aktualisierten Stellen

### `AGENTS.md` (Zeile 104–119)

- **Vorher:** Kein automatisches Gate definiert
- **Nachher:** §9 Automatisches Gate (siehe Text oben)
- **Beweis:** Datei `AGENTS.md` Zeile 104–119 enthält nun die vollständige Tabelle

### `knowledge/lifecycle/rekursion/index.md` (Zeile 156)

- **Vorher:** Kein Verweis auf automatisches Gate
- **Nachher:** Punkt 2 fügt Verweis auf AGENTS.md: §9 hinzu
- **Beweis:** Datei `index.md` Zeile 156 erweiterter Text mit Gate-Logik

### `knowledge/lifecycle/rekursion/wissenszyklus-8-stufen.md` (Zeile 131)

- **Vorher:** `Human-Gate (approved)` nur
- **Nachher:** `Human-Gate (approved), Automatisches Gate (AGENTS.md: §9), externes Signal, Provenienz`
- **Beweis:** Datei `wissenszyklus-8-stufen.md` Zeile 131 enthält nun erweiterte Guardrails

### `skills/recursive-improve/SKILL.md` (Zeile 91)

- **Vorher:** `self_update` nur nach menschlicher Freigabe des Diffs.
- **Nachher:** `self_update` nur nach menschlicher Freigabe des Diffs. + Automatisches Gate (AGENTS.md: §9) Score-basierte Entscheidung
- **Beweis:** Datei `skills/recursive-improve/SKILL.md` Zeile 91 erweiterte Guardrails

---

## 3. Test-Simulationen

### Test 1: Compare-Score 96%

| Bedingung | Gate | Ergebnis |
|---|---|---|
| Score ≥ 95% in Compare **und** alle 8 Stufen melden „sicher" | **Automatisch (allow)** | ✅ Automatisch – Lernen läuft kontinuierlich |

### Test 2: Compare-Score 80%

| Bedingung | Gate | Ergebnis |
|---|---|---|
| Score 70–94% in Compare | **Menschliches Gate (ask)** | ✅ Human-Gate – Grenzfall, Mensch entscheidet |

### Test 3: Neue Quelle

| Bedingung | Gate | Ergebnis |
|---|---|---|
| Neue Quelle (nicht in Ontologie) | **Immer menschliches Gate (ask)** | ✅ Human-Gate – Keine Erfindungen |

### Zusammenfassung

| Simulierung | Getroffenes Gate | Begründung |
|---|---|---|
| Score 96% | Automatisch | Über 95% – kontinuierliches Lernen |
| Score 80% | Menschliches Gate | Grenzfall (70–94%) |
| Neue Quelle | Human-Gate | Ontologie-Prinzip – keine Erfindungen |

---

## 3. Fazit

- ✅ Automatisches Gate in `AGENTS.md: §9` verankert
- ✅ Alle 4 Ziel-Dateien aktualisiert mit Verweis auf neue §9
- ✅ 3 Simulations-Tests dokumentiert
- ✅ Human-Gate bleibt für kritische Aktionen bestehen
- ✅ Keine Erfindungen – alle Belege in Dateien verankert

---

**Status:** Gesetz erstellt, Stellen aktualisiert, Tests simuliert.