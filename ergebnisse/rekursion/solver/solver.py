"""
Solver: sortiere_zahlen

Aufgabe: Sortiere eine Liste von Zahlen aufsteigend.
Bekannte Schwäche: Entfernt KEINE Duplikate.
"""

def sortiere_zahlen(liste: list) -> list:
    """
    Sortiert eine Liste von Zahlen aufsteigend.
    
    BEKANNTER BUG: Duplikate werden NICHT entfernt.
    Eingabe: [3, 1, 2, 1, 3] -> Ausgabe: [1, 1, 2, 3, 3] (sollte [1, 2, 3] sein)
    """
    return sorted(liste)


if __name__ == "__main__":
    # Schnelltest
    test = [3, 1, 2, 1, 3]
    print(f"Eingabe: {test}")
    print(f"Ausgabe: {sortiere_zahlen(test)}")
    print(f"Erwartet (ohne Duplikate): [1, 2, 3]")