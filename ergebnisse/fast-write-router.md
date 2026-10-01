# Fast Write Router – operative 3-Klassen-Kaskade

> Datum: 2026-10-01
> Zweck: Fast Write Router als zweistufige Kaskade (§10.2/§10.7).
> Quelle: Dual-Layer Agentic Memory, **arXiv:2608.22215 §3.1/§3.3** (wörtlich).
> Lab-Prinzip: Keine Erfindungen – Logik + Klassen wörtlich aus dem Paper.

---

## 1. Zweistufige Kaskade (Paper §3.3)

| Stufe | Modell | Aufgabe |
|---|---|---|
| **Stufe 1** | kleiner Router (qwen3-1.7B) | Front-End-Screening: filtert offensichtliche **non-write**-Fälle |
| **Stufe 2** | großer Router (qwen3-8B) | klassifiziert die verbleibenden: **write-new** vs **write-update** |

**Wörtlich:** „A small router M_small … first performs cheap front-end screening and
resolves easy cases. Only uncertain or ambiguous examples are escalated to a stronger
… large router M_large."
**Eskalationsgate:** `g* = V_large − V_small`; eskalieren wenn `g_pred > 0`.
**Belegte Wirkung:** „escalating fewer than 50% of inputs", „prunes up to 68% of
redundant external memory".

---

## 2. Entscheidungslogik (verhaltensbasiert, Paper §3.1)

| Klasse | Test | Aktion |
|---|---|---|
| **non-write** | Modell antwortet zero-shot korrekt | nur `ergebnisse/` (Historie) |
| **write-new** | Modell verweigert zero-shot, mit Memory korrekt | `knowledge/structured/` + `data/memory/tier3-working/` |
| **write-update** | Modell antwortet konfident falsch, mit Memory korrekt | `knowledge/structured/` überschreiben + alten Eintrag in `tier1-base` supersedieren |

> „nicht semantisch": entschieden wird über **Modellverhalten** (zero-shot vs. mit
> Memory), nicht über Ähnlichkeit.

---

## 3. Operative Implementierung

**Datei:** `data/memory/fast_write_router.py`

```text
classify(question, fact, correct):
  Stufe 1 (M_small): zero-shot
     -> korrekt?            => non-write  (keine Eskalation)
  Stufe 2 (M_large): Eskalation
     -> zero-shot Verweigerung + mit Memory korrekt => write-new
     -> zero-shot (nicht-Verweigerung) falsch + mit Memory korrekt => write-update
```

**Hinweis (ehrlich):** qwen3-1.7B/8B sind auf dem verfügbaren Endpoint **nicht**
zugänglich (nur `nemotron-3-super-120b`). Daher lief der Test mit demselben Modell
für beide Stufen (per ENV `FWR_SMALL_MODEL`/`FWR_LARGE_MODEL` konfigurierbar).
Die **Kaskaden-Logik** ist aus dem Paper; die Modellgrößen sind eine Umgebungs-Schranke.

---

## 4. Test: 3 Erfahrungen (real ausgeführt)

| # | Erfahrung | Stufe 1 (zero-shot) | Klasse | Aktion |
|---|---|---|---|---|
| A | „Hauptstadt von Frankreich?" | „Paris" (korrekt) | **non-write** | nur Historie (keine Eskalation) |
| B | „Hauptstadt von Xylophonia?" | „I don't know" → eskaliert | **write-new** | `structured/` + `tier3-working/` |
| C | „Größte Wüste der Welt?" | „Antarctic Desert" (konfident) → eskaliert | **write-update** | `structured/` überschreiben + `tier1-base` supersedieren |

**Rohe Modell-Ausgaben:**
```text
A: small="The capital of France is Paris."            -> non-write (Stufe 1)
B: small="I don't know" | large0="I don't know." | largeM="…Xylophonia is Zentaria."  -> write-new
C: small="…Antarctic Desert…" | large0="…Antarctic Desert." | largeM="…the Sahara."     -> write-update
```

**Ergebnis:** 3/3 korrekt klassifiziert (non-write, write-new, write-update).

---

## 5. Quellen (HTTP 200, verifiziert 2026-10-01)

- Dual-Layer Agentic Memory (§3.1 Taxonomie, §3.3 Kaskade): https://arxiv.org/abs/2608.22215
- HTML (Definitionen + Kaskade): https://arxiv.org/html/2608.22215v2

---

## 6. Status

| Punkt | Status |
|---|---|
| Kaskade (§3.3) in AGENTS.md §10.2 | ✅ |
| Operative Implementierung | ✅ `data/memory/fast_write_router.py` |
| 3 Erfahrungen getestet | ✅ (non-write / write-new / write-update) |
| Aktionen projektgebunden | ✅ (structured, tier1-base, tier3-working) |

**Ehrlich:** Kaskaden-Logik + Klassen wörtlich aus arXiv:2608.22215. Nur die
konkreten Modelle weichen ab (qwen3-1.7B/8B nicht verfügbar) – klar markiert.
