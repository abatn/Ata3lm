# Compare – Unterphase der Rekursions-Kommunikation

> Lab-Prinzip: Projekt + Skills + Connectors + Knowledge. MD-first.
> Eltern-Dok: `knowledge/lifecycle/rekursion/index.md` (§2.4).
> Compare berechnet Ähnlichkeit und Konsistenz – ausschließlich auf Basis
> externer, verifizierbarer Signale (Code-Ausführung, DB/Grader). Sonst
> droht „konfidente Fehlanpassung".

## 1. Definitionen (aus Quelle, kein Eigenbau)

Drei Kennzahlen, strikt zu trennen (Duesterwald et al. 2026):

- **Mean@k:** mittlere Pass-Rate über k Läufe (Standard-„Accuracy").
- **Pass@k:** Anteil Tasks mit ≥1 erfolgreichem von k Läufen (optimistisch –
  richtig bei verifizierbarem Retry).
- **Pass^k:** Anteil Tasks mit Erfolg in ALLEN k Läufen (pessimistisch –
  die Nutzerfrage „klappt es auch beim zweiten Mal?").
- Es gilt immer: **Pass^k ≤ Mean@k ≤ Pass@k.**
- **Consistency Gap = Mean@k − Pass^k** (Prozentpunkte): misst, wie viel
  scheinbare Accuracy unter Wiederholung verdampft.

Quellen:

- Paper: Duesterwald et al. (2026): Closing the Consistency Gap –
  https://arxiv.org/abs/2609.08832 (eingereicht 8. Sep 2026)
- Praxis-Blog (IBM Research / Hugging Face): ALTK-Evolve Consistency –
  https://huggingface.co/blog/ibm-research/altk-evolve-consistency

## 2. Belegte Befunde (nur zitiert, nicht selbst gemessen)

Setup: ReAct-Agent (Yao et al. 2023) + GPT-4.1, AppWorld `test_normal`
(168 Tasks), k=5, Standard-AppWorld-Grader:

- Mean@5 = **77.4 %**, Pass^5 = **53.0 %** → Gap **24.4 pp**
  (auf Hard-Tasks bis ~30 pp).
- Mit Consistency-Guidelines: Pass^5 **53.0 % → 69.0 %** (+16.0 pp),
  Mean@5 **77.4 % → 81.0 %** (nicht degradiert), Gap → **12.0 pp**.
- Generalisierung auf ähnliche Tasks (gleiche AppWorld-Szenarien):
  Pass^5 +13.0 pp.
- Diagnose-Werkzeug **Consistency Analyzer**: EINE aufgezeichnete Trajektorie
  genügt, kein Ground Truth, kein End-to-End-Replay – pro
  Entscheidungsschritt EIN Zusatz-Call mit k Completions (Default k=5),
  Black-Box (keine Logits), Flip-anfällige Schritte → Scorecard →
  Guideline-Generator → episodisches Memory für Folgeläufe.

Lehre (aus Quelle): Konsistenz ist orthogonal zu Capability – ein stärkeres
Modell hebt Mean@k, schließt den Gap aber nicht automatisch. Empfehlung:
**Pass^k immer neben Mean@k berichten.**

## 3. Skill-Auftrag: Ähnlichkeit und Konsistenz (Pass@k vs. Pass^k)

Auftrags-Begriffe, auf belegte Metriken gemappt (Mapping, keine
Paper-Behauptung):

- **Ähnlichkeit:** Trajektorien-/Ergebnis-Übereinstimmung über Läufe
  (welche Entscheidungspunkte flippen? → Analyzer-Logik).
- **Konsistenz:** Pass^k + Consistency Gap als Zahl, mit Beleg-Tabelle
  (Mean@k, Pass@k, Pass^k, Gap, k, n Tasks, Grader).
- **Pass@k vs. Pass^k:** beide berichten + begründen, welche zählt
  (Retry möglich → Pass@k; Produktion ohne Retry → Pass^k).

## 4. Rekursionsschnittstelle (externe Signale – Pflicht)

```text
Observe-Output (r, Traces) ──Compare──▶ Delta-Bericht ──▶ Revise
   │                              ▲
   └─ externe Referenz (Grader / Code-Run / DB), NIEMALS nur internes Scoring
```

- **Erlaubte Signale:** AppWorld-Grader (belegt), Code-Ausführung
  (Interpreter/Compiler – vgl. Reflexion-Evaluierung), DB-/Ground-Truth-
  Abgleich, Validierungsset, menschliches Urteil.
- **Verboten:** rein internes Self-Scoring („sieht gut aus") –
  Guardrail gegen konfidente Fehlanpassung.
- **Output:** Delta-Bericht (besser/gleich/schlechter + Zahlen + Log-Beleg)
  nach `ergebnisse/rekursion/NNN-*.md`. Ohne Beleg kein `continue_improve`.

## 5. Input / Output

Input: `(s, r)`, Traces, externe Referenz (Grader/Test/DB).

Output: Metrik-Tabelle + Delta-Bericht + File in `ergebnisse/rekursion/`.

## 6. Guardrails

1. Compare ohne externes Signal = ungültig (als `rejected` loggen).
2. k und n immer angeben (keine „Accuracy" ohne Wiederholungszahl).
3. Pass@k und Pass^k getrennt berichten, nicht vermischen.
4. Kein Revise ohne belegten Delta-Bericht.

## 7. Quellen (keine Erfindungen)

- https://arxiv.org/abs/2609.08832
- https://huggingface.co/blog/ibm-research/altk-evolve-consistency
- AppWorld (Trivedi et al. 2024, via Paper referenziert – keine
  Eigenbehauptung zu Details)
- ReAct (Yao et al. 2023): https://arxiv.org/abs/2210.03629
- Skill: `skills/recursive-improve/compare/SKILL.md`
- Connector: `connectors/consistency-gap.md`
