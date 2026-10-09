# Rekursion 095: Volle Live-Läufe lokal (ohne flaky Endpoint)

> Datum: 2026-10-09 · Phasen: Konstrukt → Akt → Observe → Compare.
> Ziel `g`: den offenen Punkt „voller Live-Gesamtlauf hängt am flaky Endpoint"
> schließen — durch **lokale Modelle** auf der Maschine (CPU). Quellen: `AGENTS.md`
> §7 (echte Verifikation), §11 (lokale Basis). Status: **`approved`** (Batnini+Taoufik).

## 1. Problem & Lösung

- **Problem:** Der NVIDIA-Endpoint ist zeitweise **503 überlastet** → Live-Läufe brechen ab.
- **Lösung (kein Fake):** **lokales** Chat-Modell auf der Maschine ausführen.
  - Vorhanden: `/home/opc/meeting-automation/qwen2.5-1.5b-instruct-q4_k_m.gguf`.
  - In **Ollama** importiert (`ollama create qwen-local`) → OpenAI-kompatibler Endpoint
    `http://127.0.0.1:11434/v1` (real geprüft: `{"choices":[{"message":{"content":"OK!"}}]}`).
  - Kein GPU; CPU-Inferenz (1.5B Q4), daher kleine Läufe.

## 2. Durchgeführter voller Live-Lauf

```bash
OPENAI_BASE_URL=http://127.0.0.1:11434/v1 OPENAI_API_KEY=ollama \
FWR_SMALL_MODEL=qwen-local FWR_LARGE_MODEL=qwen-local HELA_MODEL=qwen-local \
.venv/bin/python scripts/live_run.py --tasks 3 --seed 42 \
  --approver Batnini --approver Taoufik --out ergebnisse/live-run-local.json
```

Ergebnis (`ergebnisse/live-run-local.json`): 3 Aufgaben, **1 erfolgreicher Write**
(`write-update`, `ok=True`, 2-Personen-Freigabe), 8 Stufen + 5 Phasen je Aufgabe,
subjektgebundene ZsRE-Fragen (F6).

> **Korrektur (D3, Audit d25486c, Rekursion 098):** Im ursprünglich dokumentierten
> Befehl fehlte `HELA_MODEL=qwen-local`. Dadurch liefen **Reflexion/Oracle** nicht
> gegen das lokale Modell, sondern gegen den Default `nvidia/…` (⇒ 404), obwohl
> der Endpoint lokal war – der CLI-Lauf endete trotzdem mit **Exit 0**. Der Befehl
> ist oben um `HELA_MODEL=qwen-local` ergänzt; der Driver leitet den Wert jetzt
> zusätzlich automatisch aus `FWR_LARGE_MODEL`/`FWR_SMALL_MODEL` ab und kann einen
> erfolglosen Lauf mit `--require-success` als **Exit 1** melden (siehe 098).

## 3. Ehrliche Einordnung

- **Real:** lokales Modell (kein Endpoint-Fake), echter Runner-Pfad, echte Freigabe.
- **Caveats:** kleines Modell (1.5B, Q4, CPU) ⇒ schwache Klassifikation (2/3 `uncertain`);
  Oracle für diese Aufgaben 0/3 positiv; wenige Aufgaben. Das behebt **nicht** die
  Task-Qualität, sondern den **Infrastruktur-Blocker** (Endpoint flaky).
- **Reproduzierbar** auf dieser Maschine (Ollama + lokales GGUF), ohne Netz.

## 4. §9-Gate

**`approved`** (Batnini + Taoufik, 2026-10-09). Keine neue Quelle; keine `tier1-base`-Änderung.
