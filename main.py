import tkinter as tk
from tkinter import messagebox
from yt_dlp import YoutubeDL
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

# Funkcja sprawdzająca długość filmu i ustawiająca domyślną nazwę pliku
def fetch_video_length():
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

# Funkcja do pobierania i wycinania fragmentu
def download_and_extract():
    url = url_entry.get()
    start_time = int(start_entry.get())
    end_time = int(end_entry.get())
    output_filename = output_entry.get()
    selected_format = format_var.get()

    # Ustaw domyślną nazwę, jeśli pole jest puste
    if not output_filename:
        output_filename = "clip"
    output_filename += f".{selected_format}"  # Dodaj rozszerzenie do nazwy pliku

    try:
        # Pobieranie wideo przy użyciu yt-dlp
        ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'video.mp4'}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Przycięcie lub wyodrębnienie dźwięku w zależności od wybranego formatu
        if selected_format == "mp4":
            ffmpeg_extract_subclip("video.mp4", start_time, end_time, targetname=output_filename)
        elif selected_format == "mp3":
            # Przycinanie fragmentu i zapis jako mp3
            with VideoFileClip("video.mp4") as video:
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile(output_filename)
        
        messagebox.showinfo("Sukces", f"Wycinek zapisano jako {output_filename}")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

# Konfiguracja okna GUI
root = tk.Tk()
root.title("Pobieranie fragmentu YouTube")
root.geometry("400x350")

# Elementy interfejsu
tk.Label(root, text="Link do filmu:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

# Przycisk do pobrania długości filmu i ustawienia domyślnej nazwy pliku
check_button = tk.Button(root, text="Sprawdź film", command=fetch_video_length)
check_button.pack()

tk.Label(root, text="Czas początkowy (sekundy):").pack()
start_entry = tk.Entry(root, width=10)
start_entry.pack()

tk.Label(root, text="Czas końcowy (sekundy):").pack()
end_entry = tk.Entry(root, width=10)
end_entry.pack()

tk.Label(root, text="Nazwa zapisanego pliku:").pack()
output_entry = tk.Entry(root, width=20)
output_entry.pack()

# Dodanie opcji wyboru formatu
format_var = tk.StringVar(value="mp4")  # Ustawienie domyślnego formatu
tk.Label(root, text="Wybierz format pliku:").pack()
tk.Radiobutton(root, text="MP4", variable=format_var, value="mp4").pack()
tk.Radiobutton(root, text="MP3", variable=format_var, value="mp3").pack()

download_button = tk.Button(root, text="Pobierz i wytnij fragment", command=download_and_extract)
download_button.pack()

# Uruchomienie GUI
root.mainloop()
