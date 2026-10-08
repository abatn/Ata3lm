# Rekursion 079: N4 + N6 + N5 — Freigabebindung (§6-Kopf) · PROV-Revisionskette · MCP-§6-Pflichtfelder

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare (echte Tests).
> **Befund-Quelle (verbindlich): Audit b09a0a9** (Datei `tests/test_network_boundaries.py`).
> N-Nummerierung = **Audit** (NICHT Rekursion 062–063).
> Ziel `g`: (N4) die Zwei-Personen-Freigabe bindet auch die §6-Kopffelder
> (`source_ref`/`ontology_ref`); (N6) `prov:wasRevisionOf` verweist auf die reale
> vorige Entity-ID (Body-Hash); (N5) **jeder** `structured`-Einstieg trägt die
> §6-Pflichtfelder (kein MCP-Umgehungspfad).
> Auftrag: „Knowledge-Agent härten — N1–N8 (Revision b09a0a9)", **Phase 2** (Fixes N4+N6+N5).
> Status: **umgesetzt** · §9-Status: **`approved` (Batnini + Taoufik, 2026-10-08)** ·
> **kein Commit** (G6).

## 1. Soll/Norm (Audit + Fundstellen)

| Feld | Wert (Audit b09a0a9, verbindlich) |
|---|---|
| Befund N4 | **N4 · P1 · K8-Metadaten nicht in der Freigabebindung** |
| Befund N6 | **N6 · P2 · K8 bricht PROV-Revisionsverknüpfung** |
| Befund N5 | **N5 · P2 · MCP umgeht §6-Pflichtfelder** |
| Datei | `data/memory/write_gateway.py` (`_approval_sha`, `store`, `old_content`) · `data/memory/mcp_memory_server.py` (`write`) |
| **Soll N4** | Freigabe bindet Body **+ Zielmenge + `source_ref`/`ontology_ref`**; leere Refs ⇒ exakt der alte Hash (rückwärtskompatibel). |
| **Soll N6** | Vorgänger-Hash über den **Body ohne K8-Kopf** ⇒ `prov:wasRevisionOf` == vorige `entity:@id`. |
| **Soll N5** | Jeder `structured`-Einstieg (`store` **und** MCP-`write`) schreibt den §6-Kopf (`Ontologie-Bezug`/`Quelle`/`Evidence`); nicht-structured (JSONL/History/tier1/tier3) bleibt body-only. |
| Repro N4 | `test_k8_changed_source_and_ontology_need_bound_approval` |
| Repro N6 | `test_k8_revision_links_to_preceding_entity` |
| Repro N5 | `test_k8_all_structured_entrypoints_have_required_fields` |

Norm: `AGENTS.md` §9.3 (Zwei-Personen-Freigabe) · §6 (Pflichtfelder/keine Erfindung)
· §9.2c (nur trusted+verified) · §10.7 (supersede = invalidieren, nicht löschen).
PROV-O `prov:wasRevisionOf` (bereits im Repo, `data/memory/provenance.py:5`).

## 2. Befund (Ist ≠ Soll)

- **N4:** `_approval_sha(content, targets)` band nur Body + Zielpfade. Nach der
  Freigabe waren `source_ref`/`ontology_ref` (K8-Kopf) frei änderbar, ohne dass
  `diff_sha` brach — die §6-Herkunft war nicht Teil der Bindung.
- **N6:** `old_content = structured_file.read_text()` hasht seit K8 **Kopf + Body**;
  die vorige `entity.sha256` ist aber der Hash des **Fakts** (Body). `revision_of`
  zeigte daher auf eine nie existierende Entity (PROV-Kette gebrochen).
- **N5:** `mcp_memory_server.write(scope="structured")` rief `store_file` mit dem
  Roh-Body ⇒ in `knowledge/structured/` fehlten `ontologie-bezug`/`quelle`/`evidence`
  (zweiter structured-Pfad ohne K8-Kopf).

## 3. Änderung (Diff-Skizze, line-level)

