from __future__ import annotations  # Must be at the top of the file
import json
from datetime import datetime, timezone, date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from cryptography.fernet import Fernet
import sqlite3
import sys
from datetime import datetime
import pandas as pd
from typing import Any


"""
    Zrobione testy:
    Bez safari
    Bez pałacu i safari
    
    Niezaliczone testy:

"""


class Interval:
    """
    Represents an interval with a start and end time.
    """
    def __init__(self, start: int =0, end: int =0, activity_type : str ="proposed_safari_beginning"):
        self.start = start
        self.end = end
        self.activity_type = activity_type  # e.g., "safari" or "palace"

    def overlaps_with(self, other: Interval):
        """
        Check if this interval overlaps with another interval.
        """
        return not (self.end <= other.start or other.end <= self.start)

    def to_dict(self):
        """
        Convert the interval to a dictionary with activity-specific keys.
        """
        if self.activity_type == "safari":
            return {
                "proposed_safari_beginning": self.start,
                "proposed_safari_end": self.end
            }
        elif self.activity_type == "palace":
            return {
                "proposed_palace_beginning": self.start,
                "proposed_palace_end": self.end
            }
        else:
            raise ValueError("Invalid activity type")



# Ścieżki do plików
current_script_dir = Path(__file__).parent
sciezka_zapisu_klucza = current_script_dir / "Klucz.txt"
db_name = current_script_dir / "random_codes.db"  # Ścieżka do bazy danych
db_used_name = current_script_dir / "random_used_codes.db"  # Ścieżka do bazy danych

schedule_address = current_script_dir / 'data.json'
config_file = current_script_dir / "config.json"


if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)
else:
    config = {'day': date.today().isoformat(), 'mode': 'light'}


root = tk.Tk()

with open(schedule_address, 'r') as file:
    data = json.load(file)
    
safari_data = data[0]
#safari_data={}
palace_data = data[1]

def str_key_2_int(json):
    data_int_keys = {}
    for key_str, value in json.items():
        try:
            key_int = int(key_str)
            data_int_keys[key_int] = value
        except ValueError:
            # Handle cases where the key might not be a valid integer string
            data_int_keys[key_str] = value
    return data_int_keys

safari_data = str_key_2_int(safari_data)
palace_data = str_key_2_int(palace_data)

#palace_data = {1439: {'Godzina': 1439, 'Liczba osób': 0, 'Maksymalna liczba osób': 0}}
#palace_data = {}

codes_used: dict[str, list[str]] = {
    "Pałac": [],
    "Safari bizon": [],
    "Wejście na teren": [],
    "Labirynt bukowy": [],
    "Labirynt z kukurydzy": [],
    "Muzeum cztery rodziny": []
}

# Czas trwania atrakcji (w minutach)
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
# Wczytanie klucza szyfrującego
try:
    with open(sciezka_zapisu_klucza, "r", encoding="utf-8") as file:
        key:bytes = file.read().encode()
    cipher_suite = Fernet(key)
except FileNotFoundError:
    messagebox.showerror("Błąd", "Plik z kluczem nie został znaleziony.")
    exit()



# Funkcja do naprawy błędnie zakodowanych nazw
def fix_encoding(text:str) -> str:
    # Zdekoduj jako ISO-8859-1, a następnie zakoduj jako UTF-8
    return text.encode('iso-8859-1').decode('utf-8')

# Wczytanie i odszyfrowanie biletów

# Tutaj jest pobieranie biletu i robienie z niego zmiennej "tickets"
try:
    if len(sys.argv) > 1:
        encrypted_data = sys.argv[1]
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        decrypted_json = json.loads(decrypted_data.decode())
        tickets = decrypted_json
        # Naprawa nazw biletów
        for ticket in tickets:
            ticket['ticket_name'] = ticket['ticket_name'].replace("WejĹ›cie_na_teren", "Wejście na teren").replace("PaĹ‚ac", "Pałac")
        
except FileNotFoundError:
    messagebox.showerror("Błąd", "Plik z biletami nie został znaleziony.")
    exit()
except json.JSONDecodeError:
    messagebox.showerror("Błąd", "Nieprawidłowy format pliku JSON.")
    exit()
