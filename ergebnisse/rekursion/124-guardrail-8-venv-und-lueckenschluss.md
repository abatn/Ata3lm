# Rekursion 124 — Guardrail 8 (`.venv`) ins Gesetz + Provenienz-Lückenschluss

**Datum:** 2026-10-18
**Ziel `g`:** Mandat des Nutzers in drei Teilen — Ziel A (README-Indexzeile Rek. 122,
geschärfter Glob `NNN`, Lückenschluss der 4 offenen Historien-Dateien), Ziel B
(Korrektur der falschen Attribution „AGENTS.md sagt I/O-/Auswertungs-Trennung selbst
voraus" → `rejected` nach `AGENTS.md:14`), Ziel C (`.venv`-Regel ins Gesetz nach
Human-Gate + Zwei-Personen-Freigabe, Snapshot `versions/v13`, erneuter Volllauf,
diese Provenienz).

---

## 1. Gate & Freigabe (§9 Z.121, §9.3)

- **Human-Gate (§9 Z.121):** erteilt. Namentliche Freigabe im Session-Chat 2026-10-18:
  **Batnini** und **Taoufik**.
- **Zwei-Personen-Verifikation (§9.3, `AGENTS.md:225-232`):** ≥ 2 distinkte Personen
  erfüllt — zwei Namen, kein Doppelzähler.
- **Status:** `approved` (Ziel C). Ziel A/B brauchten kein §9-Gate (keine
  Gesetzes-/Interface-Änderung — nur Historien-Index, Prüf-Test und Historien-Daten).