```diff
 # write_gateway.py — N4
-def _approval_sha(content, targets):
-    return provenance.content_hash(content + "\x00" + "\x00".join(parts))
+def _approval_sha(content, targets, source_ref="", ontology_ref=""):
+    refs = (source_ref or "") + "\x00" + (ontology_ref or "")
+    material = content if refs == "\x00" else content + "\x00" + refs   # N4
+    return provenance.content_hash(material + "\x00" + "\x00".join(parts))
 # store(): Freigabe über Body + Refs binden
-        _gate_approval(approval_obj, approvers, question, _approval_sha(clean, [t for t, _ in targets]))
+        _gate_approval(..., _approval_sha(clean, [t for t, _ in targets],
+                                          source_ref=source_ref, ontology_ref=ontology_ref))
 # write_gateway.py — N6
+def _strip_k8_header(text):                       # K8-Kopf strippen -> Body
+    if not text.lower().startswith("- ontologie-bezug:"): return text
+    return text.partition("\n\n")[2]
-    old_content = structured_file.read_text(encoding="utf-8") if structured_file.exists() else None
+    old_content = _strip_k8_header(structured_file.read_text(encoding="utf-8")) if structured_file.exists() else None

 # mcp_memory_server.py — N5
+    written = clean
+    if scope == "structured":
+        record = provenance.build_record(fact=clean, activity=f"mcp-write:{scope}",
+                                         agent="mcp-memory-server", source="tool:verified", now=time.time())
+        written = write_gateway._structured_doc(clean, record)
-    res = write_gateway.store_file(target=path, content=clean, ...)
+    res = write_gateway.store_file(target=path, content=written, ...)
```

| Datei | Inhalt |
|---|---|
| `data/memory/write_gateway.py` | `_approval_sha` bindet optional `source_ref`/`ontology_ref` (leer ⇒ alter Hash); `store()` reicht die §6-Kopffelder in die Freigabe; neuer `_strip_k8_header`; `old_content` wird über den **Body** gehasht (N6). |
| `data/memory/mcp_memory_server.py` | `write` erzeugt für `scope="structured"` den `_structured_doc`-Kopf (N5); `written` statt `clean` an `store_file`; `bytes` = geschriebene Länge. Nicht-structured unverändert. |
| `tests/test_network_boundaries.py` | +3 verbindliche Repro-Fälle N4/N5/N6 (echte tmp-Dateien/Scopes). |
| `tests/test_write_gateway.py` | +2 (N6-Legacy-body-only-Zweig; positiver N4-Refs-Freigabezweig). |
| `tests/test_mcp_memory.py` | 9 Roh-Gleichheits-Asserts für `structured` K8-konform umgestellt (Body via Kopf-Toleranz + 3 Pflichtfelder); Semantik (Tri-Color, Scope-Trennung, R11–R14, N1/N2 fail-closed) unverändert. |

- Geänderte Komponenten: **2** (`write_gateway.py`, `mcp_memory_server.py`).
- Interface-/Format-Änderung? **ja** — Bindungsformat (`_approval_sha`), `structured`-Format
  beim MCP-Write ⇒ §9-pflichtig, **`approved`** (Batnini + Taoufik, 2026-10-08).

## 4. Real vs. offen (ehrlich)

- **Real:** echte Dateisystem-/Scope-Tests (kein Mock, keine Fake-Antworten, G7);
  alle 3 Repros wurden **zuerst rot** gegen die HEAD-Module verifiziert (§5), dann grün.
- **Rückwärtskompatibilität (N4):** leere `source_ref`/`ontology_ref` liefern **exakt**
  den alten `_approval_sha`; der `store_file`-Pfad ruft ohne Refs auf und ist unverändert.
- **Rückwärtskompatibilität (N6):** ein `structured`-Dokument **ohne** K8-Kopf
  (Write vor K8, body-only) wird unverändert gehasht (Test `test_n6_legacy_body_only_structured_file_bleibt_body`).