except Exception:
    messagebox.showerror("Błąd", "Zły kod QR")
    exit()

def filter_attraction_times(tickets: list[dict], safari_data: dict, palace_data: dict) -> tuple[dict, dict]:
        """
        Filters available times for Safari and Palace based on the number of people in the tickets.

        Args:
            tickets: A list of ticket dictionaries.
            safari_data: A dictionary of available Safari times and capacity.
            palace_data: A dictionary of available Palace times and capacity.

        Returns:
            A tuple containing the filtered safari_data and palace_data dictionaries.
        """
        safari_people_count = sum(ticket['number_of_people'] for ticket in tickets if ticket['ticket_name'] == "Safari bizon")
        palace_people_count = sum(ticket['number_of_people'] for ticket in tickets if ticket['ticket_name'] == "Pałac")

        filtered_safari_data = {}
        for time, data in safari_data.items():
            available_space = data['Maksymalna liczba osób'] - data['Liczba osób']
            if safari_people_count <= available_space:
                filtered_safari_data[time] = data

        filtered_palace_data = {}
        for time, data in palace_data.items():
            available_space = data['Maksymalna liczba osób'] - data['Liczba osób']
            if palace_people_count <= available_space:
                filtered_palace_data[time] = data
                

        return filtered_safari_data, filtered_palace_data

newsafari_data, newpalace_data = filter_attraction_times(tickets= tickets, safari_data= safari_data, palace_data=palace_data)
safari_data = newsafari_data
palace_data = newpalace_data

def number_to_hour(list: list[int]) -> list[str]: # A function for changing list of numbers to hours. Maybe it isn't of datetime type, but it doesn't matter
    new_list: list[str] = []
    for item in list:
        minutes: int = item%60
        hours: int = int((item - (item%60))/60)
        if minutes < 10:
            text: str = f"{hours}:0{minutes}"
        else:
            text = f"{hours}:{minutes}"
        new_list.append(text)
    return new_list
        
#------------------------------------------------------------------------------------
def approve_ticket() -> None:
    """Funkcja zatwierdzająca bilet."""
    optimal_schedule_dict: dict[str, int] = optimal_hours(
        tickets=tickets,
        proposed_palace=propose_hours(safari_data=safari_data, palace_data=palace_data)[0],
        proposed_safari=propose_hours(safari_data=safari_data, palace_data=palace_data)[1]
    )
    print("safari_data: ",safari_data)
    safari_people_count = sum(ticket['number_of_people'] for ticket in tickets if ticket['ticket_name'] == "Safari bizon")
    palace_people_count = sum(ticket['number_of_people'] for ticket in tickets if ticket['ticket_name'] == "Pałac")
    if safari_data:
        for time_key, term_data in safari_data.items():
            if optimal_schedule_dict["proposed_safari_beginning"] == time_key:
                if "Liczba osób" in term_data:
                    term_data["Liczba osób"] += safari_people_count
                    print(f"Updated Safari {time_key}: {term_data['Liczba osób']}")
                    print(f"Added count: {safari_people_count}")      
    print(safari_data)
    print("palace_data: ",palace_data)
    if palace_data:
        for time_key, term_data in palace_data.items():
            if optimal_schedule_dict["proposed_palace_beginning"] == time_key:
                if "Liczba osób" in term_data:
                    term_data["Liczba osób"] += palace_people_count
                    print(f"Updated Palace {time_key}: {term_data['Liczba osób']}")
                    print(f"Added count: {palace_people_count}")    
    print(palace_data)
    schedules = [safari_data, palace_data]
    
    with open(schedule_address, 'w') as f:
        json.dump(schedules, f)
        
    
    root.destroy()

#------------------------------------------------------------------------------------



def is_ticket_expired(expiration_date_str: str) -> bool:
    """Sprawdza, czy bilet wygasł."""
    expiration_date = datetime.fromisoformat(expiration_date_str)  # Offset-aware
    current_time = datetime.now(timezone.utc)  # Offset-aware
    return expiration_date < current_time


