from __future__ import annotations  # Must be at the top of the file
import json
from datetime import datetime, timezone
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext
from cryptography.fernet import Fernet
import sqlite3
#import subprocess
import sys
from datetime import datetime#, timedelta
import pandas as pd
#import heapq
import greenlet
from typing import Any


current_script_dir = Path(__file__).parent
sciezka_zapisu_klucza = current_script_dir / "Klucz.txt"
db_name = current_script_dir / "random_codes.db"  # Ścieżka do bazy danych

BUK_DURATION = 30
MUZEUM_DURATION = 30
SAFARI_DURATION = 30  # Safari trwa 1 godzinę
PALACE_DURATION = 60  # Pałac trwa 1 godzinę
KUKU_DURATION = 60  # Pałac trwa 1 godzinę


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
            print("tutaj jestem", self.start)
            return {
                "proposed_palace_beginning": self.start,
                "proposed_palace_end": self.end
            }
        else:
            raise ValueError("Invalid activity type")

class Backend_logic:
    def __init__(self) -> None:
        pass
    def get_ticket(self) -> int:
        try:
            if len(sys.argv) > 1:
                encrypted_data = sys.argv[1]
                print(encrypted_data)
                decrypted_data = cipher_suite.decrypt(encrypted_data)
                decrypted_json = json.loads(decrypted_data.decode())
                tickets = decrypted_json
                # Naprawa nazw biletów
                for ticket in tickets:
                    ticket['ticket_name'] = ticket['ticket_name'].replace("WejĹ›cie_na_teren", "Wejście na teren").replace("PaĹ‚ac", "Pałac")
                print("tickets",tickets)
            else:
                print("aha")
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Plik z biletami nie został znaleziony.")
            exit()
        except json.JSONDecodeError:
            messagebox.showerror("Błąd", "Nieprawidłowy format pliku JSON.")
            exit()
        except Exception:
            messagebox.showerror("Błąd", "Zły kod QR")
            exit()
    