# PROPOSAL E — N5: MCP-Write nutzt §6-Pflichtfelder (kein Umgehungspfad)

> **Implementiert (Phase 2) — §9-Freigabe `approved` (Batnini + Taoufik, 2026-10-08).**
> Umsetzung + Belege: `ergebnisse/rekursion/079-n4-n6-n5-approval-provrevision-mcp.md`.
> Befund-Quelle (verbindlich): Audit b09a0a9. (Ursprünglich Phase-0-Entwurf.)

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-08 |
| Iteration | `t → t+1` (geplant, Phase 2) |
| Phase | Konstrukt (Entwurf) |
| Betroffenes Artefakt | `data/memory/mcp_memory_server.py` (ggf. `data/memory/write_gateway.py`) |
| Komponenten-Typ | Code |
| Autor | Knowledge-Agent (Auftrag N1–N8) |

### Befund (Soll/Ist, Audit b09a0a9 — verbindlich)

**N5 · P2 · MCP umgeht §6-Pflichtfelder.**
Datei: `mcp_memory_server.py` ~`:213` · `write_gateway.py` ~`:354` (`store_file`).
**Soll:** MCP-Write nutzt `_structured_doc`.
**Ist:** `mcp_memory_server.write` schreibt über `write_gateway.store_file(target=path, content=clean, …)` **Body-only** — die §6-Pflichtfelder (`Ontologie-Bezug`/`Quelle`/`Evidence`, K8) fehlen in `structured/`. Damit existiert ein zweiter strukturiert-Schreibpfad ohne K8-Kopf (K2 „EIN Schreibpfad" formal gewahrt, K8-Invariante aber umgangen).
Repro (Phase 2): `test_k8_all_structured_entrypoints_have_required_fields`.

## 1. Ziel `g`

- Ziel: Jeder `structured`-Eintrag — egal über welchen Einstiegspunkt — trägt die §6-Pflichtfelder; der MCP-Einstieg nutzt `_structured_doc` (oder einen äquivalenten, gebundenen Pfad).
- Task-Input: Repro-Fall aus `tests/test_network_boundaries.py` (Audit b09a0a9).

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Rev. `b09a0a9`, `mcp_memory_server.py` |
| Score (externes Signal) | `0/1` = `0 %` — **gemäß Audit-Befund** (Repro-Test entsteht mit Phase 2) |
| Signal-Quelle | 1 benannter Repro-Fall (Audit) |
| Drift-Referenz | Git-Hash `b09a0a9` |

## 3. Änderung (Diff-Skizze, line-level — Richtung, kein Final-Patch)

```diff
 # mcp_memory_server.py (~:213, write)
-    res = write_gateway.store_file(
-        target=path,
-        content=clean,
-        ...
-    )
+    # N5: strukturiert-Einträge tragen die §6-Pflichtfelder (K8) – kein Umgehungspfad.
+    doc = write_gateway._structured_doc(clean, record, ontology_ref=..., source_ref=...)
+    res = write_gateway.store_file(target=path, content=doc, ...)
```

Hinweis: genaue Form (Rekord-Bau vor dem Write, `ontology_ref`/`source_ref`-Durchreichung
oder dedizierter Gateway-Parameter) wird in Phase 2 festgelegt; möglichst **kein**
neuer öffentlicher Parameter (§9), sondern Nutzung der bestehenden K8-Mechanik.

- Geänderte Komponenten: **1** (primär `mcp_memory_server.py`).
- Interface-/Format-Änderung? **ja** — der MCP-Write erhält den §6-K8-Kopf (`_structured_doc`); das geschriebene `structured`-Format ändert sich (auch ohne neuen öffentlichen Parameter) ⇒ **immer Human-Gate (§9/Guardrail 4)**.

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher (Ziel) |
|---|---|---|---|
| `test_k8_all_structured_entrypoints_have_required_fields` | alle structured-Einstiege mit Pflichtfeldern | fail (Audit-Ist) | pass |

- **Score vorher:** `0/1` = `0 %` (Audit-Befund) · **Score nachher (Ziel):** `1/1` = `100 %`
- **Δ Score (Ziel):** `+100` Prozentpunkte

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`.
- **Drift-Wert (Schätzung):** ~10–15/311 ≈ **3–5 %**.
- **Drift-Bound:** 10 % (Default, §9.1c). **Überschritten?** nein (Schätzung; Messung in Phase 2).

## 6. Evidenz / Quellen

- Quelle 1 (**bereits im Repo — KEINE neue Quelle**): **MCP-Spec** (Model Context Protocol — Server/Tool-Write-Kontrakt): <https://modelcontextprotocol.io/specification>, referenziert in `AGENTS.md` §11.4. Kein neuer Ontologie-Eintrag / keine Quellen-Freigabe nötig.
- Quelle 2: AGENTS.md §6 + K8 (Rek. 075: „gateway-geschriebene Fakten tragen `ontologie-bezug`/`quelle`/`evidence`") — intern, bereits Norm.
- Interne Referenz: `data/memory/mcp_memory_server.py:195-235` · `data/memory/write_gateway.py:145-166` (`_structured_doc`) · Audit b09a0a9.

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `0 % → 100 %` (Ziel) | ask |
| Neue Quelle? | **nein** (MCP-Spec in `AGENTS.md` §11.4) | — |
| Interface-/Format-Änderung? | **ja** (`structured`-Format, s. §3) | **ask** |
| Drift ≤ Bound? | ja (≈ 5 % ≤ 10 %) | — |

- **Gate-Ergebnis:** **`ask`** (Phase 2 nur nach §9 `approved`, ≥ 2 Personen).

## 8. Freigabe

- Status: **`implementiert (approved)`** — §9-Freigabe: Batnini + Taoufik, 2026-10-08.
- Human-Gate-Referenz: `ergebnisse/rekursion/079-n4-n6-n5-approval-provrevision-mcp.md`.