def is_code_in_db(ticket_name: str, authentication_code: str) -> bool:
    """Sprawdza, czy kod autentyfikacyjny znajduje się w odpowiedniej kolumnie bazy danych."""
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

    # Sprawdzenie w głównej bazie danych
    conn1 = sqlite3.connect(db_name)
    cursor1 = conn1.cursor()
    query = f'SELECT "{column_name}" FROM codes WHERE "{column_name}" = ?'
    cursor1.execute(query, (authentication_code,))
    result1 = cursor1.fetchone()
    conn1.close()

    if result1 is None:
        return False  # Kod nie istnieje w głównej bazie

    # Sprawdzenie czy kod został już użyty
    conn2 = sqlite3.connect(db_used_name)
    cursor2 = conn2.cursor()
    
    # Utworzenie tabeli jeśli nie istnieje (możesz to zrobić raz podczas inicjalizacji)
    cursor2.execute(f'CREATE TABLE IF NOT EXISTS codes ("{column_name}" TEXT)')
    
    cursor2.execute(query, (authentication_code,))
    result2 = cursor2.fetchone()
    
    if result2 is not None:
        conn2.close()
        return False  # Kod został już wcześniej użyty
    
    # Dodanie kodu do bazy użytych kodów
    insert_query = f'INSERT INTO codes ("{column_name}") VALUES (?)'
    cursor2.execute(insert_query, (authentication_code,))
    conn2.commit()
    conn2.close()
    
    return True




#GUI object that should take the ticket and display it --------------------------------------------------------------------------
from typing import Dict, TextIO
from tkinter import scrolledtext

def display_ticket_info(
    ticket: Dict[str, str],
    text_widget: Union[scrolledtext.ScrolledText, TextIO],
    show_validation: bool = True
) -> None:
    """
    Display formatted ticket information with optional validation.
    
    Args:
        ticket: Ticket dictionary
        text_widget: Output target (Tkinter widget or file-like)
        show_validation: Whether to show validation status
    """
    # Prepare validation markers if enabled
    if show_validation:
        code_valid = "✔️" if is_code_in_db(
            ticket['ticket_name'], 
            ticket['authentication_code']
        ) else "❌"
        
        expired = is_ticket_expired(ticket['expiration_date'])
        expiry_marker = "❌" if expired else "✔️"
    
    # Build output lines
    lines = [
        f"Informacje o bilecie: {ticket['ticket_name']}",
        f"Typ biletu: {ticket['ticket_type']}",
        f"Liczba osób: {ticket['number_of_people']}"
    ]
    
    if show_validation:
        lines.extend([
            f"Kod autentyfikacyjny: {ticket['authentication_code']} {code_valid}",
            f"Data wygaśnięcia: {ticket['expiration_date']} {expiry_marker}"
        ])
    
    # Handle different output targets
    if isinstance(text_widget, scrolledtext.ScrolledText):
        text_widget.configure(state="normal")
        for line in lines:
            text_widget.insert(tk.END, line + "\n")
        text_widget.insert(tk.END, "-" * 40 + "\n")
        text_widget.configure(state="disabled")
    else:
        # Fallback for file-like objects
        for line in lines:
            text_widget.write(line + "\n")
        text_widget.write("-" * 40 + "\n")



#GUI object that should have the logic of it seperated--------------------------------------------------------------------------
#Ticket object --------------------------------------------------------------------------
def Visit_combinations(tickets: list[dict[str,str]],
                       proposed_safari: list[int],
                       proposed_palace: list[int]) -> list[dict[str,int]]:
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
    ticket_other_types = {}

    # Check each ticket and add its duration if it matches one of the specified attractions
    for ticket in tickets:
        ticket_name = ticket['ticket_name']
        if ticket_name in durations:  # Only add tickets that are in the durations dictionary
            ticket_other_types[ticket_name] = durations[ticket_name]
    #print(ticket_other_types)
    
    # Initialize an empty list to store non-overlapping combinations
    subcombinations: list[dict[str,int]] = []
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
            combination = {
                "Godzina przyjścia": current_minutes,
                **palace_interval.to_dict()
            }
            combination = dict(sorted(combination.items(), key=lambda item: item[1]))
            subcombinations.append(combination)

    elif proposed_palace == [] and proposed_safari != []:
        for safari_start in proposed_safari:
            safari_interval = Interval(
                start=safari_start,
                end=safari_start + SAFARI_DURATION,
                activity_type="safari"
            )
            combination = {
                "Godzina przyjścia": current_minutes,
                **safari_interval.to_dict()
            }
            combination = dict(sorted(combination.items(), key=lambda item: item[1]))
            subcombinations.append(combination)
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
                if not safari_interval.overlaps_with(palace_interval):
                    combination = {
                        "Godzina przyjścia": current_minutes,
                        **safari_interval.to_dict(), #jeśli nie mamy biletu safari to tego się pozbywamy
                        **palace_interval.to_dict()
                    }
                    combination = dict(sorted(combination.items(), key=lambda item: item[1]))
                    subcombinations.append(combination)
    else:
        subcombinations.append(combination)

    # Sort the subcombinations list based on the 'proposed_safari_beginning' time
    subcombinations.sort(key=lambda x: x['proposed_safari_beginning'])
    return subcombinations

