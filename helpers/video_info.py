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
    Pobiera metadane filmu za pomocą yt-dlp i zwraca jako dict.
    """
    try:
        yt_dlp_command = [
            "yt-dlp",
            "--no-warnings",
            "--ignore-errors",
            "--geo-bypass",
            "--no-check-certificate",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--referer", "https://www.youtube.com/",
            "--dump-json",
            url
        ]
        
        result = subprocess.run(
            yt_dlp_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        if not result.stdout.strip():
            raise Exception("Pusta odpowiedź z serwera")
            
        try:
            video_info = json.loads(result.stdout)
            if not isinstance(video_info, dict) or 'title' not in video_info:
                raise Exception("Nieprawidłowa struktura odpowiedzi z serwera")
            return video_info
            
        except json.JSONDecodeError as e:
            error_msg = "Nie można sparsować odpowiedzi JSON"
            if result.stderr:
                error_msg += f"\nBłąd: {result.stderr}"
            if result.stdout:
                error_msg += f"\nOdpowiedź: {result.stdout[:500]}"
            raise Exception(error_msg)
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Nieznany błąd podczas pobierania informacji o filmie"
        if "HTTP Error 429" in error_msg:
            error_msg = "Zbyt wiele żądań. Proszę spróbować ponownie później."
        elif "This video is not available" in error_msg:
            error_msg = "Film jest niedostępny lub został usunięty."
        raise Exception(f"Błąd yt-dlp: {error_msg}")
        
    except Exception as e:
        raise Exception(f"Wystąpił błąd: {str(e)}")


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
