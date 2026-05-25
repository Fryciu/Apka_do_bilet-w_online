import tkinter as tk
from tkinter import ttk, messagebox, font
import keyboard
from pathlib import Path
import time
import threading
import subprocess
import sys
import json
import os
from datetime import date


#TODO naprawić bug związany ze złym zapisywaniem dni i znikaniem okienek 9/10 

current_script_dir = Path(__file__).parent
sciezka_zapisu_klucza = current_script_dir / "Klucz.txt"
sciezka_zapisu = current_script_dir / "Przykład_zakryptowanego_biletu.txt"
db_name = current_script_dir / "random_codes.db"  # Ścieżka do bazy danych
sciezka_apki_do_odczytywania_biletow = current_script_dir / "testowa_apka_do_odczytania_zakryptowanych_biletów.py"
schedule_address = current_script_dir / 'data.json'
config_file = current_script_dir / "config.json"

def callablepopen(qrcode):
    subprocess.Popen([sys.executable, 
                      qrcode,sciezka_apki_do_odczytywania_biletow, 
                    app.safari_data, app.palace_data, app.mode])


class SafariApp:
    def __init__(self, root):        
        self.mode = "light"
        self.check_date_and_cleanup()  # Add this line after initializing paths
        self.root = root
        self.root.title("Safari i Pałac - Zarządzanie Wejściami")
        self.qr_mode = False
        self.palace_frames = []
        self.safari_frames = []
        self.safari_data = {}  # Change to dictionary
        self.palace_data = {}  # Change to dictionary
    
        self.qr_code = ""  # Zmienna do przechowywania kodu QR
    
        # Create a Canvas and Scrollbar
        self.canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        # Configure the Canvas to scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
    
        # Place the Canvas and Scrollbar in the window
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
    
        # Configure the root grid to allow resizing
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
    
        # Ustawienia
        self.settings_frame = ttk.LabelFrame(self.scrollable_frame, text="Ustawienia")
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
        self.mode_button = ttk.Button(self.settings_frame, text="Zmień tryb", command=self.toggle_mode)
        self.mode_button.grid(row=0, column=0, padx=5, pady=5)
    
        self.font_size_label = ttk.Label(self.settings_frame, text="Rozmiar aplikacji:")
        self.font_size_label.grid(row=1, column=0, padx=5, pady=5)
    
        self.qr_button = ttk.Button(self.settings_frame, text="Tryb czytania kodu\nQR wyłączony", command=self.toggle_qr_mode)
        self.qr_button.grid(row=0, column=1, padx=5, pady=5)
    
        self.font_size = ttk.Combobox(self.settings_frame, values=["8", "10", "12", "14", "16", "18", "20", "22", "24"], width=5)
        self.font_size.grid(row=1, column=1, padx=5, pady=5)
        self.font_size.current(2)  # Domyślny rozmiar czcionki
        self.font_size.bind("<<ComboboxSelected>>", self.change_font_size)
    
        # Zmienne w ustawieniach
        self.var1_label = ttk.Label(self.settings_frame, text="Maksymalna liczba osób, która zmieści się na większym wozie od Safari:")
        self.var1_label.grid(row=3, column=0, padx=5, pady=5)
    
        self.var1_entry = ttk.Entry(self.settings_frame, width=5)
        self.var1_entry.grid(row=3, column=1, padx=5, pady=5)
        self.var1_entry.insert(0, "40")
    
        self.var2_label = ttk.Label(self.settings_frame, text="Maksymalna liczba osób, która zmieści się na mniejszym wozie od safari:")
        self.var2_label.grid(row=4, column=0, padx=5, pady=5)
    
        self.var2_entry = ttk.Entry(self.settings_frame, width=5)
        self.var2_entry.grid(row=4, column=1, padx=5, pady=5)
        self.var2_entry.insert(0, "42")
    
        self.var2_label = ttk.Label(self.settings_frame, text="Maksymalna liczba osób na jednej wycieczce po pałacu:")
        self.var2_label.grid(row=5, column=0, padx=5, pady=5)
    
        self.var_palac_entry = ttk.Entry(self.settings_frame, width=5)
        self.var_palac_entry.grid(row=5, column=1, padx=5, pady=5)
        self.var_palac_entry.insert(0, "40")
    
        self.update_button = ttk.Button(self.settings_frame, text="Aktualizuj wartości ustawień", command=self.update_settings_values)
        self.update_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self.update_button = ttk.Button(self.settings_frame, text="Aktualizuj wartości terminów", command=self.update_term_values)
        self.update_button.grid(row=6, column=1, columnspan=2, padx=5, pady=5)
        style = ttk.Style()
        style.theme_use('clam')  # Use a theme that supports customization
        # Add the first terms
        self.add_palace_term(deleteable="no")  # Add the first Palace term
        self.add_safari_term(deleteable="no")  # Add the first Safari term
        self.load_config()  # Load config at startup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def check_date_and_cleanup(self):
        """Check date and reset data if date changed"""
        today = date.today().isoformat()

        try:
            # Load or create config
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {'day': today, 'mode': 'light'}

            # Check if date changed
            if config.get('day') != today:
                print(f"Date changed from {config.get('day')} to {today}")

                # Reset data structures
                self.safari_data = {}
                self.palace_data = {}

                # Update config with new date
                config['day'] = today
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=4)

                print("Reset data for new day")

        except Exception as e:
            print(f"Error in date check: {e}")
    def on_close(self):
        """Handle application exit"""
        self.save_config()  # Save current configuration
        self.root.destroy()  # Close the application
    
    def load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "mode": "dark",
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.mode = config.get("mode", default_config["mode"])
                    # Apply loaded mode immediately
                    print(self.mode)
                    if self.mode == "dark":
                        self.mode = "light"
                        self.toggle_mode()  # Will switch from default light to dark
                    print("Dziwne")
            else:
                self.mode = default_config["mode"]
                self.save_config()  # Create default config file
                print("AHa")
        except Exception as e:
            print(f"Error loading config: {e}")
            self.mode = default_config["mode"]
            
    def save_config(self):
        """Save current configuration to file"""
        config = {
            "mode": self.mode,
            "day": date.today().isoformat()  # Format: YYYY-MM-DD
        }
        print(config)
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    
    def on_save_button_click(self, nazwa):
        if nazwa == "Safari":
            time = self.safari_time.get()
            count = self.safari_count.get()
            max_count = self.safari_max.get()
            button = self.save_safari_button
        elif nazwa == "Pałac":
            time = self.palace_time.get()
            count = self.palace_count.get()
            max_count = self.palace_max.get()
            button = self.save_palace_button

        Dane_z_wycieczki = save(time, count, max_count, nazwa)
        if Dane_z_wycieczki:
            # Store or update the data in the appropriate dictionary
            if nazwa == "Safari":
                self.safari_data[Dane_z_wycieczki["Godzina"]] = Dane_z_wycieczki
            elif nazwa == "Pałac":
                self.palace_data[Dane_z_wycieczki["Godzina"]] = Dane_z_wycieczki

            # Update the button text
            button.config(text="Zapisane")
            self.save_schedule()
            self.print_saved_terms()

    def reset_button_text(self, nazwa):
        if nazwa == "Safari":
            self.save_safari_button.config(text="Zapisz")
        elif nazwa == "Pałac":
            self.save_palace_button.config(text="Zapisz")

    def change_font_size(self, event):
        new_size = int(self.font_size.get())
        self.apply_font_size(new_size)

    def apply_font_size(self, size):
        custom_font = font.Font(size=size)
        for widget in self.root.winfo_children():
            self.apply_font_recursive(widget, custom_font)

    def apply_font_recursive(self, widget, custom_font):
        try:
            widget.configure(font=custom_font)
        except tk.TclError:
            pass  # Ignoruj widgety, które nie mają opcji 'font'

        for child in widget.winfo_children():
            self.apply_font_recursive(child, custom_font) 

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")   

    
    def load_data(self, data_address):
        """Load schedule data or return empty structure if file doesn't exist or is invalid"""
        default_data = [{}, {}]  # [safari_data, palace_data]

        try:
            if data_address.exists() and data_address.stat().st_size > 0:
                with open(data_address, 'r') as file:
                    data = json.load(file)
                    # Validate the structure
                    if isinstance(data, list) and len(data) >= 2:
                        return data
        except Exception as e:
            print(f"Error loading schedule data: {e}")

        # Return default if file doesn't exist or is invalid
        return default_data
    
    
    
    def save_schedule(self):
        """Save current data to schedule file"""
        try:
            # Ensure the directory exists
            schedule_address.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data to save
            data_to_save = [
                self.safari_data,
                self.palace_data
            ]

            # Save with atomic write pattern
            temp_file = schedule_address.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data_to_save, f, indent=4)

            # Replace old file only if write was successful
            temp_file.replace(schedule_address)

        except Exception as e:
            print(f"Error saving schedule: {e}")
            messagebox.showerror("Błąd", f"Nie udało się zapisać danych: {e}")
                

    def toggle_mode(self):
        if self.mode == "light":
            # Change to dark mode
            self.mode = "dark"
            style = ttk.Style()
            style.theme_use('clam')  # Use a theme that supports customization

            # Configure dark colors for various widget elements
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabelframe', background='#2d2d2d', foreground='white')
            style.configure('TLabelframe.Label', background='#2d2d2d', foreground='white')
            style.configure('TLabel', background='#2d2d2d', foreground='white')
            style.configure('TButton', background='#444444', foreground='white')
            style.configure('TEntry', fieldbackground='#444444', foreground='white')
            style.configure('TCombobox', fieldbackground='#444444', foreground='white')
            style.configure('TSpinbox', fieldbackground='#444444', foreground='white')
            style.configure('Vertical.TScrollbar', background='#444444', troughcolor='#2d2d2d')

            # Configure the Canvas for dark mode
            self.canvas.configure(background='#2d2d2d')

            # Change button text
            self.mode_button.configure(text="Tryb jasny")

            # Apply dark mode to all existing safari and palace frames
            self.apply_theme_to_frames()

        else:
            # Change to light mode
            self.mode = "light"
            style = ttk.Style()
            style.theme_use('clam')  # Reset to a standard theme

            # Configure light colors
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TLabelframe', background='#f0f0f0', foreground='black')
            style.configure('TLabelframe.Label', background='#f0f0f0', foreground='black')
            style.configure('TLabel', background='#f0f0f0', foreground='black')
            style.configure('TButton', background='#e0e0e0', foreground='black')
            style.configure('TEntry', fieldbackground='white', foreground='black')
            style.configure('TCombobox', fieldbackground='white', foreground='black')
            style.configure('TSpinbox', fieldbackground='white', foreground='black')
            style.configure('Vertical.TScrollbar', background='#e0e0e0', troughcolor='#f0f0f0')

            # Configure the Canvas for light mode
            self.canvas.configure(background='#f0f0f0')

            # Change button text
            self.mode_button.configure(text="Tryb ciemny")

            # Apply light mode to all existing safari and palace frames
            self.apply_theme_to_frames()

    def apply_theme_to_frames(self):
        """Apply the current theme to all safari and palace frames"""
        # Loop through all palace frames
        for frame in self.palace_frames:
            self.apply_theme_to_widgets(frame)

        # Loop through all safari frames
        for frame in self.safari_frames:
            self.apply_theme_to_widgets(frame)

        # Apply to settings frame as well
        self.apply_theme_to_widgets(self.settings_frame)

    def apply_theme_to_widgets(self, parent_widget):
        """Apply the current theme to all widgets in a parent widget"""
        for child in parent_widget.winfo_children():
            if isinstance(child, ttk.Spinbox):
                self.apply_spinbox_theme(child)
            elif isinstance(child, ttk.Combobox):
                self.apply_combobox_theme(child)
            elif isinstance(child, ttk.LabelFrame):
                child.configure(style='TLabelframe')
                self.apply_theme_to_widgets(child)
            elif isinstance(child, ttk.Label):
                child.configure(style='TLabel')
            elif isinstance(child, ttk.Button):
                child.configure(style='TButton')
            elif isinstance(child, ttk.Entry):
                child.configure(style='TEntry')
            elif isinstance(child, tk.Frame) or isinstance(child, ttk.Frame):
                self.apply_theme_to_widgets(child)

    def apply_spinbox_theme(self, spinbox):
        """Apply the current theme to a ttk Spinbox"""
        if self.mode == "dark":
            spinbox.configure(style='TSpinbox')
            # Some spinboxes might need special handling
            try:
                spinbox.configure(fieldbackground='#444444', foreground='white')
            except:
                pass
        else:
            spinbox.configure(style='TSpinbox')
            try:
                spinbox.configure(fieldbackground='white', foreground='black')
            except:
                pass


    def apply_combobox_theme(self, combobox):
        """Apply the current theme to a ttk Combobox"""
        style = ttk.Style()
        
        # Save current value
        current_value = combobox.get()
        
        if self.mode == "dark":
            # Configure what we can directly on the widget
            try:
                combobox.configure(foreground='white')
            except:
                pass
                
            # Use the style system for the rest
            style.configure('TCombobox', 
                fieldbackground='#444444',
                background='#444444',
                foreground='white'
            )
            
            style.map('TCombobox',
                fieldbackground=[('readonly', '#444444')],
                selectbackground=[('readonly', '#666666')],
                background=[('readonly', '#444444')],
                foreground=[('readonly', 'white')]
            )
            
            # Apply arrow color using Tcl/Tk directly
            try:
                style.configure('TCombobox', arrowcolor='white')
            except:
                pass
        else:
            # Configure what we can directly on the widget
            try:
                combobox.configure(foreground='black')
            except:
                pass
                
            # Use the style system for the rest
            style.configure('TCombobox', 
                fieldbackground='white',
                background='white',
                foreground='black'
            )
            
            style.map('TCombobox',
                fieldbackground=[('readonly', 'white')],
                selectbackground=[('readonly', '#0078d7')],
                background=[('readonly', 'white')],
                foreground=[('readonly', 'black')]
            )
            
            # Apply arrow color using Tcl/Tk directly
            try:
                style.configure('TCombobox', arrowcolor='black')
            except:
                pass
            
        # Try to force a visual refresh
        values = combobox.cget('values')
        combobox.configure(values=values)
        combobox.set(current_value)
   
    
    def print_saved_terms(self):
        """Print all saved terms for Safari and Pałac."""
        print("Safari Data:", self.safari_data)
        print("Pałac Data:", self.palace_data)
        

    def change_font_size(self, event):
        new_size = int(self.font_size.get())
        custom_font = font.Font(size=new_size)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Label, ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Combobox)):
                        child.configure(font=custom_font)
    
    def update_settings_values(self):
        try:
            var1 = int(self.var1_entry.get())
            var2 = int(self.var2_entry.get())
            var3 = var1 + var2
            self.safari_max['values'] = [var1, var2, var3]
            self.safari_max.current(0)
            var4 = int(self.var_palac_entry.get())
            self.palace_max['values'] = [i*var4 for i in range(1,6)]
            self.apply_font_size(int(self.font_size.get()))
            self.update_palace_max_values()
            self.update_safari_max_values()

        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne liczby całkowite.")

    def process_qr_code(self):
       """
       Przechwytuje kod QR i sprawdza jego poprawność.
       """
       if self.qr_mode:
           def read_qr():
               while self.qr_mode:
                   event = keyboard.read_event()
                   if event.event_type == keyboard.KEY_DOWN:
                       if event.name == "enter":
                           self.root.after(0, callablepopen(self.qr_code))  # Obsłuż kod na głównym wątku Tkintera
                       else:
                           self.qr_code += event.name  # Dodaj znak do kodu QR

           threading.Thread(target=read_qr, daemon=True).start()  # Uruchom w tle

    def toggle_qr_mode(self):
        """
        Włącza lub wyłącza tryb czytania kodów QR.
        """
        self.qr_mode = not self.qr_mode
        status = "włączony" if self.qr_mode else "wyłączony"
        self.qr_button.config(text=f"Tryb czytania kodu\nQR {status}")
        time.sleep(0.01)
        if self.qr_mode:
            self.process_qr_code()  # Rozpocznij odczytywanie kodów QR
        else:
            self.qr_code = ""  # Wyczyść kod QR po wyłączeniu trybu
  
    def update_palace_max_values(self):
        var4 = int(self.var_palac_entry.get())
        self.palace_max['values'] = [i * var4 for i in range(1, 6)]
        for frame in self.palace_frames:
            palace_max = frame.winfo_children()[5]  # Zakładając, że combobox jest 6. elementem
            palace_max['values'] = [i * var4 for i in range(1, 6)]

    def update_safari_max_values(self):
        var1 = int(self.var1_entry.get())
        var2 = int(self.var2_entry.get())
        var3 = var1 + var2
        self.safari_max['values'] = [var1, var2, var3]
        for frame in self.safari_frames:
            safari_max = frame.winfo_children()[5]  # Zakładając, że combobox jest 6. elementem
            safari_max['values'] = [var1, var2, var3]

    def update_settings_values(self):
        try:
            var1 = int(self.var1_entry.get())
            var2 = int(self.var2_entry.get())
            var3 = var1 + var2
            self.safari_max['values'] = [var1, var2, var3]
            self.safari_max.current(0)
            var4 = int(self.var_palac_entry.get())
            self.palace_max['values'] = [i * var4 for i in range(1, 6)]
            self.update_palace_max_values()  # Aktualizacja wartości w nowych oknach
            self.update_safari_max_values()  # Aktualizacja wartości w nowych oknach
            self.apply_font_size(int(self.font_size.get()))

        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne liczby całkowite.")
    
    def str_key_2_int(self, data):
        new_data = []
        for el in data:
            data_int_keys = {}
            for key_str, value in el.items():
                try:
                    key_int = int(key_str)
                    data_int_keys[key_int] = value
                except ValueError:
                    # Handle cases where the key might not be a valid integer string
                    data_int_keys[key_str] = value
            new_data.append(data_int_keys)
        return new_data
    
    
    def update_term_values(self):
        
            
        
        with open(schedule_address, 'r') as file:
            data = json.load(file)
        data = self.str_key_2_int(data=data)

        # Clear existing frames
        for el in self.safari_frames[:]:  # Use a copy of the list to avoid modification issues
            self.delete_safari_term(el)
        for el in self.palace_frames[:]:
            self.delete_palace_term(el)

        # Process Safari terms (first dictionary in the list)
        safari_terms = data[0]
        first_safari = True
        for time_minutes, term_data in safari_terms.items():
            if first_safari:
                self.add_safari_term(
                    deleteable="no",
                    premaxvalue=term_data["Maksymalna liczba os\u00f3b"],
                    prevalue=term_data["Liczba os\u00f3b"],
                    prehour=term_data["Godzina"]
                )
                first_safari = False
            else:
                self.add_safari_term(
                    premaxvalue=term_data["Maksymalna liczba os\u00f3b"],
                    prevalue=term_data["Liczba os\u00f3b"],
                    prehour=term_data["Godzina"]
                )

        # Process Palace terms (second dictionary in the list)
        palace_terms = data[1]
        first_palace = True
        for time_minutes, term_data in palace_terms.items():
            if first_palace:
                self.add_palace_term(
                    deleteable="no",
                    premaxvalue=term_data["Maksymalna liczba os\u00f3b"],
                    prevalue=term_data["Liczba os\u00f3b"],
                    prehour=term_data["Godzina"]
                )
                first_palace = False
            else:
                self.add_palace_term(
                    premaxvalue=term_data["Maksymalna liczba os\u00f3b"],
                    prevalue=term_data["Liczba os\u00f3b"],
                    prehour=term_data["Godzina"]
                )
        
        
            
        
    
    def add_safari_term(self, max_count=None, 
                        deleteable = "yes", premaxvalue = 0, 
                        prevalue = 0, prehour = 0):
        new_safari_frame = ttk.LabelFrame(self.scrollable_frame, text="Wejście na Safari")
        new_safari_frame.grid(row=len(self.safari_frames), column=3, padx=10, pady=10, sticky="nsew")

        safari_time_label = ttk.Label(new_safari_frame, text="Godzina wejścia (np. 14:00):")
        safari_time_label.grid(row=0, column=0, padx=5, pady=5)

        safari_time = ttk.Entry(new_safari_frame, width=10)
        safari_time.grid(row=0, column=1, padx=5, pady=5)
        if prehour != 0:
            safari_time.insert(0, string=str(format_minutes_to_time(prehour)))

        safari_count_label = ttk.Label(new_safari_frame, text="Liczba osób:")
        safari_count_label.grid(row=1, column=0, padx=5, pady=5)

        safari_count = ttk.Spinbox(new_safari_frame, from_=0, to=1000, width=5)
        safari_count.grid(row=1, column=1, padx=5, pady=5)
        safari_count.delete(0, tk.END)  # Clear default value
        safari_count.insert(0, str(prevalue))  # Set default value to 0

        safari_max_label = ttk.Label(new_safari_frame, text="Maksymalna liczba osób:")
        safari_max_label.grid(row=2, column=0, padx=5, pady=5)

        safari_max = ttk.Combobox(new_safari_frame, values=[40, 42, 82], width=5) #TODO zmień values tak, aby mogły być one zapisywane w jakimś pliku config. (Raczej nie potrzebne ze względu na rzadką wymianę pojazdów)
        safari_max.grid(row=2, column=1, padx=5, pady=5)
        if premaxvalue:
            safari_max.set(premaxvalue)  # Set the max_count from the parent term
        else:
            if max_count:
                safari_max.set(max_count)  # Set the max_count from the parent term
            else:
                safari_max.current(0)  # Default to the first value

        button_frame_safari = ttk.Frame(new_safari_frame)
        button_frame_safari.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        if deleteable == "yes":
            delete_safari_button = ttk.Button(button_frame_safari, text="Usuń termin")
            delete_safari_button["command"] = lambda frame=new_safari_frame: self.delete_safari_term(frame)
            delete_safari_button.pack(side="left", padx=5)

        add_safari_button = ttk.Button(button_frame_safari, text="Dodaj termin")
        add_safari_button["command"] = lambda: self.add_safari_term(max_count=safari_max.get())
        add_safari_button.pack(side="left", padx=5)

        save_safari_button = ttk.Button(button_frame_safari, text="Zapisz")
        save_safari_button["command"] = lambda: self.on_save_button_click_dynamic(
            safari_time, safari_count, safari_max, save_safari_button, "Safari"
        )
        save_safari_button.pack(side="left", padx=5)

        # Bind events to reset button text
        safari_time.bind("<KeyRelease>", lambda e: self.reset_button_text_dynamic(save_safari_button))
        safari_count.bind("<KeyRelease>", lambda e: self.reset_button_text_dynamic(save_safari_button))
        safari_max.bind("<<ComboboxSelected>>", lambda e: self.reset_button_text_dynamic(save_safari_button))

        # Add the new frame to the list
        self.safari_frames.append(new_safari_frame)
        self.apply_font_size(int(self.font_size.get()))
    
    def reset_button_text_dynamic(self, button):
        button.config(text="Zapisz")

    def add_palace_term(self, max_count=None, deleteable = "yes", premaxvalue = 0, 
                        prevalue = 0, prehour = 0):
        new_palace_frame = ttk.LabelFrame(self.scrollable_frame, text="Wejście na Pałac")
        new_palace_frame.grid(row=len(self.palace_frames), column=2, padx=10, pady=10, sticky="nsew")

        palace_time_label = ttk.Label(new_palace_frame, text="Godzina wejścia (np. 14:00):")
        palace_time_label.grid(row=0, column=0, padx=5, pady=5)

        palace_time = ttk.Entry(new_palace_frame, width=10)
        palace_time.grid(row=0, column=1, padx=5, pady=5)
        
        if prehour != 0:
            palace_time.insert(0, string=str(format_minutes_to_time(prehour)))

        palace_count_label = ttk.Label(new_palace_frame, text="Liczba osób:")
        palace_count_label.grid(row=1, column=0, padx=5, pady=5)

        palace_count = ttk.Spinbox(new_palace_frame, from_=0, to=1000, increment=1, width=5)
        palace_count.grid(row=1, column=1, padx=5, pady=5)
        palace_count.delete(0, tk.END)  # Clear default value
        palace_count.insert(0, string=str(prevalue))  # Set default value to 0

        palace_max_label = ttk.Label(new_palace_frame, text="Maksymalna liczba osób:")
        palace_max_label.grid(row=2, column=0, padx=5, pady=5)

        palace_max = ttk.Combobox(new_palace_frame, values=[40, 80, 120, 160, 200], width=5)
        palace_max.grid(row=2, column=1, padx=5, pady=5)
        if premaxvalue:
            palace_max.set(premaxvalue)  # Set the max_count from the parent term
        else:
            if max_count:
                palace_max.set(max_count)  # Set the max_count from the parent term
            else:
                palace_max.current(0)  # Default to the first value

        button_frame_palace = ttk.Frame(new_palace_frame)
        button_frame_palace.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        if deleteable == "yes":
            delete_palace_button = ttk.Button(button_frame_palace, text="Usuń termin")
            delete_palace_button["command"] = lambda frame=new_palace_frame: self.delete_palace_term(frame)
            delete_palace_button.pack(side="left", padx=5)

        add_palace_button = ttk.Button(button_frame_palace, text="Dodaj termin")
        add_palace_button["command"] = lambda: self.add_palace_term(max_count=palace_max.get())
        add_palace_button.pack(side="left", padx=5)

        save_palace_button = ttk.Button(button_frame_palace, text="Zapisz")
        save_palace_button["command"] = lambda: self.on_save_button_click_dynamic(
            palace_time, palace_count, palace_max, save_palace_button, "Pałac"
        )
        save_palace_button.pack(side="left", padx=5)

        # Bind events to reset button text
        palace_time.bind("<KeyRelease>", lambda e: self.reset_button_text_dynamic(save_palace_button))
        palace_count.bind("<KeyRelease>", lambda e: self.reset_button_text_dynamic(save_palace_button))
        palace_max.bind("<<ComboboxSelected>>", lambda e: self.reset_button_text_dynamic(save_palace_button))

        # Add the new frame to the list
        self.palace_frames.append(new_palace_frame)
        self.apply_font_size(int(self.font_size.get()))

    def delete_palace_term(self, frame=None):
        if frame is None:
            # Usuń pierwszy termin
            if self.palace_frames:
                frame = self.palace_frames[0]  # Get the first frame
                time_entry = frame.winfo_children()[1]  # Assuming the time entry is the second widget
                time = time_entry.get()
                try:
                    time_minutes = time_to_minutes(time)
                    if time_minutes in self.palace_data:
                        del self.palace_data[time_minutes]  # Remove from dictionary
                except ValueError:
                    pass
                frame.destroy()
                self.palace_frames.pop(0)  # Remove the frame from the list
                print(self.palace_frames)
        else:
        
            # Usuń konkretny termin
            if frame in self.palace_frames:  # Check if the frame is in the list
                time_entry = frame.winfo_children()[1]  # Assuming the time entry is the second widget
                time = time_entry.get()
                try:
                    time_minutes = time_to_minutes(time)
                    if time_minutes in self.palace_data:
                        del self.palace_data[time_minutes]  # Remove from dictionary
                except ValueError:
                    pass
                frame.destroy()
                self.palace_frames.remove(frame)  # Remove the frame from the list
                print(self.palace_frames) 

        # Przesunięcie pozostałych ramek w górę
        for i, palace_frame in enumerate(self.palace_frames):
            palace_frame.grid(row=i, column=2, padx=10, pady=10, sticky="nsew") 

    def delete_safari_term(self, frame=None):
        if frame is None:
            # Delete the first term
            if self.safari_frames:
                frame = self.safari_frames.pop(0)
                time_entry = frame.winfo_children()[1]  # Assuming the time entry is the second widget
                time = time_entry.get()
                try:
                    time_minutes = time_to_minutes(time)
                    if time_minutes in self.safari_data:
                        del self.safari_data[time_minutes]  # Remove from dictionary
                except ValueError:
                    pass
                frame.destroy()
        else:
            # Delete specific term
            time_entry = frame.winfo_children()[1]  # Assuming the time entry is the second widget
            time = time_entry.get()
            try:
                time_minutes = time_to_minutes(time)
                if time_minutes in self.safari_data:
                    del self.safari_data[time_minutes]  # Remove from dictionary
            except ValueError:
                pass
            if frame in self.safari_frames:  # Check if frame is still in list
                self.safari_frames.remove(frame)
            frame.destroy()

        # Move remaining frames up
        for i, safari_frame in enumerate(self.safari_frames):
            safari_frame.grid(row=i, column=3, padx=10, pady=10, sticky="nsew")
            
    def on_save_button_click_dynamic(self, time_entry, count_entry, max_entry, button, nazwa):
        time = time_entry.get()
        count = count_entry.get()
        max_count = max_entry.get()

        Dane_z_wycieczki = save(time, count, max_count, nazwa)
        if Dane_z_wycieczki:
            # Store or update the data in the appropriate dictionary
            if nazwa == "Safari":
                self.safari_data[Dane_z_wycieczki["Godzina"]] = Dane_z_wycieczki
            elif nazwa == "Pałac":
                self.palace_data[Dane_z_wycieczki["Godzina"]] = Dane_z_wycieczki

            # Update the button text
            button.config(text="Zapisane")
            self.save_schedule()
            self.print_saved_terms()

