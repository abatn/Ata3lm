"""
Solver v6: berechne_median

Aufgabe: Berechne den Median einer Liste von Zahlen.
Bekannte Schwaeche: Gibt das mittlere Element der UNSORTIERTEN Liste zurueck.
"""


def berechne_median(liste: list):
    """
    Berechne den Median einer Liste von Zahlen.

    BEKANNTER BUG: Nimmt das mittlere Element der unortierten Liste,
    ohne zu sortieren und ohne Mittelwert bei gerader Laenge.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 4 (sollte 3 sein)
    Eingabe: [1, 2, 3, 4] -> Ausgabe: 3 (sollte 2.5 sein)
    """
    if not liste:
        return None
    return liste[len(liste) // 2]


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {berechne_median(test)}")
    print("Erwartet: 3")
