from datetime import datetime, timezone
import sqlite3
from cryptography.fernet import Fernet
import json
from Interval import Interval

BUK_DURATION = 30
MUZEUM_DURATION = 30
SAFARI_DURATION = 30  # Safari trwa 1 godzinę
PALACE_DURATION = 60  # Pałac trwa 1 godzinę
KUKU_DURATION = 60  # Pałac trwa 1 godzinę
durations = {
        "Muzeum cztery rodziny": MUZEUM_DURATION,
        "Labirynt bukowy": BUK_DURATION,
        "Labirynt z kukurydzy": KUKU_DURATION 
    }



class Ticket:
    def __init__(self,system_arguments_list:list[str], sciezka_zapisu_klucza: str) -> None:
        self.code_not_found_error = 0
        self.file_not_found_error = 0
        self.format_error = 0
        self.exception_error = 0
        self.tickets = list([{"":""},{"":""}])
        self.subcombinations: list[dict[str,int]] = []
        self.safari_data = 
        
        try:
            with open(sciezka_zapisu_klucza, "r", encoding="utf-8") as file:
                key:bytes = file.read().encode()
            cipher_suite = Fernet(key)
            try:
                if len(system_arguments_list) > 1:
                    encrypted_data = system_arguments_list[1] #TODO change that later to [2] so that the factual app will work
                    print(encrypted_data)
                    decrypted_data = cipher_suite.decrypt(encrypted_data)
                    decrypted_json = json.loads(decrypted_data.decode())
                    tickets = decrypted_json
                    # Naprawa nazw biletów
                    for ticket in tickets:
                        ticket['ticket_name'] = ticket['ticket_name'].replace("WejĹ›cie_na_teren", "Wejście na teren").replace("PaĹ‚ac", "Pałac")
                    print("tickets",tickets)
                    self.tickets = tickets

            except FileNotFoundError:
                print("Błąd", "Plik z biletami nie został znaleziony.")
                self.file_not_found_error = 1
            except json.JSONDecodeError:
                print("Błąd", "Nieprawidłowy format pliku JSON.")
                self.format_error = 1
            except Exception:
                print("Błąd", "Zły kod QR")
                self.exception_error = 1
        except FileNotFoundError:
            self.code_not_found_error = 1
            print("Błąd", "Plik z kluczem nie został znaleziony.")

    def get_data(self, type: str, system_arguments_list: list[str]) -> dict[str,int]:
        if type == "safari":
            return sys.a
            
        
    
    def approve_ticket(self) -> None:
        """Funkcja zatwierdzająca bilet."""
        print("Zatwierdzenie", "Bilet został zatwierdzony!") #change that to some other logic
                    
    def is_ticket_expired(self, expiration_date_str: str) -> bool:
        """Sprawdza, czy bilet wygasł."""
        expiration_date = datetime.fromisoformat(expiration_date_str)  # Offset-aware
        current_time = datetime.now(timezone.utc)  # Offset-aware
        return expiration_date < current_time
    
    def is_code_in_db(self, ticket_name: str, authentication_code: str, db_name: str) -> bool:
        """Sprawdza, czy kod autentyfikacyjny znajduje się w odpowiedniej kolumnie bazy danych."""
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Mapowanie nazw atrakcji na nazwy kolumn w bazie danych
        column_mapping = {
            "Pałac": "Pałac",
            "Safari bizon": "Safari bizon",
            "Wejście na teren": "Wejście na teren",
            "Labirynt bukowy": "Labirynt bukowy",
            "Labirynt z kukurydzy": "Labirynt z kukurydzy",
            "Muzeum cztery rodziny": "Muzeum cztery rodziny"
        }

        column_name = column_mapping.get(ticket_name)
        if not column_name:
            return False

        # Zapytanie do bazy danych
        query = f'SELECT "{column_name}" FROM codes WHERE "{column_name}" = ?'
        cursor.execute(query, (authentication_code,))
        result = cursor.fetchone()

        conn.close()
        return result is not None 
    
    def Visit_combinations(self,
                            proposed_safari: list[int],
                            proposed_palace: list[int]) -> None:
        """
        Calculate the decision coefficient based on the presence of specific tickets.

        Args:
            tickets (list): List of ticket dictionaries.
            proposed_safari (list): List of proposed safari start times.
            proposed_palace (list): List of proposed palace start times.

        Returns:
            list: A list of non-overlapping and sorted combinations of safari and palace intervals.
        """
        # Define durations for each attraction
        # Initialize an empty dictionary to store durations of present tickets
        ticket_other_types: dict[str,int] = {}

        # Check each ticket and add its duration if it matches one of the specified attractions
        for ticket in self.tickets:
            ticket_name = ticket['ticket_name']
            if ticket_name in durations:  # Only add tickets that are in the durations dictionary
                ticket_other_types[ticket_name] = durations[ticket_name] #ticket_other_types is a subset of a ticket that

        # Initialize an empty list to store non-overlapping combintations
        current_time = datetime.now().time()  # Pobierz aktualną godzinę
        current_minutes = current_time.hour * 60 + current_time.minute  # Przelicz na minuty od północy
        # Generate all possible combinations of safari and palace intervals
        combination: dict[str,int] = {}

        if proposed_safari == [] and proposed_palace != []:
            for palace_start in proposed_palace:
                palace_interval = Interval(
                    start=palace_start,
                    end=palace_start + PALACE_DURATION,
                    activity_type="palace"
                )
                print("przedział",palace_interval)
                combination = {
                    "Godzina przyjścia": current_minutes,
                    **palace_interval.to_dict()
                }
                combination = dict(sorted(combination.items(), key=lambda item: item[1]))
                self.subcombinations.append(combination)

        elif proposed_palace == [] and proposed_safari != []:
            for safari_start in proposed_safari:
                safari_interval = Interval(
                    start=safari_start,
                    end=safari_start + SAFARI_DURATION,
                    activity_type="safari"
                )
                print("przedział",safari_interval)
                combination = {
                    "Godzina przyjścia": current_minutes,
                    **safari_interval.to_dict()
                }
                combination = dict(sorted(combination.items(), key=lambda item: item[1]))
                self.subcombinations.append(combination)
        elif proposed_palace != [] and proposed_safari != []:
            for safari_start in proposed_safari: #jeśli nie mamy biletu safari to tego się pozbywamy
                safari_interval = Interval(
                    start=safari_start,
                    end=safari_start + SAFARI_DURATION,
                    activity_type="safari"
                )

                for palace_start in proposed_palace:
                    palace_interval = Interval(
                        start=palace_start,
                        end=palace_start + PALACE_DURATION,
                        activity_type="palace"
                    )
                    print("przedział",palace_interval)
                    if not safari_interval.overlaps_with(palace_interval):
                        combination = {
                            "Godzina przyjścia": current_minutes,
                            **safari_interval.to_dict(), #jeśli nie mamy biletu safari to tego się pozbywamy
                            **palace_interval.to_dict()
                        }
                        combination = dict(sorted(combination.items(), key=lambda item: item[1]))
                        self.subcombinations.append(combination)
        else:
            combination = {
                    "Godzina przyjścia": current_minutes,
                }
            self.subcombinations.append(combination)

        # Sort the subcombinations list based on the 'proposed_safari_beginning' time
        print("kombinacjeee",self.subcombinations)
        self.subcombinations.sort(key=lambda x: x['proposed_safari_beginning'])
    
    def optimal_hours(self) -> dict[str,int]:

        def get_key(zmienna: int) -> str:
            for key, value in durations_local.items():
                if zmienna == value:
                    return key
            return ""  # Return None if no match is found


        combinations = self.Visit_combinations(self.tickets, proposed_safari, proposed_palace) #list of combinations
        coefficients = []
        durations_local = durations.copy()
        print("durations_local --------------------------------------------------------",durations_local) 
        list_from_durations=[]
        #proposed_non_time_attractions = []
        print(combinations)
        has_labirynt_bukowy = any(ticket['ticket_name'] == 'Labirynt bukowy' for ticket in tickets)
        has_labirynt_kukurydziany = any(ticket['ticket_name'] == 'Labirynt kukurydziany' for ticket in tickets)
        has_muzeum = any(ticket['ticket_name'] == 'Muzeum cztery rodziny' for ticket in tickets)
        durations_local = {key: value for key, value, keep in zip(durations_local.keys(), 
                                                                  durations_local.values(), 
                                                                  [has_muzeum,has_labirynt_bukowy,has_labirynt_kukurydziany]) if keep} #dictionary containing valid tickets for non-time based attractions
        for _, values in durations_local.items():
            list_from_durations.append(values) #list of durations
        list_from_durations: list[int]= sorted(list_from_durations) #that is later sorted
        list_of_dicts: list[dict[str,Any]] = [{}]
        for dictionary in combinations: #We check every combination
            optimal_coefficient = 0
            listfromdict: list[tuple[str,int]] = list(dictionary.items()) #list of one combination
            print("list_from_dict", listfromdict)
            outer_loop = greenlet.getcurrent()
            for i in range(1, len(listfromdict), 2):
                #print()
                if len(listfromdict)%2 == 0:
                    added_symbol: int = listfromdict[i+1][1] - listfromdict[i][1]
                else: 
                    added_symbol = listfromdict[i][1] - listfromdict[i-1][1] 
                if list_from_durations == []:
                    pass
                else:
                    j = 0
                    for duration_value in list_from_durations:
                        if added_symbol > duration_value:
                            print("lista_from_durations",list_from_durations)
                            print(j)
                            added_symbol -= list_from_durations[j]
                            print(list_from_durations[j])
                            print("Argument do metody pop",get_key(list_from_durations[j]))
                            print(durations_local)
                            item: int = list_from_durations[j]
                            print("lista której szukam",list(durations_local.items())[j])
                            temp: tuple[str, int] = list(durations_local.items())[j]

                            key, dict_value = temp
                            # Add the first key-value pair to dict2
                            list_of_dicts.append({"Klucz": key,"dict_value": dict_value+listfromdict[i][1], "iteracja": i})
                            print(list_of_dicts)

                            durations_local.pop(get_key(item))
                            list_from_durations.remove(item)
                            outer_loop.switch()
                        j +=1

                optimal_coefficient += added_symbol
            coefficients.append(optimal_coefficient)
        if coefficients == []:
            print("tablica combinations pusta")
            return {}
        else:
            print("tablica combinations niepusta")
            minimal = min(coefficients)
            print("minimal", minimal)
            #print(minimal)
            temp = coefficients.index(minimal)
            #print(temp)
            #print(combinations)

            final_dict = combinations[temp]
            nazwa = ""

            for attract_info in list_of_dicts:
                print(attract_info.items())
                for key, value in attract_info.items():
                    if key == 'Klucz':
                        nazwa = value
                    if key == 'dict_value':
                        wartość = value
                        final_dict[nazwa] = wartość

            final_dict = {key: val for key, val in sorted(final_dict.items(), key = lambda ele: ele[1])}
            print("final_dict: ",final_dict)
            return final_dict
    
    def propose_hours(self, safari_data, palace_data):
        """Proponuje godziny atrakcji na podstawie aktualnej godziny i dostępnych terminów."""
        current_time = datetime.now().time()  # Pobierz aktualną godzinę
        current_minutes = current_time.hour * 60 + current_time.minute  # Przelicz na minuty od północy     # Dostępne godziny dla Safari i Pałacu
        safari_hours = sorted(safari_data.keys())  # Posortowane godziny Safari
        palace_hours = sorted(palace_data.keys())  # Posortowane godziny Pałacu
        print(safari_hours)
        print(palace_hours)
        # Propozycje godzin
        proposed_safari: list[int] = []
        proposed_palace: list[int] = []        # Sprawdź, które godziny Safari są możliwe
        for hour in safari_hours:
            if hour >= current_minutes - 3:  # Minimalny czas na dojazd: 3 minut
                proposed_safari.append(hour)        # Sprawdź, które godziny Pałacu są możliwe
        for hour in palace_hours:
            if hour >= current_minutes - 3:  # Minimalny czas na dojazd: 3 minut
                proposed_palace.append(hour)

        print(proposed_palace)
        print(proposed_safari)
        self.optimal_hours(self.tickets, proposed_safari, proposed_palace)    
    
    
    def display_all_hours(self):
        pass