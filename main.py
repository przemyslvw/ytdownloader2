import tkinter as tk
from tkinter import messagebox
from yt_dlp import YoutubeDL
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip

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
root.geometry("400x300")

# Elementy interfejsu
tk.Label(root, text="Link do filmu:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

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
