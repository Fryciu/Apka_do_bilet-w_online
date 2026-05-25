# first_app.py (sending data)
import tkinter as tk
import subprocess
import sys
import os
from pathlib import Path

current_script_dir = Path(__file__).parent
sciezka_apki_do_odczytywania_biletow = current_script_dir / "testowa_apka_do_odczytania_zakryptowanych_biletów.py"

def send_data():
    
    data = entry.get()
    subprocess.Popen([sys.executable, sciezka_apki_do_odczytywania_biletow, data])

root = tk.Tk()
root.title("First App (Sender)")

label = tk.Label(root, text="Enter data to send:")
label.pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack(pady=10)

send_button = tk.Button(root, text="Send Data", command=send_data)
send_button.pack(pady=10)

root.mainloop()
