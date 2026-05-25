import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

current_script_dir = Path(__file__).parent

# Function to generate random codes
def generate_random_code(liczba_liter_w_kodzie=6):
    listaznaków = [chr(i) for i in range(48, 58)]  # Digits 0-9
    for i in range(65, 91):  # Uppercase letters A-Z
        listaznaków.append(chr(i))
    for i in range(97, 123):  # Lowercase letters a-z
        listaznaków.append(chr(i))

    word = []
    for _ in range(liczba_liter_w_kodzie):
        word.append(listaznaków[np.random.randint(0, len(listaznaków) - 1)])
    return ''.join(word)

# Function to create the database and table
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            "Wejście na teren" TEXT,
            "Safari bizon" TEXT,
            "Pałac" TEXT,
            "Labirynt bukowy" TEXT,
            "Labirynt z kukurydzy" TEXT,
            "Muzeum cztery rodziny" TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to append generated codes to the database
def append_codes_to_db(db_name, num_codes=1):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Generate codes and insert into the database
    if num_codes == 0:
        codes = [generate_random_code() for _ in range(6)]  # Generate 6 random codes
        cursor.execute('''
            INSERT INTO codes (
                "Wejście na teren", "Safari bizon", "Pałac", 
                "Labirynt bukowy", "Labirynt z kukurydzy", "Muzeum cztery rodziny"
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', [None,None,None,None,None,None])
    else:
        for _ in range(num_codes):
            codes = [generate_random_code() for _ in range(6)]  # Generate 6 random codes
            cursor.execute('''
                INSERT INTO codes (
                    "Wejście na teren", "Safari bizon", "Pałac", 
                    "Labirynt bukowy", "Labirynt z kukurydzy", "Muzeum cztery rodziny"
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', codes)
    
    conn.commit()
    conn.close()

# Main function
def main():
    db_name = current_script_dir / "random_codes.db"
    create_database(db_name)  # Create the database and table
    db_name2 = current_script_dir / "random_used_codes.db"
    create_database(db_name2)  # Create the database and table
    # Append 10 sets of random codes to the database
    append_codes_to_db(db_name, num_codes=10)
    append_codes_to_db(db_name2, num_codes=0)
    print("Random codes have been generated and appended to the database.")

if __name__ == "__main__":
    main()