#Ticket object --------------------------------------------------------------------------    
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Attraction:
    name: str
    duration: int
    available: bool

def optimal_hours(
    tickets: List[Dict[str, Any]],
    proposed_safari: List[int],
    proposed_palace: List[int]
) -> Dict[str, int]:
    """
    Calculate optimal non-overlapping schedule for attractions.
    
    Args:
        tickets: List of ticket dictionaries
        proposed_safari: Available safari start times in minutes
        proposed_palace: Available palace start times in minutes
        
    Returns:
        Dictionary of attraction names to start times
    """
    
    # 1. Setup and validation
    if not proposed_safari and not proposed_palace:
        return {}
    
    # 2. Get available non-time attractions
    non_time_attractions = _get_non_time_attractions(tickets)
    
    # 3. Generate possible time-based attraction combinations
    time_based_combos = _generate_time_combinations(
        proposed_safari, 
        proposed_palace
    )
    
    # 4. Find best schedule with non-time attractions
    best_schedule = _find_optimal_schedule(
        time_based_combos,
        non_time_attractions
    )
    
    return best_schedule

def _get_non_time_attractions(tickets: List[Dict[str, Any]]) -> List[Attraction]:
    """Filter and return available non-time-based attractions."""
    available = []
    present_attractions = {
        'Muzeum cztery rodziny': any(t['ticket_name'] == 'Muzeum cztery rodziny' for t in tickets),
        'Labirynt bukowy': any(t['ticket_name'] == 'Labirynt bukowy' for t in tickets),
        'Labirynt z kukurydzy': any(t['ticket_name'] == 'Labirynt z kukurydzy' for t in tickets)
    }
    
    for name, duration in durations.items():
        if present_attractions.get(name, False):
            available.append(Attraction(name, duration, True))
    
    return sorted(available, key=lambda x: x.duration)

def _generate_time_combinations(
    safari_times: List[int],
    palace_times: List[int]
) -> List[Dict[str, int]]:
    """Generate non-overlapping time-based attraction combinations."""
    combinations = []
    current_time = datetime.now().time()
    current_minutes = current_time.hour * 60 + current_time.minute
    
    # Handle all possible combinations
    for safari_start in safari_times:
        safari_end = safari_start + SAFARI_DURATION
        
        for palace_start in palace_times:
            palace_end = palace_start + PALACE_DURATION
            
            if not (palace_end <= safari_start or safari_end <= palace_start):
                continue  # Skip overlapping times
                
            combo = {
                "Godzina przyjścia": current_minutes,
                "proposed_safari_beginning": safari_start,
                "proposed_safari_end": safari_end,
                "proposed_palace_beginning": palace_start,
                "proposed_palace_end": palace_end
            }
            combinations.append(combo)
    
    return sorted(combinations, key=lambda x: x['proposed_safari_beginning'])