- **Freigabe-Record (`freigabe-record-*.json`): nicht angelegt** — im Auftrag nicht
  verlangt (Ablauf war „Gesetz → v13 → Volllauf → Provenienz 124"). Freigabe belegt
  durch diese Datei + Session-Chat. **Offen:** bei Bedarf über
  `data/memory/approval.py` nachziehen (nicht gemacht, nicht beauftragt).

## 2. Gesetzesänderung `AGENTS.md` (§9.1b, Ziel C)

**Befehl:** `sed -n '105,112p' AGENTS.md` nach dem Edit.

```text
7. Echte Verifikation: **Tests/Compare nur mit echten Quellen/LLM/Endpoint** –
   Fake- oder skriptete Antworten sind **verboten**; „offline/kein Geld" ist keine
   Ausrede (Auftrag, 2026-10-03).
8. Python-Umgebung: alle Läufe über `.venv` — `make test` und `pytest`
   laufen mit `.venv/bin/python` (Auftrag, 2026-10-18).

## 9. Automatisches Gate (Zusatz zu Human-Gate)
```

| | vorher | nachher |
|---|---|---|
| Zeilen (`wc -l AGENTS.md`) | **411** | **413** |
| `sha256sum AGENTS.md` | `04307ef1760da186666d1b969b03cb34792a8d8307b0b627adca8c29abc855c5` | `5b78e571fc2729f52251b901c4d9cfabe1f8d88300fe9c6e222b164ad1b9a75c` |
| ≡ `versions/v12` | JA (`cmp` byte-identisch) | nein — neuer Stand, in `versions/v13` |
| Guardrails | 1–7 | 1–**8** (`grep -c "^8\. Python-Umgebung"` → `1`) |

**Wortlaut-Herkunft:** die 2 Zeilen stammen aus dem ursprünglichen Eingriff, den
Rek. 122 zurückgenommen hat — dort dokumentiert als
`121-env-fix-venv.md:237-238`: *„`AGENTS.md` Guardrail 8 in 2 Zeilen ergänzt
(Z.108-109: alle Läufe über `.venv`, `make test`/`pytest` mit `.venv/bin/python`)"*.
Unterschied zu Rek. 122: **diesmal lag das Gate vor** (dort: Verstoß gegen §9 Z.121
**und** §9.1b → `rejected`).

**Nicht aufgenommen:** der Zusatz „(Auftrag, 2026-10-18)" ist Herkunftsangabe im
Stil von Guardrail 6/7, kein Regelinhalt. Kein weiterer Text ergänzt.

## 3. Snapshot `versions/v13` (§9.1b, `AGENTS.md:159-161`)

**Befehle:** `mkdir -p data/memory/tier1-base/versions/v13` + Kopien + `cmp`.

```text
cmp AGENTS.md data/memory/tier1-base/versions/v13/AGENTS.md  → BYTE-IDENTISCH
5b78e571fc2729f52251b901c4d9cfabe1f8d88300fe9c6e222b164ad1b9a75c  .../v13/AGENTS.md
ls v13 → AGENTS.md core-relations.md episodic_graph.json identity.md ontology.md
```

- **Umfang = 5 Dateien**, exakt wie `v12` (Pflicht-Basisdateien aus
  `tests/test_invariants.py:14` `BASIS_DATEIEN` + `AGENTS.md` ab `AGENTS_AB = 5`).
- **Warum vollständig:** mein erster Versuch legte nur `AGENTS.md` an. Der Test
  `test_versions_lueckenlos` verlangt pro Snapshot `core-relations.md`,
  `episodic_graph.json`, `identity.md`, `ontology.md` — **ohne sie wäre der Lauf rot
  gewesen** (das war der eigentliche Rek.-122-Fehler, nicht die Zeilenzahl 411/413:
  dort fehlte `versions/v13` ganz).
- **Herkunft der 4 Basisdateien:** von `v12` übernommen; vorher geprüft
  (`cmp -s v12/<f> tier1-base/<f>` → alle `IDENTISCH`), sie sind seit 2026-10-14
  unverändert (Dateigröße 1633 / 647 / 1243 / 4238).
- Versionen lückenlos `v1…v13` (`ls` → `README.md v1 v10 v11 v12 v13 v2 … v9`).

## 4. Provenienz-Lückenschluss (Ziel A, Guardrail 3)

**Prüfbefehl** (Glob war zu eng: `0[0-9][0-9]-*.md` = nur 000–099):

```text
tests/test_agents_law.py:48  files = sorted(REK.glob("[0-9][0-9][0-9]-*.md"))
tests/test_agents_law.py:80  (dito in test_rekursion_index_vollstaendig)
```

**Vorher** (Rohtext): `1 failed, 9 passed in 0.05s` — 4 Befunde:
`107`/`116` „Freigabe fehlt", `115`/`122` „Quelle fehlt".

**Nachher** (Rohtext): `10 passed in 0.04s`, `EXIT=0`.

| Datei | fehlte | offizielle Quelle (Herkunft) | übernommener Wert (wortgleich) |
|---|---|---|---|
| `107-e3-e4-e2e.md` | Freigabe | Index `ergebnisse/rekursion/README.md:134` | `approved` (lokal) + Caveat |
| `115-grader.md` | Quelle | Index `README.md:142` + externe Prüfung | `arXiv:2609.36043` |
| `116-kaskade-variante-a.md` | Freigabe | Index `README.md:143` | `approved`: Batnini + Taoufik, 2026-10-14 (Auftrag; kein Diff-SHA) + Caveat |
| `122-revert-agents-md-guardrail8.md` | Quelle | Index `README.md:149` | `AGENTS.md:97/:99/:103/:159-161`, §9/§9.1b/§9.3, Guardrail 3/6, Rek. 121 |

**Jede Ergänzung ist als eigener Abschnitt `## N. Provenienz-Nachtrag — … (2026-10-18)`
gekennzeichnet** mit Wert, Herkunft (Datei:Zeile), Anlass und Ehrlich-Hinweis
(„keine neue Freigabe erteilt" / „keine Quelle erfunden").

**Externe Verifikation der einen neuen Quelle** (nicht erfunden, abgerufen):
`https://arxiv.org/abs/2609.36043` → Titel **„SAGE: A Statistical Acceptance Gate for
Self-Evolving Agents"** (cs.AI, eingereicht 28.09.2026) — passt zum Acceptance-Grader
dieser Rekursion.

**Records geprüft** (`ls ergebnisse/freigabe-record-*`): vorhanden nur
`…-115-2026-10-14.json` und `…-118-119-2026-10-16.json`. Für `107` und `116` existiert
**kein** Record → daher dort ausdrücklich **kein** Diff-SHA behauptet.

## 5. Index + Glob (Ziel A)

- `ergebnisse/rekursion/README.md`: Indexzeile für `122-revert-agents-md-guardrail8.md`
  ergänzt (Status `rejected`, Quellen `AGENTS.md:97/:99/:103/:159-161`).
- Glob an zwei Stellen auf `[0-9][0-9][0-9]-*.md` geschärft → geprüft **124 statt 100
  Dateien** (+24, Nrn. 100–123), Index-Lücken: 0.

## 6. Verifikation — Volllauf (Guardrail 7: echter Lauf)

**Befehl:** `make test > /tmp/opencode/make_test_v13.txt 2>&1`

```text
MAKE_EXIT=0
845 passed, 1 skipped in 427.27s (0:07:07)
Required test coverage of 100% reached. Total coverage: 100.00%
TOTAL   4390      0   1222      0   100%
grep -cE "FAILED|ERROR" → 0
SKIPPED [1] tests/test_lifecycle_discard.py:155: kein Konsolidierungs-State vorhanden
```

**Vorher** (Rek. 123, gleicher Stand): `845 passed, 1 skipped`, `100.00 %`, `EXIT 0`,
**965.64 s** → jetzt **427.27 s** (Zeitersparnis, nicht verstanden — offener Punkt).

**Einzelbelege der kritischen Tests** (`.venv/bin/python -m pytest tests/test_agents_law.py
tests/test_invariants.py -o addopts= -v`): `15 passed in 0.07s`, darunter
`test_provenienz_jeder_rekursion PASSED`, `test_rekursion_index_vollstaendig PASSED`,
`test_versions_lueckenlos PASSED`, `test_neuester_snapshot_gleich_aktuell PASSED`.

**Lint:** `ruff check tests/test_agents_law.py` → `All checks passed!`

## 7. Gesetzes- und Git-Integrität

- **Änderung nur am Gesetz + Historien-/Prüfdateien.** `git status --porcelain | wc -l`
  → `29` (23 ` M ` + 6 `??`), `git rev-parse --short HEAD` → `4bd63cb`.
- **Kein `git add`, `git commit`, `git push`** ausgeführt (Guardrail 6,
  `AGENTS.md:103`) — Snapshot-Weg §5.3 „Commit + Push" der
  `ergebnisse/versionierung.md` daher **bewusst unterlassen**.
- **Keine** Quell-/Testdatei außer `tests/test_agents_law.py` in diesem Schritt
  geändert; **kein** Skip, **kein** Fake, **kein** Fixture für den Volllauf
  (Guardrail 7).

## 8. Ehrliche Trennung

**Gemessen (alle mit Befehl + Rohtext oben):** 411 → 413 Zeilen; beide `sha256`;
`cmp` v13 byte-identisch; v13 = 5 Dateien; `10 passed` nach Lückenschluss;
`845 passed, 1 skipped, 100.00 %, 427.27 s, EXIT 0`; `0 FAILED/ERROR`;
`15 passed` Einzelbeleg; `ruff` sauber; `29` uncommittete Einträge, HEAD `4bd63cb`;
arXiv-Titel abgerufen.

**Geschätzt:** kein Wert in dieser Datei als „geschätzt" geführt — alle Zahlen gemessen.

**Offen / nicht behauptet:**
- **Grund für 965.64 s → 427.27 s ist unbekannt** (möglich Cache/Erstlauf-Effekt) —
  nicht analysiert, nicht als Verbesserung verkauft.
- **Kein JSON-Freigabe-Record** für Rek. 124 (siehe §1).
- **`.venv` steht jetzt im Gesetz**, obwohl das Verzeichnis untracked ist — die
  Regel bindet den Lauf an eine Umgebung, die Git nicht kennt. Das ist bewusst so
  (Ausgangspunkt von Rek. 121), aber ein echtes Risiko für frische Checkouts.
- **Python-Version nicht im Gesetz verankert:** `.venv` läuft auf 3.11.13, das
  System-Python ist 3.9.25 und ohne `pyshacl`/`mcp` (11 failed, 795 passed, 2 errors).
  Der Unterschied wird durch Guardrail 8 nicht abgedeckt — nur der Pfad.
- **`test_provenienz_jeder_rekursion` bricht beim 1. Fehler ab**
  (`tests/test_agents_law.py:54`) — deshalb zeigte der Vorher-Lauf nur `1 failed`,
  obwohl 4 Dateien betroffen waren.

## 9. Quellen (§9.1d, Guardrail 3)

- `AGENTS.md:97` (Human-Gate), `:99` (Provenienz), `:103` (Git-Sperre),
  `:159-161` (§9.1b Versionierung), `:176-180` (§9.1d Evidenz),
  `:225-232` (§9.3 Zwei-Personen), `:14` (Geltungsbereich → `rejected`).
- `tests/test_invariants.py:14,46-47,50-56` (Snapshot-Pflicht + `≡` zum jüngsten Stand).
- `tests/test_agents_law.py:48,54,80` (Glob, Abbruch bei erstem Fehler, Index).
- `ergebnisse/versionierung.md` §2 (Snapshot-Umfang), §5 (Regel für neue Versionen).
- `ergebnisse/rekursion/121-env-fix-venv.md:237-238` (ursprünglicher Wortlaut Guardrail 8).
- `ergebnisse/rekursion/README.md:134,142,143,149` (offizielle Werte der 4 Lücken).
- `ergebnisse/freigabe-record-115-2026-10-14.json`, `…-118-119-2026-10-16.json`
  (einzige bestehenden Records).
- <https://arxiv.org/abs/2609.36043> — „SAGE: A Statistical Acceptance Gate for
  Self-Evolving Agents" (2026-09-28, cs.AI).
