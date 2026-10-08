# FadeMem — adaptiver Exponential-Decay für Tier-3-Eviction

> Datum: 2026-10-07 · Status: **Belegt** (Mechanismus: adaptiver Exponential-Decay,
> moduliert durch Relevanz/Zugriffsfrequenz/Zeit) + **Auftrag** (geschlossene Form,
> Defaults β/γ, Policy-Name `fademem`).
> §9-Status: **approved** (Batnini + Taoufik, 2026-10-08; neue Quelle in
> `ontology.md` §C aufgenommen, siehe `versions/v12`) — die Umstellung des
> **Defaults** auf `fademem` ist weiterhin §9-pflichtig und **nicht** hier freigegeben.

## 1. Quellen (VOR Nutzung per curl geprüft)

| Quelle | Link | HTTP |
|---|---|---|
| FadeMem (ICASSP 2026), DOI | `10.1109/icassp55912.2026.11462095` → https://doi.org/10.1109/icassp55912.2026.11462095 | **202** (→ ieeexplore.ieee.org/document/11462095) |
| FadeMem (arXiv) | https://arxiv.org/abs/2601.18642 | **200** |

**Belegt (Abstract, wörtlich):** „retention is governed by adaptive exponential decay
functions modulated by **semantic relevance**, **access frequency**, and **temporal
patterns**." Ferner: binäres Behalten/Vergessen wird abgelöst („current AI systems
employ binary retention strategies"); Befund 45 % Storage-Reduktion bei besserem
Multi-Hop-Reasoning.

## 2. Was neu ist (additiv, kein API-Bruch)

| Element | Status |
|---|---|
| `decay_score(entry, now, *, beta, gamma)` (Modul-Funktion) | **NEU** |
| `WorkingMemory.decay_score(key, ...)` (now = `self.tick`) | **NEU** |
| `_evict_fademem()` (Eviction nach niedrigstem Score) | **NEU** |
| `policy="fademem"` (opt-in) | **NEU** |
| Default `policy="value"` / `policy="lru"` | **unverändert** |

## 3. Formel (§6-Schranke)

```text
age       = max(0, now − last_used)                     # zeitliches Muster
relevance = clamp(importance, 0, 1)                     # semantische Relevanz
freq_norm = min(hits / 10, 1)                           # Zugriffsfrequenz (gesättigt)
λ(rel,f)  = beta · exp(−gamma · (rel + freq_norm))      # adaptiv: rel/freq dämpfen λ
score     = relevance · exp(−λ · age)                   # höher = überlebt länger
```

**Belegt:** die *Form* (adaptiver Exponential-Decay, moduliert durch Relevanz,
Frequenz, Zeit). **Auftrag:** die konkrete geschlossene Form und die Defaults
`beta=0.05`, `gamma=1.5`, `freq_saturation=10` (das Abstract nennt keine Formel).

**Eviction-Regel:** verdrängt wird das Item mit dem **niedrigsten** Decay-Score
(nicht mehr „ältestes" wie bei LRU). Relevante, häufige und frische Einträge
überleben länger. Gepinnte Items bleiben unverdrängbar.

## 4. Tests (echt, rein rechnerisch)

`tests/test_fademem.py` — 13 Tests:

- (a) Monotonie: Score sinkt mit Alter, steigt mit Relevanz und Frequenz; Frequenz
  sättigt bei 10; `gamma` dämpft den Verfall; `age=0 ⇒ score = relevance`.
- (b) Eviction verdrängt das Unwichtigste zuerst; relevanter+häufiger (aber alter)
  Eintrag schlägt frischen+irrelevanten; gepinnte Items nie; `lru`-Regression grün.
- (c) Grenzfälle: leer (`None`), alles frisch, alles gepinnt (`None`).

## 5. Guardrails

- **Guardrail 7:** Tests sind rein rechnerisch (keine Fake-/skripteten Modellantworten);
  Quellen real per HTTP geprüft.
- **G6:** kein `git add/commit/push`.
- **Interface:** nur *additiv* (neue Funktion/Methode/Policy); kein bestehendes
  Verhalten geändert. Ein Default-Wechsel auf `fademem` wäre §9 `ask` — **offen**.
