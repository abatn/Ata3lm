"""
Solver v5: finde_minimum

Aufgabe: Finde das Minimum einer Liste von Zahlen.
Bekannte Schwäche: Gibt das erste Element zurück, statt das echte Minimum zu berechnen.
"""


def finde_minimum(liste: list):
    """
    Findet das Minimum einer Liste von Zahlen.

    BEKANNTER BUG: Gibt einfach das erste Element zurueck,
    ohne die restlichen Elemente zu vergleichen.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 3 (sollte 1 sein)
    Eingabe: [-5, -2, -10, 0] -> Ausgabe: -5 (sollte -10 sein)
    """
    if not liste:
        return None
    return liste[0]


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {finde_minimum(test)}")
    print("Erwartet: 1")
