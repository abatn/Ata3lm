"""
Solver v6 (improved): berechne_median

Aufgabe: Berechne den Median einer Liste von Zahlen.
Verbesserung: sortiert und bildet bei gerader Laenge den Mittelwert.
"""


def berechne_median(liste: list):
    """
    Berechne den Median einer Liste von Zahlen.

    VERBESSERTER ALGORITHMUS: sortiert; bei gerader Laenge Mittelwert der beiden mittleren.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 3
    Eingabe: [1, 2, 3, 4] -> Ausgabe: 2.5
    """
    if not liste:
        return None
    s = sorted(liste)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {berechne_median(test)}")
    print("Erwartet: 3")