def time_to_minutes(time_str):
    """Convert a time string (HH:MM) to minutes since midnight."""
    try:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    except (ValueError, AttributeError):
        raise ValueError("Nieprawidłowy format godziny. Użyj formatu HH:MM.")


def save(time, count, max_count, nazwa="Safari"):
    print(time)  # Print the time for debugging purposes
    try:
        # Validate the time format
        if ':' not in time or len(time) < 4 or len(time) > 5:
            raise ValueError("Nieprawidłowy format godziny. Użyj formatu HH:MM.")

        # Split the time into hours and minutes
        hours, minutes = time.split(':')

        # Check if hours and minutes are digits and within valid ranges
        if not hours.isdigit() or not minutes.isdigit():
            raise ValueError("Nieprawidłowy format godziny. Godziny i minuty muszą być liczbami.")

        hours = int(hours)
        minutes = int(minutes)

        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ValueError("Nieprawidłowa godzina. Godziny muszą być między 00 a 23, a minuty między 00 a 59.")

        # Convert count and max_count to integers
        count = int(count)
        max_count = int(max_count)

        # Check if the number of people exceeds the maximum capacity
        if count > max_count:
            raise ValueError("Liczba osób przekracza maksymalną liczbę.")

        # Convert time to minutes since midnight
        minuty_w_dniu = time_to_minutes(time)

        # Check if the time is already in use
        if nazwa == "Safari":
            if minuty_w_dniu in app.safari_data:
                app.safari_data.pop(minuty_w_dniu)        
        elif nazwa == "Pałac":
            if minuty_w_dniu in app.palace_data:
                app.palace_data.pop(minuty_w_dniu)

        # Create the data dictionary
        Dane_z_wycieczki = {
            "Godzina": minuty_w_dniu,
            "Liczba osób": count,
            "Maksymalna liczba osób": max_count
        }

        # Print the details if everything is valid
        print(f"{nazwa}: Godzina {time}, Liczba osób: {count}, Maksymalnie: {max_count}")
        print("To są dane?",Dane_z_wycieczki)
        return Dane_z_wycieczki  # Return the data dictionary

    except ValueError as e:
        # Show an error message if any validation fails
        messagebox.showerror("Błąd", str(e))
        return None  # Indicate failure
def format_minutes_to_time(minutes):
    """Przelicza minuty od północy na format HH:MM."""
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02d}:{minutes:02d}"

if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    style = ttk.Style()
    style.configure("Dark.TLabelframe", background="gray20", foreground="white")
    style.configure("Dark.TButton", background="gray20", foreground="white")
    app = SafariApp(root)
    app.load_config()  # Load config at startup
    root.mainloop()