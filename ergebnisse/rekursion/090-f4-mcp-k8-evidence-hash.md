# Rekursion 090: F4 – MCP-K8-Kopf nach PII-Sanitisierung (Audit 75095d5)

> Datum: 2026-10-08 · Phasen: Konstrukt → Akt → Observe → Compare → Revise.
> Ziel `g` (§9.1c): Der MCP-`structured`-Write darf den K8-§6-Kopf nicht
> beschädigen – `Evidence: sha256:…` == `content_hash(body)`, Kopf/Body getrennt.
> Quellen (in `AGENTS.md` referenziert ⇒ **keine neue Quelle**): **MCP-Spec**
> (Write-Pfad-Validierung) und **TMA-NM (arXiv:2606.24322, „write-time origin
> binding is necessary")** – AGENTS.md §9.2c.
> Status: **`approved`** (Batnini + Taoufik, 2026-10-08; §9 Interface-Änderung).

## 1. Soll (Belegt + Auftrag)

- **Belegt (MCP-Spec / TMA-NM):** Die Provenienz-Bindung muss **write-time**
  erfolgen: `Evidence: sha256:<hash>` des `structured`-Eintrags muss der
  **echte Body-Hash** sein, nicht ein durch den PII-Filter verfälschter Wert.
- **Auftrag (Projekt, K8/F4):** Der K8-§6-Kopf (`Ontologie-Bezug`/`Quelle`/
  `Evidence`) wird **erst NACH** der PII-Sanitisierung erzeugt. Nur der **Body**
  läuft durch `PIIFilter.minimize`; `sha256`/Datum im Kopf bleiben unangetastet.
  Kopf und Body sind durch eine Leerzeile (`\n\n`) getrennt; `_strip_k8_header`
  greift weiterhin.

## 2. Ist (vorher → nachher)

**Vorher (75095d5, beschädigt):** `mcp_memory_server.write` baute für
`scope=structured` den `_structured_doc`-Kopf (inkl. `sha256`/Datum) **vor** dem
Store. Danach lief der **gesamte** Inhalt (Body + Kopf) durch
`write_gateway._gate_trust_pii` → `PIIFilter.minimize`. Die Phone-/Kreditkarten-
Muster entfernten die Ziffernläufe im `sha256` und im ISO-Datum: der Kopf war
zerstört und `Evidence: sha256:…` passte nicht mehr zum Body-Hash. Zusätzlich
klebten Kopf und Body zusammen (`_structured_doc` schreibt `header + "\n" + body`
mit `header`-Abschluss-`\n`; korrekt ist die Leerzeile).

**Nachher:**

| Ort | Änderung |
|---|---|
| `write_gateway.store_file` | neuer optionaler Pfad `structured=True` (+ `ontology_ref`/`source_ref`): der Kopf wird **nach** `_gate_trust_pii` aus dem realen PROV-O-Record erzeugt (`_structured_doc(clean, record)`); nur der Body wird bereinigt |
| `mcp_memory_server.write` | übergibt den Body mit `structured=(scope=="structured")` an das Gateway (statt den Kopf vorab zu bauen); `bytes` = geschriebene Dateilänge |

## 3. Diff

```
 data/memory/mcp_memory_server.py | 29 +++++++++++------------------
 data/memory/write_gateway.py     | 21 ++++++++++++++++++++-
 2 files changed, 31 insertions(+), 19 deletions(-)
 tests/test_f4_mcp_k8.py          | neu, 122 Zeilen (untracked)
```

- `write_gateway.py`: `store_file(..., structured=False, ontology_ref="",
  source_ref="")` – Interface-Erweiterung (§9 kenntlich gemacht); temporärer
  `write_targets`-Pfad; Kopf-Erzeugung **nach** PII.
- `mcp_memory_server.py`: kein Vorab-Kopf mehr; `import provenance` entfernt
  (nicht mehr benötigt); `bytes` aus der realen Datei (nicht mehr aus `written`).
- `tests/test_f4_mcp_k8.py` (neu): Repro `test_mcp_k8_evidence_hash_matches_stored_body`
  + Datum/Refs/Non-structured + echter stdio-MCP-Aufruf.
- `AGENTS.md` und `data/memory/tier1-base/` **nicht** geändert.

## 4. Compare / Tests (echtes externes Signal)

Neue Repros (`tests/test_f4_mcp_k8.py`, echte tmp-Dateien + echte PROV-O-Records):

| Test | Aussage |
|---|---|
| `test_mcp_k8_evidence_hash_matches_stored_body` | F4: Kopf-`sha256` == `provenance.content_hash(body)`; `\n\n`-Trennung; `_strip_k8_header` == Body |
| `test_mcp_k8_datum_im_kopf_unangetastet` | F4-Ursache: volles ISO-Datum im Kopf (vom PII-Filter nicht entfernt) |
| `test_mcp_k8_non_structured_bleibt_body_only` | Nicht-`structured`-Scopes unverändert Body-only |
| `test_store_file_structured_mit_refs` | `store_file(structured=True)` mit `ontology_ref`/`source_ref`; Hash == Body-Hash |
| `test_mcp_k8_stdio_evidence_hash_matches` | **echter stdio-MCP-Server** (MCP-Spec, Guardrail 7): Kopf-Hash == Body-Hash |

Angepasst: keine bestehende MCP-Erwartung geändert (Tri-Color/Scope/R11–R14/
N1/N2 bleiben grün).

**Akzeptanz (ausgeführt):**

- `.venv/bin/python -m pytest -m "not network and not live" -q --no-cov -p no:cacheprovider`
  → **alle MCP-/Gateway-Tests grün** (`tests/test_mcp_memory.py`,
  `tests/test_f4_mcp_k8.py`, `tests/test_write_gateway.py`).
- `ruff check` + `ruff format --check` (geänderte/neue Dateien) → sauber.
- Coverage (`--cov=data/memory --cov-branch`): `write_gateway.py` **100 %**
  (304 Stmts / 100 Branches, 0 Miss) und `mcp_memory_server.py` **100 %**
  (126 Stmts / 48 Branches, 0 Miss).

## 5. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-08). Keine neue Quelle (MCP-Spec /
arXiv:2606.24322 sind in `AGENTS.md` referenziert). Interface-Änderung
(optionaler `structured`-Pfad in `store_file`) ist freigegeben und im Docstring
kenntlich gemacht. `data/memory/`-Skript/Test ⇒ **kein** `versions/vN`.
**Kein** `git add/commit/push` (§G6); `git status --short`/`diff --stat` siehe §3.
