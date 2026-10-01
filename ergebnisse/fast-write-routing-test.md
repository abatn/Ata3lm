# Fast Write Routing – End-to-End-Test (3 Erfahrungen)

> Datum: 2026-09-30
> Quelle: AGENTS.md §10, arXiv:2608.22215, connectors/fast-write-routing.md

## Test-Setup

- **Klassifikator:** Fast Write Router (qwen3-1.7B → qwen3-8B Kaskade)
- **Gates:** Automatisches Gate (§9), Human-Gate (§9/§10.4)
- **Ziel:** Simuliere 3 Erfahrungen und zeige die Routing-Entscheidung.

---

## Erfahrung A: Modell kann ohne Memory antworten → non-write

### Szenario

Ein Modell wird mit einer Frage konfrontiert, die es aus seinen parametrischen Erinnerungen bereits korrekt beantworten kann.

**Beispiel-Input:**
```
Frage: "Was ist die Hauptstadt von Frankreich?"
Antwort (Zero-Shot): "Paris" ✅ (korrekt)
```

### Routing-Entscheidung

| Schritt | Entscheidung | Quelle/Referenz |
|---------|-------------|-----------------|
| 1. Zero-Shot-Test | Modell antwortet korrekt | Paper: §3.1 |
| 2. Fast Write Router | **non-write** | Paper: §3.1 (Definition) |
| 3. Aktion | Keine Speicherung extern | AGENTS.md §10.1 |

### Gate-Analyse

| Gate | Greift? | Begründung |
|------|---------|------------|
| Fast Write Router | ✅ Ja | Klassifiziert als non-write |
| Automatisches Gate (§9) | ❌ Nein | Keine Speicherung → kein Write-Op |
| Human-Gate | ❌ Nein | Keine neue Quelle, keine Interface-Änderung |

### Ergebnis

✅ **non-write** – Das Modell kann bereits antworten → kein externer Speicher nötig. Kosten gespart, kein Bloat.

---

## Erfahrung B: Modell verweigert Antwort ohne Memory → write-new

### Szenario

Ein Modell wird mit einer Frage konfrontiert, die es aus seinen parametrischen Erinnerungen nicht beantworten kann (Wissen fehlt).

**Beispiel-Input:**
```
Frage: "Was ist die Hauptstadt von Mars?"
Antwort (Zero-Shot): "Ich weiß nicht" ❌ (Verweigerung)
Antwort (mit Memory): "Mars hat keine Hauptstadt" ✅ (korrekt)
```

### Routing-Entscheidung

| Schritt | Entscheidung | Quelle/Referenz |
|---------|-------------|-----------------|
| 1. Zero-Shot-Test | Modell verweigert | Paper: §3.1 |
| 2. Memory-Test | Antwort korrekt | Paper: §3.1 |
| 3. Fast Write Router | **write-new** | Paper: §3.1 (Definition) |
| 4. Aktion | In externes Memory schreiben | AGENTS.md §10.1 |

### Gate-Analyse

| Gate | Greift? | Begründung |
|------|---------|------------|
| Fast Write Router | ✅ Ja | Klassifiziert als write-new |
| Automatisches Gate (§9) | ⚠️ Prüft Score | Vergleicht mit Validierungsset |
| Human-Gate | ⚠️ Möglicherweise | Neue Quelle? → Human-Gate (ask) |

### Ergebnis

✅ **write-new** – Wissen fehlt → extern speichern. Falls Score ≥ 95% → automatisch erlaubt (§9). Falls neue Quelle → Human-Gate erforderlich.

---

## Erfahrung C: Modell antwortet falsch (veraltetes Wissen) → write-update

### Szenario

Ein Modell hat veraltetes Wissen und antwortet selbstbewusst falsch (kein Verweigern, sondern falsche Antwort).

**Beispiel-Input:**
```
Frage: "Wer war der erste Mensch auf dem Mond?"
Antwort (Zero-Shot): "Buzz Aldrin" ❌ (falsch – war Aldrin, nicht Armstrong)
Antwort (mit Memory): "Neil Armstrong" ✅ (korrekt)
```

### Routing-Entscheidung

| Schritt | Entscheidung | Quelle/Referenz |
|---------|-------------|-----------------|
| 1. Zero-Shot-Test | Modell antwortet falsch (nicht verweigern) | Paper: §3.1 |
| 2. Memory-Test | Antwort korrekt | Paper: §3.1 |
| 3. Fast Write Router | **write-update** | Paper: §3.1 (Definition) |
| 4. Aktion | Bestehendes Memory überschreiben | AGENTS.md §10.1 |

### Gate-Analyse

| Gate | Greift? | Begründung |
|------|---------|------------|
| Fast Write Router | ✅ Ja | Klassifiziert als write-update |
| Automatisches Gate (§9) | ⚠️ Prüft Score | Score < 70% → blockiert |
| Human-Gate | ⚠️ Möglicherweise | Interface-Änderung? → Human-Gate |

### Ergebnis

✅ **write-update** – Veraltetes Wissen überschreiben. Falls Score < 70% → blockiert (§9). Falls Interface-Änderung → Human-Gate (ask).

---

## Zusammenfassung Fast Write Routing Test

| Erfahrung | Kategorie | Gate | Ergebnis |
|-----------|-----------|------|----------|
| A | non-write | Kein Gate nötig | Keine Speicherung |
| B | write-new | Automatisches Gate + mögl. Human-Gate | Extern speichern |
| C | write-update | Automatisches Gate + mögl. Human-Gate | Bestehendes überschreiben |

**Lab-Prinzip:** Alle Entscheidungen basieren auf AGENTS.md §10 und dem Paper arXiv:2608.22215. Keine Erfindungen.
