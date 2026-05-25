from cryptography.fernet import Fernet
import json
from pathlib import Path

# Generate a key for encryption

current_script_dir = Path(__file__).parent
sciezka = current_script_dir / "Przykład_biletu_do_skryptowania.json"
sciezka_zapisu = current_script_dir / "Przykład_zakryptowanego_biletu.txt"
sciezka_zapisu_klucza = current_script_dir / "Klucz.txt"


key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Your JSON data
with open(sciezka, 'r') as file:
    ticket_data = json.load(file)

with open(sciezka_zapisu_klucza, 'wb') as file:
    file.write(key)

# Convert JSON to string
json_str = json.dumps(ticket_data)

# Encrypt the JSON string
encrypted_data = cipher_suite.encrypt(json_str.encode())

print("Encrypted Data:", encrypted_data)

with open(sciezka_zapisu, 'w') as file:
    file.write(encrypted_data.decode())