def _find_optimal_schedule(
    time_combos: List[Dict[str, int]],
    non_time_attractions: List[Attraction]
) -> Dict[str, int]:
    """Find schedule that finishes earliest, respecting time-based attraction boundaries."""
    if not time_combos:
        return {}

    earliest_end_time = float('inf')
    best_full_schedule = {}

    for combo in time_combos:
        current_schedule = combo.copy()
        remaining_non_time = sorted(list(non_time_attractions), key=lambda x: x.duration)
        arrival_time = combo['Godzina przyjścia']
        safari_start = combo.get('proposed_safari_beginning')
        safari_end = combo.get('proposed_safari_end')
        palace_start = combo.get('proposed_palace_beginning')
        palace_end = combo.get('proposed_palace_end')

        potential_slots = []
        if safari_start is not None and palace_start is not None:
            potential_slots.append((arrival_time, min(safari_start, palace_start)))
            if safari_start < palace_start:
                potential_slots.append((safari_end, palace_start))
            else:
                potential_slots.append((palace_end, safari_start))
            potential_slots.append((max(safari_end, palace_end), 1440))
        elif safari_start is not None:
            potential_slots.append((arrival_time, safari_start))
            potential_slots.append((safari_end, 1440))
        elif palace_start is not None:
            potential_slots.append((arrival_time, palace_start))
            potential_slots.append((palace_end, 1440))
        else:
            potential_slots.append((arrival_time, 1440))

        unscheduled_non_time = list(remaining_non_time)
        current_non_time_schedule = {}

        for start, end in sorted(potential_slots):
            gap_duration = end - start
            if gap_duration > 0 and unscheduled_non_time:
                filled_in_slot = _fill_gap_within_bounds(
                    gap_duration, unscheduled_non_time, current_non_time_schedule, start
                )
                for name, start_time in filled_in_slot.items():
                    if name not in current_non_time_schedule:
                        current_non_time_schedule[name] = start_time
                        unscheduled_non_time = [attr for attr in unscheduled_non_time if attr.name != name]

        current_full_schedule = current_schedule.copy()
        current_full_schedule.update(current_non_time_schedule)

        # Calculate the end time of the last scheduled activity
        last_end_time = arrival_time
        for activity, start in current_full_schedule.items():
            duration = durations.get(activity, 0)
            last_end_time = max(last_end_time, start + duration)

        if last_end_time < earliest_end_time:
            earliest_end_time = last_end_time
            best_full_schedule = current_full_schedule.copy()

    return best_full_schedule

def _fill_gap_within_bounds(
    gap: int,
    attractions: List[Attraction],
    current_schedule: Dict[str, int],
    slot_start_time: int
) -> Dict[str, int]:
    """Try to fill a time gap with non-time attractions without exceeding the gap boundaries."""
    remaining_gap = gap
    scheduled_in_gap = {}
    current_time = slot_start_time
    sorted_attractions = sorted([
        attr for attr in attractions if attr.name not in current_schedule
    ], key=lambda x: x.duration)


    for attraction in sorted_attractions:
        if attraction.duration <= remaining_gap:
            potential_end_time = current_time + attraction.duration
            if potential_end_time <= slot_start_time + gap:
                scheduled_in_gap[attraction.name] = current_time
                current_schedule[attraction.name] = current_time # Update schedule
                remaining_gap -= attraction.duration
                current_time += attraction.duration

    return scheduled_in_gap

    
    
#Ticket object --------------------------------------------------------------------------    
def propose_hours(safari_data, palace_data) -> list[list[int]]:
    """Proponuje godziny atrakcji na podstawie aktualnej godziny i dostępnych terminów."""
    current_time = datetime.now().time()  # Pobierz aktualną godzinę
    current_minutes = current_time.hour * 60 + current_time.minute  # Przelicz na minuty od północy

    # Dostępne godziny dla Safari i Pałacu
    safari_hours = sorted(safari_data.keys())  # Posortowane godziny Safari
    palace_hours = sorted(palace_data.keys())  # Posortowane godziny Pałacu
    # Propozycje godzin
    proposed_safari = []
    proposed_palace = []

    # Sprawdź, które godziny Safari są możliwe
    for hour in safari_hours:
        if hour >= current_minutes - 3:  # Minimalny czas na dojazd: 3 minut
            proposed_safari.append(hour)

    # Sprawdź, które godziny Pałacu są możliwe
    for hour in palace_hours:
        if hour >= current_minutes - 3:  # Minimalny czas na dojazd: 3 minut
            proposed_palace.append(hour)
            
    optimal_hours(tickets, proposed_safari, proposed_palace)


    return proposed_palace, proposed_safari


