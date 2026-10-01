"""
Solver v4: berechne_durchschnitt

Aufgabe: Berechne den Durchschnitt einer Liste von Zahlen.
Bekannte Schwäche: Rundet auf ganze Zahlen (Integer Division).
"""

def berechne_durchschnitt(liste: list) -> float:
    """
    Berechne den Durchschnitt einer Liste von Zahlen.
    
    BEKANNTER BUG: Verwende integer Division '//' statt echter Division '/'
    Eingabe: [1, 2] -> Ausgabe: 1.0 (sollte 1.5 sein)
    Eingabe: [10, 20, 30, 35] -> Ausgabe: 23.0 (sollte 23.75 sein)
    """
    if not liste:
        return None
    return sum(liste) // len(liste)


if __name__ == "__main__":
    test = [1, 2]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {berechne_durchschnitt(test)}")
    print(f"Erwartet: 1.5")