import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import re


def sanitize_filename(filename):
    """
    Usuwa znaki specjalne z tytułu do zapisu jako nazwa pliku.
    """
    return re.sub(r'[^\w\s.-]', '', filename)


def get_video_info(url):
    """
    Pobiera metadane filmu za pomocą yt-dlp.exe jako JSON.
    """
    try:
        result = subprocess.run(
            ["yt-dlp.exe", "-j", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Błąd", f"Błąd podczas pobierania metadanych:\n{e.output}")
        raise


def fetch_video_length(url_entry, start_entry, end_entry, output_entry):
    url = url_entry.get()
    if not url:
        messagebox.showerror("Błąd", "Wklej link do filmu")
        return

    try:
        info = get_video_info(url)
        video_duration = int(info['duration'])
        video_title = info['title']

        # Ustaw start = 0, end = długość filmu
        start_entry.delete(0, tk.END)
        start_entry.insert(0, "0")

        end_entry.delete(0, tk.END)
        end_entry.insert(0, str(video_duration))

        # Nazwa pliku domyślna = tytuł
        output_entry.delete(0, tk.END)
        sanitized_title = sanitize_filename(video_title)
        output_entry.insert(0, sanitized_title)

        messagebox.showinfo("Długość filmu", f"Długość filmu: {video_duration} sekund\nNazwa pliku: {sanitized_title}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się pobrać informacji o filmie:\n{e}")