#Date object --------------------------------------------------------------------------    
def format_minutes_to_time(minutes):
    """Przelicza minuty od północy na format HH:MM."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"



#GUI object --------------------------------------------------------------------------    
def update_hours_frame(hours_frame, proposed_hours):
    """Aktualizuje ramkę z godzinami atrakcji."""
    for widget in hours_frame.winfo_children():
        widget.destroy()

    row = 0
    for attraction, time in proposed_hours.items():
        if time is not None:
            label = tk.Label(hours_frame, text=f"{attraction}: {format_minutes_to_time(time)}", font=("Arial", 12, "bold"))
            label.grid(row=row, column=0, sticky="w")
        else:
            label = tk.Label(hours_frame, text=f"{attraction}: Nie dostępne", font=("Arial", 12, "bold"))
            label.grid(row=row, column=0, sticky="w")
        row += 1



#GUI object --------------------------------------------------------------------------    
def display_all_info(normal_text, reduced_text, hours_frame, safari_data, palace_data):
    """Wyświetla wszystkie bilety i proponuje godziny atrakcji."""
    normal_text.configure(state="normal")
    reduced_text.configure(state="normal")
    normal_text.delete(1.0, tk.END)
    reduced_text.delete(1.0, tk.END)
    # Proponuj godziny atrakcji
    proposed_hours = propose_hours(safari_data, palace_data)
    #update_hours_frame(hours_frame, proposed_hours)

    # Reszta funkcji pozostaje bez zmian
    ticket_groups = {}
    for ticket in tickets:
        ticket_name = ticket['ticket_name']
        ticket_groups.setdefault(ticket_name, []).append(ticket)

    i = 0
    for ticket_name, ticket_list in ticket_groups.items():
        normal_tickets = [t for t in ticket_list if t['ticket_type'] == "normal"]
        reduced_tickets = [t for t in ticket_list if t['ticket_type'] == "reduced"]

        for ticket in normal_tickets:
            display_ticket_info(ticket, normal_text)

        for ticket in reduced_tickets:
            display_ticket_info(ticket, reduced_text)

    normal_text.configure(state="disabled")
    reduced_text.configure(state="disabled")

class DarkMode:
    """Klasa zarządzająca trybem ciemnym aplikacji."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style()
        self.is_dark = False
        self.option_menus = []  # Track all OptionMenu widgets
        
        # Kolory dla trybu jasnego
        self.light_colors = {
            'bg': '#f0f0f0',
            'fg': 'black',
            'text_bg': 'white',
            'text_fg': 'black',
            'button_bg': '#e0e0e0',
            'frame_bg': '#f0f0f0',
            'entry_bg': 'white',
            'entry_fg': 'black',
            'option_menu_bg': 'white',
            'option_menu_fg': 'black',
            'menu_bg': 'white',
            'menu_fg': 'black',
            'active_bg': '#d0d0d0',
            'active_fg': 'black',
            'highlight_bg': '#f0f0f0'
        }
        
        # Kolory dla trybu ciemnego
        self.dark_colors = {
            'bg': '#2d2d2d',
            'fg': 'white',
            'text_bg': '#444444',
            'text_fg': 'white',
            'button_bg': '#444444',
            'frame_bg': '#2d2d2d',
            'entry_bg': '#444444',
            'entry_fg': 'white',
            'option_menu_bg': '#444444',
            'option_menu_fg': 'white',
            'menu_bg': '#555555',
            'menu_fg': 'white',
            'active_bg': '#666666',
            'active_fg': 'white',
            'highlight_bg': '#2d2d2d'
        }
    
    def add_option_menu(self, option_menu):
        """Add an OptionMenu to be managed by the theme"""
        self.option_menus.append(option_menu)
        self._style_option_menu(option_menu)
    
    def toggle(self):
        """Przełącz między trybem jasnym a ciemnym."""
        self.is_dark = not self.is_dark
        self.apply_theme()
        # Update config file
        config['mode'] = 'dark' if self.is_dark else 'light'
        with open(config_file, 'w') as f:
            json.dump(config, f)
    
    def apply_theme(self):
        """Zastosuj wybrany motyw do wszystkich widgetów."""
        colors = self.dark_colors if self.is_dark else self.light_colors
        
        # Konfiguracja stylów ttk
        self.style.theme_use('clam')
        self.style.configure('.', 
                           background=colors['bg'],
                           foreground=colors['fg'],
                           fieldbackground=colors['entry_bg'],
                           selectbackground=colors['entry_bg'],
                           selectforeground=colors['entry_fg'])
        
        # Style all standard widgets
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TButton', 
                           background=colors['button_bg'],
                           foreground=colors['fg'],
                           bordercolor=colors['button_bg'])
        
        # Style OptionMenus
        for option_menu in self.option_menus:
            self._style_option_menu(option_menu)
        
        # Konfiguracja głównego okna
        self.root.configure(bg=colors['bg'])
        
        # Aktualizacja wszystkich istniejących widgetów
        self._update_widgets(self.root, colors)
    
    def _style_option_menu(self, option_menu):
        """Style an OptionMenu according to current theme"""
        colors = self.dark_colors if self.is_dark else self.light_colors
        
        option_menu.config(
            bg=colors['option_menu_bg'],
            fg=colors['option_menu_fg'],
            activebackground=colors['active_bg'],
            activeforeground=colors['active_fg'],
            highlightbackground=colors['highlight_bg']
        )
        
        # Configure the dropdown menu
        menu = option_menu['menu']
        menu.config(
            bg=colors['menu_bg'],
            fg=colors['menu_fg'],
            activebackground=colors['active_bg'],
            activeforeground=colors['active_fg'],
            selectcolor=colors['menu_fg']
        )

    def _update_widgets(self, parent, colors):
        """Rekurencyjnie aktualizuj wszystkie widgety."""
        for child in parent.winfo_children():
            widget_type = child.winfo_class()
            
            if widget_type in ('Frame', 'TFrame', 'TLabelframe'):
                child.configure(background=colors['bg'])
            elif widget_type == 'Label':
                child.configure(bg=colors['bg'], fg=colors['fg'])
            elif widget_type == 'Button':
                child.configure(bg=colors['button_bg'], fg=colors['fg'],
                              activebackground=colors['active_bg'],
                              activeforeground=colors['active_fg'])
            elif widget_type in ('Text', 'ScrolledText'):
                child.configure(bg=colors['text_bg'], fg=colors['text_fg'],
                              insertbackground=colors['text_fg'])
            elif widget_type == 'Entry':
                child.configure(bg=colors['entry_bg'], fg=colors['entry_fg'],
                              insertbackground=colors['entry_fg'])
            
            if child.winfo_children():
                self._update_widgets(child, colors)
