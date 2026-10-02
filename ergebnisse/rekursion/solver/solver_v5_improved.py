"""
Solver v5 (improved): finde_minimum

Aufgabe: Finde das Minimum einer Liste von Zahlen.
Verbesserung: Nutzt die eingebaute min()-Funktion (echter Vergleich).
"""


def finde_minimum(liste: list):
    """
    Findet das Minimum einer Liste von Zahlen.

    VERBESSERTER ALGORITHMUS: Nutzt min() fuer echten Vergleich.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 1
    Eingabe: [-5, -2, -10, 0] -> Ausgabe: -10
    """
    if not liste:
        return None
    return min(liste)


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {finde_minimum(test)}")
    print("Erwartet: 1")
