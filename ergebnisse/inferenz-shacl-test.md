# Test: Inferenz-Schicht macht Invalidität sichtbar (Aufgabe 4)

> Datum: 2026-10-01
> Zweck: Zeigen, dass SHACL **allein** (auf dem expliziten Graphen) eine
> Invalidität **nicht** erkennt, die Inferenz-Schicht sie aber **sichtbar** macht.
> Quelle der Mechanik: Robaldo & Batsakis (Swansea University), Semantic Web
> Journal — siehe `ergebnisse/inferenz-shacl.md`.

## Ehrlichkeits-Hinweis

Dies ist eine **eigenständige Simulation** des Musters „Inferenz → Validierung".
**Hinweis (2026-10-04):** Inzwischen ist eine **echte** Engine-Ausführung
(`rdflib` + `pyshacl`) verfügbar — siehe Abschnitt „Echte Ausführung mit Engine"
in `ergebnisse/inferenz-shacl.md` und `tests/test_shacl_inferenz.py`. Die
Simulation hier bleibt als Vorstufe erhalten; die konkreten Triple-Mengen sind
illustrativ, nicht normativ.

## Test-Harness (Python)

```python
from datetime import datetime
def show(t): return f"{t[0]} {t[1]} {t[2]}"

# ---------- Test 1: Zeitintervall endet vor Start (Paper-Beispiel) ----------
explicit = {
    ("i1","hasBeginning","b1"), ("b1","inXSDDateTime","2024-05-10T00:00:00"),
    ("i1","hasEnd","e1"),       ("e1","inXSDDateTime","2024-05-01T00:00:00"),
}
def rule_negative_duration(triples):
    # CONSTRUCT { ?i :hasNegativeDuration true }
    # WHERE { ?i :hasBeginning/:inXSDDateTime ?tb . ?i :hasEnd/:inXSDDateTime ?te . FILTER(?te < ?tb) }
    def val(i, prop):
        for (s,p,o) in triples:
            if s==i and p==prop:
                for (s2,p2,o2) in triples:
                    if s2==o and p2=="inXSDDateTime": return o2
    out=[]
    for (i,p,o) in list(triples):
        if p=="hasBeginning":
            tb, te = val(i,"hasBeginning"), val(i,"hasEnd")
            if tb and te and datetime.fromisoformat(te) < datetime.fromisoformat(tb):
                out.append((i,"hasNegativeDuration","true"))
    return out
def shape_S1(triples):
    return [t for t in triples if t[1]=="hasNegativeDuration" and t[2]=="true"]

print("=== Test 1: Intervall endet vor Start ===")
print("SHACL allein (explizite Triples):     Verletzungen =", shape_S1(explicit))
inferred = explicit | set(rule_negative_duration(explicit))
print("Inferierte Triples (Regel R1):        ", [show(t) for t in rule_negative_duration(explicit)])
print("Nach Inferenz-Schicht:                Verletzungen =", [show(t) for t in shape_S1(inferred)])

# ---------- Test 2: Transitive 'before'-Kette mit Zyklus (Allen) ----------
explicit2 = {("i1","before","i2"),("i2","before","i3"),("i3","before","i1")}
def rule_transitive(triples):
    # CONSTRUCT { ?a :before ?c } WHERE { ?a :before ?b . ?b :before ?c }, bis Fixpunkt
    t=set(triples); new=[]; changed=True
    while changed:
        changed=False
        for (a,p,b) in list(t):
            if p!="before": continue
            for (b2,p2,c) in list(t):
                if b2==b and p2=="before" and (a,"before",c) not in t:
                    t.add((a,"before",c)); new.append((a,"before",c)); changed=True
    return new
def shape_S2(triples):
    return [t for t in triples if t[1]=="before" and t[0]==t[2]]

print("\n=== Test 2: 'before'-Zyklus (Transitivität) ===")
print("SHACL allein (explizite Triples):     Verletzungen =", shape_S2(explicit2))
new = rule_transitive(explicit2)
print("Inferierte Triples (Regel R2):        ", sorted(show(t) for t in new))
print("Nach Inferenz-Schicht:                Verletzungen =", sorted(show(t) for t in shape_S2(explicit2|set(new))))
```

## Reale Ausgabe

```text
=== Test 1: Intervall endet vor Start ===
SHACL allein (explizite Triples):     Verletzungen = []
Inferierte Triples (Regel R1):         ['i1 hasNegativeDuration true']
Nach Inferenz-Schicht:                Verletzungen = ['i1 hasNegativeDuration true']

=== Test 2: 'before'-Zyklus (Transitivität) ===
SHACL allein (explizite Triples):     Verletzungen = []
Inferierte Triples (Regel R2):         ['i1 before i1', 'i1 before i3', 'i2 before i1', 'i2 before i2', 'i3 before i2', 'i3 before i3']
Nach Inferenz-Schicht:                Verletzungen = ['i1 before i1', 'i2 before i2', 'i3 before i3']
```

## Interpretation

| Test | SHACL allein | Nach Inferenz-Schicht |
|---|---|---|
| 1 (Intervall endet vor Start) | 0 Verletzungen (**verpasst**) | 1 Verletzung (**erkannt**) |
| 2 (`before`-Zyklus, transitiv) | 0 Verletzungen (**verpasst**) | 3 Verletzungen (**erkannt**) |

- In beiden Fällen steht die verletzende Information **nicht** im expliziten
  Graphen; sie entsteht erst durch die Inferenz-Regel (R1/R2). Genau das
  beschreibt das Paper: die inferierten Triples sind „intermediate results",
  ohne die SHACL die Invalidität nicht findet.

## Inferenz-Kette (Provenienz, vgl. `knowledge/cognition/inference-<id>.md`)

| Regel-ID | Regel | Input-Triples | Output-Triples |
|---|---|---|---|
| R1 | `hasNegativeDuration` bei `te < tb` | `i1 hasBeginning b1`, `b1 inXSDDateTime 2024-05-10`, `i1 hasEnd e1`, `e1 inXSDDateTime 2024-05-01` | `i1 hasNegativeDuration true` |
| R2 | transitive Hülle von `before` | `i1 before i2`, `i2 before i3`, `i3 before i1` | `i1 before i3`, `i2 before i1`, `i3 before i2`, `i1 before i1`, `i2 before i2`, `i3 before i3` |

## Quellen (HTTP 200)

- https://www.semantic-web-journal.net/system/files/swj3959.pdf
- https://www.w3.org/TR/shacl-af/#SPARQLRule
