"""
Solver: sortiere_zahlen (verbessert)

Aufgabe: Sortiere eine Liste von Zahlen aufsteigend und entfernt Duplikate.

Verbesserung gegenüber π₀:
- Hinzufügen von `set()` um Duplikate zu entfernen
- Gleiche Sortierreihenfolge
- Gleiche Leistung für alle Fälle außer Duplikate

Quelle: Eine kleinere Verbesserung am bestehenden Solver (π₀), keine Erfindung.
"""


def sortiere_zahlen(liste: list) -> list:
    """
    Sortiert eine Liste von Zahlen aufsteigend und entfernt Duplikate.

    VERBESSERTER ALGORITHMUS: Deduplizierung einführen durch `set()`.
    Eingabe: [3, 1, 2, 1, 3] -> Ausgabe: [1, 2, 3]
    """
    return sorted(set(liste))


if __name__ == "__main__":
    # Schnelltest
    test = [3, 1, 2, 1, 3]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {sortiere_zahlen(test)}")
    print("Erwartet: [1, 2, 3]")
