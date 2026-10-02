# Branch-Coverage aktiviert: 100 % (Line + Branch)

> Datum: 2026-10-01 · Auftrag: „Aktiviere Branch-Coverage … nach
> pytest/coverage-Dokumentation." · Lab-Prinzip §6: nur was in den Dateien
> steht bzw. in der Doku belegt ist.

## 1. Änderung an der Konfiguration

```diff
--- a/pytest.ini
+++ b/pytest.ini
@@
+    --cov-branch
     --cov=data/memory
     --cov=skills
     --cov=ergebnisse/rekursion/solver
     --cov-report=term-missing
-    # Mindest-Score: 100 % Gesamt-Coverage (Statement-Coverage, .coveragerc)
+    # Mindest-Score: 100 % Gesamt-Coverage (Line + Branch, siehe .coveragerc)
     --cov-fail-under=100
```

```diff
--- a/.coveragerc
+++ b/.coveragerc
@@
 [run]
-# Statement-Coverage (kein Branch-Coverage) – bewusst und dokumentiert:
-# ergebnisse/ci-setup.md §2.
-branch = False
+# Line- UND Branch-Coverage (coverage-Doku: .../branch.html).
+# Aktiviert zusätzlich per `--cov-branch` in pytest.ini.
+branch = True
```

Quellen (HTTP 200 am 2026-10-01):
- `--cov-branch`: https://pytest-cov.readthedocs.io/en/latest/config.html
- Branch-Messung + `# pragma: no branch`: https://coverage.readthedocs.io/en/latest/branch.html
- Konfiguration: https://coverage.readthedocs.io/en/latest/config.html

## 2. Ausgangslage: 5 partiell abgedeckte Branches

Erster Lauf mit `--cov-branch`:

```text
data/memory/bias_monitor.py                    84   0   18   1    99%   61->74
data/memory/ingestion_hook.py                 278   0   58   1    99%   246->244
data/memory/shared/shared_memory.py           115   0   26   1    99%   142->140
data/memory/tier3-working/lru_cache.py        132   0   46   2    99%   152->144, 175->167
------------------------------------------------------------------------------------------
TOTAL                                        1195   0  264   5    99%
FAIL Required test coverage of 100% not reached. Total coverage: 99.66%
```

## 3. Die fehlenden Verzweigungen (Datei:Zeile) und ihre Tests

| Datei:Zeile | Bogen | Bedeutung | Test (neu) |
|---|---|---|---|
| `bias_monitor.py:61` | `61->74` | `for _ in range(iters)` läuft **null** mal (Schleife wird nie betreten) | `test_memory.py::test_capped_simplex_ohne_iterationen` (`iters=0`) |
| `ingestion_hook.py:246` | `246->244` | `if name not in graph.nodes:` **False** – Entity ist bereits im Graph | `test_ingestion.py::test_update_graph_knoten_bereits_vorhanden` |
| `shared/shared_memory.py:142` | `142->140` | `if len(vals) > 1:` **False** – Key hat nur eine Ausprägung (kein Konflikt) | `test_shared_memory.py::test_sync_ohne_konflikt_bei_gleichem_wert` |
| `lru_cache.py:152` | `152->144` | `if len(self.items) > before or p.stem in self.items:` **False** – Item wird sofort verdrängt | `test_lru_cache.py::test_fill_from_structured_ohne_aufnahme_bei_vollem_cache` |
| `lru_cache.py:175` | `175->167` | `if freq * crit >= 0.8:` **False** – **strukturell unerreichbar** | `# pragma: no branch` (siehe §4) |

## 4. Der unerreichbare Zweig (`lru_cache.py:175`) – ehrlich begründet

```python
freq = self.items.get(key, {}).get("hits", 0) + 1      # >= 1
crit = order[cls]                                      # 1.0 (write-update) oder 0.8 (write-new)
if freq * crit >= 0.8:  # pragma: no branch
```

`freq >= 1` und `crit ∈ {1.0, 0.8}` ⇒ `freq * crit >= 0.8` ist **immer wahr**.
Der False-Zweig kann mit den erlaubten Klassen nicht erreicht werden. Coverage.py
sieht das nicht und markiert die Zeile als partiell; die dokumentierte Direktive
`# pragma: no branch` nimmt sie aus (coverage-Doku „Structurally partial
branches"). Es wurde **keine** Zeile mit `# pragma: no cover` versteckt und
**kein** Test erfunden.

Alternative (nicht umgesetzt, wäre Verhaltensänderung → Gate §9): `order`-Werte
so ändern, dass auch `< 0.8` möglich ist.

## 5. Ergebnis nach der Anpassung

```text
make test  →  123 passed · Coverage 1195 Statements / 264 Branches
              TOTAL  1195  0  264  0  100%
              Required test coverage of 100% reached. Total coverage: 100.00%
```

Neue Tests (4) für echte Pfade + 1 dokumentierte Ausnahme:

| Test | Datei | Abgedeckter Bogen |
|---|---|---|
| `test_capped_simplex_ohne_iterationen` | `tests/test_memory.py` | `bias_monitor.py 61->74` |
| `test_update_graph_knoten_bereits_vorhanden` | `tests/test_ingestion.py` | `ingestion_hook.py 246->244` |
| `test_sync_ohne_konflikt_bei_gleichem_wert` | `tests/test_shared_memory.py` | `shared_memory.py 142->140` |
| `test_fill_from_structured_ohne_aufnahme_bei_vollem_cache` | `tests/test_lru_cache.py` | `lru_cache.py 152->144` |
| `# pragma: no branch` | `data/memory/tier3-working/lru_cache.py:175` | unerreichbar (`freq*crit >= 0.8`) |

## 6. Geänderte Dateien

| Datei | Änderung |
|---|---|
| `pytest.ini` | `--cov-branch` ergänzt, Kommentar auf „Line + Branch" |
| `.coveragerc` | `branch = True` (vorher `False`) |
| `tests/test_memory.py` | +1 Test (14) |
| `tests/test_ingestion.py` | +1 Test (17) |
| `tests/test_shared_memory.py` | +1 Test (8) |
| `tests/test_lru_cache.py` | +1 Test (10) |
| `data/memory/tier3-working/lru_cache.py` | `# pragma: no branch` + Begründung (keine Logikänderung) |
| `tests/README.md` | Branch-Coverage + neue Verzweigungen dokumentiert |
| `ergebnisse/ci-setup.md` | Branch-Coverage-Ergebnis nachgezogen |

## 7. Gate (§9)

- **Keine Verhaltensänderung** am Produktionsverhalten: `lru_cache.py` erhielt nur
  einen Kommentar + `# pragma: no branch` (kein Codepfad geändert). Die Tests
  ergänzen nur Abdeckung. → **kein** Human-Gate nötig.
- **Konfigurationsänderung** (Branch-Coverage an, Mindest-Score bleibt 100 %)
  durch Auftrag gedeckt.
- **Neue Quelle:** nein – nur coverage-/pytest-Doku als Prüfnachweis.

## 8. Reproduktion

```bash
python3 -m pytest -q --cov-branch                    # erwartet: 100 %, rc=0
python3 -m pytest -q --cov-branch -k "not ingestion and not reflective"
                                                     # erwartet: < 100 %, rc=1
```
