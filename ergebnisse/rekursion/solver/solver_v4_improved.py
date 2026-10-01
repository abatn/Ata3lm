"""
Solver v4: berechne_durchschnitt (verbessert)

Aufgabe: Berechne den Durchschnitt einer Liste von Zahlen.
Bekannte Schwäche behoben: Nutzt echte Division '/' statt Integer Division '//'.
"""

def berechne_durchschnitt(liste: list) -> float:
    """
    Berechne den Durchschnitt einer Liste von Zahlen.
    
    VERBESSERTER ALGORITHMUS: Nutzt echte Division '/' für korrekte Gleitkomma-Ergebnisse.
    Eingabe: [1, 2] -> Ausgabe: 1.5
    Eingabe: [10, 20, 30, 35] -> Ausgabe: 23.75
    """
    if not liste:
        return None
    return sum(liste) / len(liste)


if __name__ == "__main__":
    test = [1, 2]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {berechne_durchschnitt(test)}")
    print(f"Erwartet: 1.5")