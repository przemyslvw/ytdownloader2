import tkinter as tk
from tkinter import messagebox
from yt_dlp import YoutubeDL

def fetch_video_length(url_entry, start_entry, end_entry, output_entry):
    url = url_entry.get()
    if not url:
        messagebox.showerror("Błąd", "Wklej link do filmu")
        return

    try:
        # Pobieranie informacji o wideo przy użyciu yt-dlp
        ydl_opts = {'format': 'best', 'quiet': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_duration = int(info['duration'])
            video_title = info['title']

        # Ustawienie maksymalnych wartości dla pól start i end
        start_entry.delete(0, tk.END)
        start_entry.insert(0, "0")
        end_entry.delete(0, tk.END)
        end_entry.insert(0, str(video_duration))

        # Ustawienie tytułu filmu jako domyślnej nazwy pliku, bez znaków specjalnych
        output_entry.delete(0, tk.END)
        sanitized_title = "".join(char if char.isalnum() else "_" for char in video_title)
        output_entry.insert(0, sanitized_title)

        messagebox.showinfo("Długość filmu", f"Długość filmu: {video_duration} sekund\nNazwa pliku: {sanitized_title}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się pobrać informacji o filmie:\n{e}")
