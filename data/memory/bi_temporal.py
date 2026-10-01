#!/usr/bin/env python3
"""
Bi-temporale Semantik für Memory-Einträge.

Quelle (verifiziert 2026-10-01, HTTP 200):
  - **Engram** (arXiv:2606.09900, https://github.com/ly-wang19/engram):
    Fakten tragen zwei Zeitachsen:
      - **valid time** (`valid_at` / `invalid_at`) – wann der Fakt in der Welt gilt;
      - **transaction time** (`created_at` / `expired_at`) – wann wir ihn lernten/verwarfen;
      plus `supersedes`-Pointer. Invariante: „never hard-delete a contradicted fact —
    invalidate it … and keep the history." Read-Path: bi-temporaler **as-of**-Filter.
  - Graphiti (arXiv:2501.13956): bi-temporal (Projekt-Konnektor).

Lab-Prinzip: Mechanik = aus der Quelle; die konkreten Feldnamen/Daten sind Auftrag.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Fact:
    subject: str
    predicate: str
    obj: str
    # VALID TIME: wann gilt der Fakt in der Welt?
    valid_from: str
    valid_to: Optional[str] = None          # None = weiterhin gültig
    # TRANSACTION TIME: wann wurde er gespeichert/verworfen?
    recorded_at: str = ""
    superseded_at: Optional[str] = None     # None = weiterhin geglaubt
    supersedes: int = -1                    # Index des abgelösten Fakts


class BiTemporalStore:
    """Bi-temporaler Faktenspeicher (valid time × transaction time)."""

    def __init__(self):
        self.facts: list[Fact] = []

    def assert_fact(self, subject: str, predicate: str, obj: str,
                    valid_from: str, recorded_at: str) -> dict:
        """Retroaktives Update: bei Widerspruch (gleiches s,p, anderes o) wird der
        alte Fakt invalidiert (valid_to + superseded_at), NICHT gelöscht."""
        superseded = None
        for i, f in enumerate(self.facts):
            if (f.subject == subject and f.predicate == predicate
                    and f.superseded_at is None and f.obj != obj):
                f.valid_to = valid_from           # Welt: alter Fakt endet, als neuer begann
                f.superseded_at = recorded_at      # Wissen: alter Fakt verworfen bei Speicherung
                superseded = i
        new = Fact(subject, predicate, obj, valid_from, None, recorded_at, None,
                   supersedes=(superseded if superseded is not None else -1))
        self.facts.append(new)
        return {"index": len(self.facts) - 1, "superseded": superseded, "fact": asdict(new)}

    def as_of(self, valid_time: str, knowledge_time: str) -> list[dict]:
        """Bitemporal: „Was glaubten wir am knowledge_time über valid_time?" """
        return [asdict(f) for f in self.facts
                if f.valid_from <= valid_time and (f.valid_to is None or valid_time < f.valid_to)
                and f.recorded_at <= knowledge_time
                and (f.superseded_at is None or knowledge_time < f.superseded_at)]

    def world_state_as_of(self, valid_time: str) -> list[dict]:
        """Nur valid time: was war am valid_time tatsächlich wahr (egal wann gelernt)."""
        return [asdict(f) for f in self.facts
                if f.valid_from <= valid_time and (f.valid_to is None or valid_time < f.valid_to)]

    def knowledge_as_of(self, knowledge_time: str) -> list[dict]:
        """Nur transaction time: was glaubten wir am knowledge_time?"""
        return [asdict(f) for f in self.facts
                if f.recorded_at <= knowledge_time
                and (f.superseded_at is None or knowledge_time < f.superseded_at)]


def _demo() -> None:
    st = BiTemporalStore()
    print("=== [1] Retroaktives Update (Ivan: Globex → Moonshot) ===")
    r1 = st.assert_fact("Ivan", "works_at", "Globex", valid_from="2024-01-01", recorded_at="2024-01-01")
    print("  assert (Ivan works_at Globex)  ->", {k: r1[k] for k in ("index", "superseded")})
    r2 = st.assert_fact("Ivan", "works_at", "Moonshot", valid_from="2024-03-01", recorded_at="2024-03-15")
    print("  assert (Ivan works_at Moonshot)->", {k: r2[k] for k in ("index", "superseded")})

    print("\n=== [2] Beide Zeitstempel je Fakt ===")
    for i, f in enumerate(st.facts):
        print(f"  F{i}: {f.subject} {f.predicate} {f.obj}")
        print(f"       valid_time:        {f.valid_from} .. {f.valid_to or 'offen'}")
        print(f"       transaction_time:  {f.recorded_at} .. {f.superseded_at or 'offen'}"
              + (f"  (supersedes F{f.supersedes})" if f.supersedes >= 0 else ""))

    print("\n=== [3] As-of-Time-Abfragen ===")
    q = [("2024-02-01", "2024-02-01"), ("2024-04-01", "2024-04-01"), ("2024-02-01", "2024-04-01")]
    for vt, kt in q:
        hits = st.as_of(vt, kt)
        print(f"  as_of(valid={vt}, knowledge={kt}) -> "
              + (", ".join(f"{h['subject']} {h['predicate']} {h['obj']}" for h in hits) or "(kein Fakt)"))
    print("  world_state_as_of(2024-02-01) ->",
          [f"{h['obj']}" for h in st.world_state_as_of("2024-02-01")])
    print("  knowledge_as_of(2024-04-01)   ->",
          [f"{h['obj']}" for h in st.knowledge_as_of("2024-04-01")])


if __name__ == "__main__":
    _demo()
