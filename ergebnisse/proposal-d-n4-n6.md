# PROPOSAL D — N4 + N6: K8-Metadaten in der Freigabebindung + PROV-Revisionsverknüpfung

> **Implementiert (Phase 2) — §9-Freigabe `approved` (Batnini + Taoufik, 2026-10-08).**
> Umsetzung + Belege: `ergebnisse/rekursion/079-n4-n6-n5-approval-provrevision-mcp.md`.
> Befund-Quelle (verbindlich): Audit b09a0a9. (Ursprünglich Phase-0-Entwurf.)

## 0. Metadaten

| Feld | Wert |
|---|---|
| Datum | 2026-10-08 |
| Iteration | `t → t+1` (geplant, Phase 2) |
| Phase | Konstrukt (Entwurf) |
| Betroffenes Artefakt | `data/memory/write_gateway.py` |
| Komponenten-Typ | Code |
| Autor | Knowledge-Agent (Auftrag N1–N8) |

### Befund (Soll/Ist, Audit b09a0a9 — verbindlich)

**N4 · P1 · K8-Metadaten nicht in Freigabebindung.**
Datei: `write_gateway.py` ~`:651` (Bindung) · ~`:707` (Kopf).
**Soll:** `_approval_sha` bindet auch `source_ref` + `ontology_ref`.
**Ist:** Die Zwei-Personen-Freigabe (§9.3) bindet nur `clean` + Zielmenge; die K8-Kopffelder `source_ref`/`ontology_ref` (§6-Pflichtfelder, `_structured_doc` ~`:707`) sind **nicht** gebunden ⇒ nach Freigabe änderbar, ohne dass `diff_sha` bricht (Replay-Bindung umgeht §6).
Repro (Phase 2): `test_k8_changed_source_and_ontology_need_bound_approval`.

**N6 · P2 · K8 bricht PROV-Revisionsverknüpfung.**
Datei: `write_gateway.py` ~`:682` (`old_content`) · ~`:690` (`revision_of`).
**Soll:** Hash auf **BODY** (Kopf strippen) ⇒ `prov:wasRevisionOf` == vorige Entity-ID.
**Ist:** `old_content = structured_file.read_text()` hasht seit K8 **Kopf+Body** der structured-Datei; der vorige Record hat `entity.sha256` = Hash(**Body**) ⇒ `revision_of=f"entity:{content_hash(old_content)[:16]}"` zeigt auf eine nie existierende Entity — die PROV-Revisionskette (`prov:wasRevisionOf`) ist gebrochen.
Repro (Phase 2): `test_k8_revision_links_to_preceding_entity`.

## 1. Ziel `g`

- Ziel: (N4) Freigabe bindet Inhalt + Ziele + `source_ref`/`ontology_ref`; (N6) `revision_of` verweist per Body-Hash auf die reale vorige Entity-ID.
- Task-Input: Repro-Fälle aus `tests/test_network_boundaries.py` (Audit b09a0a9).

## 2. Baseline (vorher)

| Feld | Wert |
|---|---|
| `π` (Modell/Policy) | Rev. `b09a0a9` (post-K8), `write_gateway.py` |
| Score (externes Signal) | `0/2` = `0 %` — **gemäß Audit-Befund** (Repro-Tests entstehen mit Phase 2) |
| Signal-Quelle | 2 benannte Repro-Fälle (Audit) |
| Drift-Referenz | Git-Hash `b09a0a9` |

## 3. Änderung (Diff-Skizze, line-level — Richtung, kein Final-Patch)

```diff
 # N4 — write_gateway.py (~:651, Freigabebindung in store())
-    state, binding = _gate_approval(..., _approval_sha(clean, [t for t, _ in targets]))
+    state, binding = _gate_approval(
+        ..., _approval_sha(clean, [t for t, _ in targets], source_ref=source_ref, ontology_ref=ontology_ref)
+    )  # N4: §6-Kopffelder sind Teil der Freigabe-Bindung (§9.3)
 # _approval_sha: Material um die beiden Felder erweitern (Format-Änderung, kenntlich)
 # N6 — write_gateway.py (~:682/:690, Revisionsverknüpfung)
-    old_content = structured_file.read_text(encoding="utf-8") if structured_file.exists() else None
+    old_content = _structured_body(structured_file) if structured_file.exists() else None
+    # N6: Kopf strippen -> Body-Hash entspricht entity.sha256 des vorigen Records
```

- Geänderte Komponenten: **1** (`write_gateway.py`; N4+N6 = zwei Punkte, weil der Auftrag D ausdrücklich als Koppelung N4+N6 führt).
- Interface-Änderung? **ja** — `_approval_sha`-Material/Format (Bindungsformat) ⇒ **immer Human-Gate (§9)**.

## 4. Score-Änderung

| Testfall | Kriterium | vorher | nachher (Ziel) |
|---|---|---|---|
| `test_k8_changed_source_and_ontology_need_bound_approval` | geänderte Kopffelder ⇒ Freigabe bricht | fail (Audit-Ist) | pass |
| `test_k8_revision_links_to_preceding_entity` | `prov:wasRevisionOf` == vorige Entity-ID | fail (Audit-Ist) | pass |

- **Score vorher:** `0/2` = `0 %` (Audit-Befund) · **Score nachher (Ziel):** `2/2` = `100 %`
- **Δ Score (Ziel):** `+100` Prozentpunkte

## 5. Drift (Δ zur Baseline)

- **Definition (Auftrag):** `Δ = geänderte Zeilen / Gesamtzeilen des Artefakts`.
- **Drift-Wert (Schätzung):** ~15/803 ≈ **2 %**.
- **Drift-Bound:** 10 % (Default, §9.1c). **Überschritten?** nein (Schätzung; Messung in Phase 2).

## 6. Evidenz / Quellen

- Quelle 1 (**bereits im Repo — KEINE neue Quelle**): W3C **PROV-O** — `prov:wasRevisionOf` (Revisionsbeziehung zwischen Entitäten): <https://www.w3.org/TR/prov-o/>, verankert in `data/memory/provenance.py:5` (verifiziert 2026-10-06, HTTP 200). Kein neuer Ontologie-Eintrag / keine Quellen-Freigabe nötig.
- Quelle 2: EU-KI-VO **Art. 14(5)** (VO (EU) 2024/1689) + AGENTS.md §9.3 (Zwei-Personen-Freigabe) — Verbindlichkeit der Bindung.
- Interne Referenz: `data/memory/write_gateway.py:651,682,690,707` · Audit b09a0a9.

## 7. Gate-Entscheidung (§9)

| Bedingung | Wert | Ergebnis |
|---|---|---|
| Score | `0 % → 100 %` (Ziel) | ask |
| Neue Quelle? | **nein** (PROV-O bereits im Repo, `data/memory/provenance.py:5`) | — |
| Interface-Änderung? | **ja** (Bindungsformat) | **ask** |
| Drift ≤ Bound? | ja (≈ 2 % ≤ 10 %) | — |

- **Gate-Ergebnis:** **`ask`** (Phase 2 nur nach §9 `approved`, ≥ 2 Personen).

## 8. Freigabe

- Status: **`implementiert (approved)`** — §9-Freigabe: Batnini + Taoufik, 2026-10-08.
- Human-Gate-Referenz: `ergebnisse/rekursion/079-n4-n6-n5-approval-provrevision-mcp.md`.