- **N5-Testanpassung (§9-`approved`):** die 9 MCP-Asserts prüften Roh-Gleichheit des
  `structured`-Bodys; da ein §6-Kopf den Dateiinhalt zwangsläufig erweitert, wurden sie
  auf `_assert_k8_structured` (Kopf-Toleranz + 3 Pflichtfelder) umgestellt. Die
  **inhaltliche Semantik** bleibt: `tier3` wird weiter per Roh-Gleichheit geprüft
  (nicht-structured body-only), Blue-Schutz/Scope-Trennung/R11–R15/N1/N2 unverändert.
- **Kein `self_update`** an `AGENTS.md`/`data/memory/tier1-base/`; reale Stores unberührt.

## 5. Compare / Beleg (externes Signal: echte Tests)

**Rot (HEAD-Module, echte Ausführung der 3 Repro-Szenarien):**

```text
[OLD] N4 approval : FAIL (Bug reproduziert)  # 'entity:aa25…' == 'entity:a70f…' -> deny nicht ausgelöst
[OLD] N6 revision : FAIL (Bug reproduziert)  # wasRevisionOf (Kopf+Body) != vorige entity:@id
[OLD] N5 structured: FAIL (Bug reproduziert) # 'ontologie-bezug' not in 'MCP-Fakt.'
```

**Grün (neue Module):**

```text
pytest tests/test_network_boundaries.py -k "k8_changed_source or k8_revision
        or all_structured_entrypoints" --no-cov -q                    -> 3 passed
pytest -m "not network and not live" -q --no-cov -p no:cacheprovider  -> 585 passed, 26 deselected
ruff check <5 geänderte Code-/Testdateien>                            -> All checks passed
ruff format --check <5 geänderte Code-/Testdateien>                   -> 5 files already formatted
Coverage data/memory/write_gateway.py   (Line + Branch)               -> 100 %
Coverage data/memory/mcp_memory_server.py (Line + Branch)             -> 100 %
```

Repro-Kommandos (verbindlich): `pytest tests/test_network_boundaries.py` (N4/N5/N6-Fälle).

## 6. Drift (Δ zur Baseline, §9.1c)

| Artefakt | geänderte Zeilen (numstat: +/−) | Dateizeilen | Roh-Anteil |
|---|---|---|---|
| `write_gateway.py` | 39 + 6 = 45 | 836 | ~5,4 % |
| `mcp_memory_server.py` | 19 + 3 = 22 | 327 | ~6,7 % |

- Roh-Anteile liegen **unter** dem 10 %-Default des §9.1c (inkl. Docstrings/Kommentare).
- **Gate-Anbindung:** Drift ≤ Bound ⇒ kein zusätzliches Drift-Gate; die
  Interface-/Formatänderung ist durch die **Zwei-Personen-Freigabe** belegt.

## 7. §9-Gate

- **Interface-/Formatänderung** (Bindungsformat, MCP-`structured`-Format, 9 Test-Asserts):
  **erforderlich** und **`approved`** — Batnini + Taoufik, 2026-10-08 (§9.3, ≥ 2 Personen).
- **Neue Quelle?** nein — PROV-O (`data/memory/provenance.py:5`), MCP-Spec (`AGENTS.md` §11.4),
  §6/§9.3/§10.7 (alle bereits im Gesetz); kein Ontologie-Eintrag nötig.
- **self_update an Originaldateien?** nein (`AGENTS.md`/`tier1-base` unberührt).
- **Kein Commit** (Guardrail 6). Reviewer-Kommandos: `git status --short`, `git diff --stat`.

**§9-Status: `approved` (Batnini + Taoufik, 2026-10-08).**

## 8. Nächstes Self-Feedback (t+1)

- Der MCP-`structured`-Kopf setzt `Ontologie-Bezug` standardmäßig „offen (§4)" und
  `Quelle=tool:verified`; der MCP-`write`-Kontrakt hat (noch) keine `ontology_ref`/
  `source_ref`-Parameter. Fließt in t+1: optionale Referenzen durchreichen (dann
  bindet N4 sie auch im MCP-Pfad).
- `_approval_sha` bindet Refs nur, wenn gesetzt; ein Kopf, der **nachträglich** von
  „offen" auf einen konkreten Bezug wechselt, ändert die Bindung (gewollt, N4).
