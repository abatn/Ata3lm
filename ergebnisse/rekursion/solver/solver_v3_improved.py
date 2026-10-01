"""
Solver v3: finde_maximum (verbessert)

Aufgabe: Finden Sie das Maximum einer Liste von Zahlen.
Bekannte Schwäche behoben: Gibt jetzt das tatsächliche Maximum zurück.
"""

def finde_maximum(liste: list) -> int:
    """
    Finden Sie das Maximum einer Liste von Zahlen.
    
    VERBESSERTER ALGORITHMUS: Nutzt eingebaute max()-Funktion oder manuelle Iteration.
    Eingabe: [3, 1, 4, 1, 5] -> Ausgabe: 5
    """
    if not liste:
        return None
    return max(liste)


if __name__ == "__main__":
    test = [3, 1, 4, 1, 5]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {finde_maximum(test)}")
    print(f"Erwartet: 5")