def display_all_hours(normal_text: scrolledtext.ScrolledText,
                    reduced_text: scrolledtext.ScrolledText,
                    hours_frame: tk.Frame,
                    dark_mode: DarkMode):  # Add dark_mode parameter
    """Wyświetla godziny o których osoby mają mieć atrakcje"""
    ticket_groups: dict[str, Any] = {}
    for ticket in tickets:
        ticket_groups.setdefault(ticket['ticket_name'], []).append(ticket)
    i = 0

    optimal_schedule_dict: dict[str, int] = optimal_hours(
        tickets=tickets,
        proposed_palace=propose_hours(safari_data=safari_data, palace_data=palace_data)[0],
        proposed_safari=propose_hours(safari_data=safari_data, palace_data=palace_data)[1]
    )

    non_time_attraction_vars: Dict[str, tk.StringVar] = {}

    for ticket_name, _ in ticket_groups.items():
        if ticket_name in ["Safari bizon", "Pałac"]:
            label = tk.Label(hours_frame, text=f"Godziny dla {ticket_name}: ", font=("Arial", 12, "bold"))
            label.grid(row=i, column=0, sticky="w")

            combinations: list[dict[str, int]] = Visit_combinations(
                tickets=tickets,
                proposed_palace=propose_hours(safari_data=safari_data, palace_data=palace_data)[0],
                proposed_safari=propose_hours(safari_data=safari_data, palace_data=palace_data)[1]
            )
            df: pd.DataFrame = pd.DataFrame(combinations)
            hours_options_int = [0]
            hours_var = tk.StringVar(value="Nie dostępne")

            if ticket_name == "Pałac":
                try:
                    if "proposed_palace_beginning" in optimal_schedule_dict:
                        hours_var.set(format_minutes_to_time(optimal_schedule_dict["proposed_palace_beginning"]))
                    if "proposed_palace_beginning" in df.columns:
                        hours_options_int: list[int] = sorted(df["proposed_palace_beginning"].unique().tolist())
                except KeyError:
                    pass
            elif ticket_name == "Safari bizon":
                try:
                    if "proposed_safari_beginning" in optimal_schedule_dict:
                        hours_var.set(format_minutes_to_time(optimal_schedule_dict["proposed_safari_beginning"]))
                    if "proposed_safari_beginning" in df.columns:
                        hours_options_int: list[int] = sorted(df["proposed_safari_beginning"].unique().tolist())
                except Exception:
                    pass

            hours_options: list[str] = number_to_hour(hours_options_int)
            
            # Create OptionMenu
            option_menu = tk.OptionMenu(hours_frame, hours_var, *hours_options)
            option_menu.grid(row=i, column=1, sticky="ew")
            
            # Register the OptionMenu with dark mode manager
            dark_mode.add_option_menu(option_menu)

        elif ticket_name in ["Muzeum cztery rodziny", "Labirynt z kukurydzy", "Labirynt bukowy"]:
            label = tk.Label(hours_frame, text=f"Godziny dla {ticket_name}: ", font=("Arial", 12, "bold"))
            label.grid(row=i, column=0, sticky="w")
            time_var = tk.StringVar(value="Dowolne")
            if ticket_name in optimal_schedule_dict:
                time_var.set(format_minutes_to_time(optimal_schedule_dict[ticket_name]))
            entry = tk.Entry(hours_frame, font=("Arial", 12), width=10, textvariable=time_var)
            entry.grid(row=i, column=1, sticky="ew")
            non_time_attraction_vars[ticket_name] = time_var

        i += 1

    normal_text.configure(state="disabled")
    reduced_text.configure(state="disabled")

