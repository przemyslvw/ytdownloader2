import tkinter as tk
from tkinter import messagebox
from pytube import YouTube
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# Funkcja do pobierania i wycinania fragmentu
def download_and_extract():
    url = url_entry.get()
    start_time = int(start_entry.get())
    end_time = int(end_entry.get())
    output_filename = output_entry.get()

    # Ustaw domyślną nazwę, jeśli pole jest puste
    if not output_filename:
        output_filename = "clip.mp4"
    else:
        output_filename += ".mp4"

    try:
        # Pobieranie wideo
        yt = YouTube(url)
        stream = yt.streams.filter(file_extension="mp4", res="720p").first()
        video_path = "video.mp4"
        stream.download(filename=video_path)

        # Przycięcie fragmentu
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=output_filename)
        messagebox.showinfo("Sukces", f"Wycinek zapisano jako {output_filename}")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

# Konfiguracja okna GUI
root = tk.Tk()
root.title("Pobieranie fragmentu YouTube")
root.geometry("400x250")

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

download_button = tk.Button(root, text="Pobierz i wytnij fragment", command=download_and_extract)
download_button.pack()

# Uruchomienie GUI
root.mainloop()
