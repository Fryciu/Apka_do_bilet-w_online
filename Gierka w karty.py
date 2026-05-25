import random
import os
import platform

# Funkcja do czekania na dowolny klawisz
def wait_for_key():
    print("\nNaciśnij dowolny klawisz, aby kontynuować...")
    if platform.system() == 'Windows':
        import msvcrt
        msvcrt.getch()
    else:
        import sys, termios, tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# Listy celów pogrupowane na poziomy trudności
cele = {
    "łatwy": [
        "Zbierz 2 karty tej samej wartości (np. dwa asy)",
        "Zbierz 3 karty w jednym kolorze (np. trzy kiery)",
        "Zbierz sekwencję 2 kart po kolei (np. 7 i 8)",
        "Zbierz 1 figurę (Walet, Dama lub Król)",
        "Zbierz 2 karty w kolorze czerwonym (kier lub karo)",
        "Zbierz najmniejszą i największą kartę w swojej ręce",
        "Zbierz karty o wartościach różniących się o dokładnie 1",
        "Zbierz trzy karty w trzech różnych kolorach",
        "Zbierz karty zajmujące pozycje 2. i 4. w twoim układzie",
        "Zbierz karty, których wartości sumują się do 10"
    ],
    "średni": [
        "Zbierz 3 karty, z których dwie są parą, a trzecia tworzy z nimi sekwencję",
        "Zbierz 3 karty tej samej wartości (np. trzy siódemki)",
        "Zbierz sekwencję 3 kart po kolei (np. 7, 8, 9)",
        "Zbierz 2 pary tych samych wartości (np. dwa asy i dwa króle)",
        "Zbierz karty o wartościach parzystych (2, 4, 6, 8, 10, Dama)",
        "Zbierz 4 karty w jednym kolorze",
        "Zbierz wszystkie walety (J)",
        "Zbierz karty, które mają otwarte 'oczka' (np. 4, 8, 6, 9, Q, A)",
        "Zbierz karty, które nie zawierają 'oczek' (np. 2, 3, 5, 7, J, K)",
        "Zbierz dwie pary, gdzie jedna para jest czerwona, a druga czarna"
    ],
    "trudny": [
        "Zbierz wszystkie karty w kolorze pik (♠)",
        "Zbierz wszystkie karty w kolorze kier (♥)",
        "Zbierz wszystkie karty w kolorze trefl (♣)",
        "Zbierz wszystkie karty w kolorze karo (♦)",
        "Zbierz karty od 10 do Asa (mini-poker)",
        "Zbierz 5 kart o rosnących wartościach (np. 3, 5, 7, 9, W)",
        "Zbierz wszystkie karty, których wartości są liczbami pierwszymi",
        "Zbierz karty tworzące 'lustrzane odbicie' (wartości i kolory symetryczne)",
        "Zbierz 'rodzinę królewską' (Król, Dama, Walet i As)"
    ],
    "szalony": [
        "Zbierz cały kolor i jedną parę (niekoniecznie z tego koloru)",
        "Zbierz sekwencję 4 kart w jednym kolorze",
        "Zbierz wszystkie karty o dwóch wybranych wartościach (np. wszystkie 7 i Q)",
        "Zbierz karty naprzemiennie: czerwona-czarna-czerwona-czarna",
        "Zbierz karty, które były zagrane w poprzedniej turze przez obu graczy",
        "Zbierz karty tworzące dokładne odbicie lustrzane talii przeciwnika",
        "Zbierz karty, których pozycje w twojej ręce sumują się do liczby kart przeciwnika",
        "Zbierz karty, gdzie liczba liter w ich nazwach tworzy ciąg arytmetyczny",
        "Zbierz karty spełniające kolory twojego ulubionego zespołu sportowego",
        "Zbierz karty, których wartości odpowiadają twoim cyfrom z numeru PESEL"
    ]
}

# Grupy wykluczających się celów
wykluczajace_sie = [
    {
        "Zbierz wszystkie karty w kolorze pik (♠)", 
        "Zbierz wszystkie karty w kolorze kier (♥)",
        "Zbierz wszystkie karty w kolorze trefl (♣)", 
        "Zbierz wszystkie karty w kolorze karo (♦)"
    },
    {
        "Zbierz karty o wartościach parzystych (2, 4, 6, 8, 10, Dama)", 
        "Zbierz karty o wartościach nieparzystych (As, 3, 5, 7, 9, Walet, Król)"
    },
    {
        "Zbierz karty, które mają otwarte 'oczka' (np. 4, 8, 6, 9, Q)",
        "Zbierz sekwencję 3 kart po kolei (np. 7, 8, 9)"
    },
    {
        "Zbierz karty, które nie zawierają 'oczek' (np. 2, 3, 5, 7, J, K)",
        "Zbierz karty o wartościach parzystych (2, 4, 6, 8, 10, Dama)"
    }
]

def losuj_cele(poziom, liczba_celow:int):
    """Losuje cele z wybranego poziomu, unikając wykluczających się kombinacji."""
    dostepne_cele = cele[poziom].copy()
    wylosowane = []
    
    for _ in range(liczba_celow):
        if not dostepne_cele:
            break  # Nie ma więcej dostępnych celów
        
        cel = random.choice(dostepne_cele)
        wylosowane.append(cel)
        dostepne_cele.remove(cel)
        
        # Usuń cele wykluczające się z obecnie wylosowanymi
        for grupa in wykluczajace_sie:
            if cel in grupa:
                for wykluczony in grupa:
                    if wykluczony in dostepne_cele:
                        dostepne_cele.remove(wykluczony)
    
    return wylosowane

def main():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    print("Witaj w generatorze celów do gry 'Sabotażysta'!")
    
    while True:
        try:
            print("\nWybierz poziom trudności:")
            print("1. Łatwy\n2. Średni\n3. Trudny\n4. Szalony\n0. Wyjście")
            poziom_input = input("Twój wybór (0-4): ")
            
            if poziom_input == '0':
                print("Do zobaczenia!")
                return
            
            poziom_num = int(poziom_input)
            if poziom_num not in {1, 2, 3, 4}:
                raise ValueError
            
            poziom = ["łatwy", "średni", "trudny", "szalony"][poziom_num - 1]
            max_cele = len(cele[poziom])
            print(f"\nDostępna liczba celów na poziomie {poziom}: {max_cele}")
            
            ile = int(input(f"Ile celów chcesz wylosować? (1-{max_cele}): "))
            if ile < 1 or ile > max_cele:
                print(f"Nieprawidłowa liczba. Losuję {min(ile, max_cele)}.")
                ile = min(ile, max_cele)
            
            cele_wylosowane = losuj_cele(poziom, ile)
            
            print("\n=== WYLOSOWANE CELE ===")
            for i, cel in enumerate(cele_wylosowane, start=1):
                print(f"{i}. {cel}")
            
            wait_for_key()
            os.system('cls' if platform.system() == 'Windows' else 'clear')
            
        except ValueError:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    main()