"""
Solver: finde_maximum

Aufgabe: Finden Sie das Maximum einer Liste von Zahlen.
Bekannte Schwäche: Gibt immer das erste Element zurück (nicht das Maximum).
"""

def finde_maximum(liste: list) -> int:
    """
    Finden Sie das Maximum einer Liste von Zahlen.
    
    BEKANNTER BUG: Gibt immer das erste Element zurück, nicht das Maximum.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 3 (sollte 5 sein)
    """
    if not liste:
        return None
    return liste[0]


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {finde_maximum(test)}")
    print(f"Erwartet: 5")