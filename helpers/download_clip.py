import os
from yt_dlp import YoutubeDL
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from tkinter import messagebox

def download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var):
    url = url_entry.get()
    start_time = int(start_entry.get())
    end_time = int(end_entry.get())
    output_filename = output_entry.get()
    selected_format = format_var.get()

    # Ustaw domyślną nazwę, jeśli pole jest puste
    if not output_filename:
        output_filename = "clip"
    output_filename += f".{selected_format}"  # Dodaj rozszerzenie do nazwy pliku

    # Find a unique filename for the downloaded video
    base_filename = "video"
    extension = ".mp4"
    counter = 1
    video_filename = base_filename + extension
    while os.path.exists(video_filename):
        video_filename = f"{base_filename}_{counter:03d}{extension}"
        counter += 1

    try:
        # Pobieranie wideo przy użyciu yt-dlp
        ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': video_filename}
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Przycięcie lub wyodrębnienie dźwięku w zależności od wybranego formatu
        if selected_format == "mp4":
            ffmpeg_extract_subclip(video_filename, start_time, end_time, targetname=output_filename)
        elif selected_format == "mp3":
            # Przycinanie fragmentu i zapis jako mp3
            with VideoFileClip(video_filename) as video:
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile(output_filename)
        
        messagebox.showinfo("Sukces", f"Wycinek zapisano jako {output_filename}")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))