def main():
    """Główna funkcja aplikacji."""
    root.title("Weryfikator Biletów")
    root.state('zoomed')
    dark_mode = DarkMode(root)
    # Main container frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Przycisk do przełączania trybu w prawym górnym rogu
    mode_button = tk.Button(root, text="☀️/🌙", 
                          command=dark_mode.toggle,
                          font=("Arial", 12))
    mode_button.pack(anchor='ne', padx=10, pady=10)
    
    # Główna ramka z zawartością
    content_frame = tk.Frame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    normal_label = tk.Label(content_frame, text="Bilety Normalne", font=("Arial", 14, "bold"))
    normal_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    reduced_label = tk.Label(content_frame, text="Bilety Ulgowe", font=("Arial", 14, "bold"))
    reduced_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    hours_label = tk.Label(content_frame, text="Godziny Atrakcji", font=("Arial", 14, "bold"))
    hours_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
    
    normal_text = scrolledtext.ScrolledText(content_frame, width=50, height=40, state="disabled")
    normal_text.grid(row=1, column=0, padx=10, pady=5)
    reduced_text = scrolledtext.ScrolledText(content_frame, width=50, height=40, state="disabled")
    reduced_text.grid(row=1, column=1, padx=10, pady=5)
    
    hours_frame = tk.Frame(content_frame)
    hours_frame.grid(row=1, column=2, padx=10, pady=5, sticky="n")
    
    approve_button = tk.Button(root, text="Zatwierdź Bilet", command=approve_ticket)
    approve_button.pack(pady=10)
        # Inicjalizacja dark mode
    
    display_all_info(normal_text, reduced_text, hours_frame, newsafari_data, newpalace_data)
    display_all_hours(normal_text, reduced_text, hours_frame, dark_mode)  # Pass dark_mode
    if config['mode'] == "dark":
        dark_mode.is_dark = True
        dark_mode.apply_theme()
    root.mainloop()

if __name__ == "__main__":
    main()