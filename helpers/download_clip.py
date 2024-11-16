import os
import re
from yt_dlp import YoutubeDL
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from tkinter import messagebox


def sanitize_filename(filename):
    """
    Usuwa niedozwolone znaki z nazwy pliku.
    """
    return re.sub(r'[<>:"/\\|?*\u0000-\u001F]', '', filename)


def download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var):
    try:
        # Pobierz dane z pól tekstowych
        url = url_entry.get()
        start_time = int(start_entry.get())
        end_time = int(end_entry.get())
        output_filename = sanitize_filename(output_entry.get())
        selected_format = format_var.get()

        # Walidacja czasu
        if start_time < 0 or end_time <= start_time:
            messagebox.showerror("Błąd", "Nieprawidłowy czas początkowy lub końcowy.")
            return

        # Ustaw domyślną nazwę pliku, jeśli pole jest puste
        if not output_filename:
            output_filename = "clip"
        output_filename += f".{selected_format}"

        # Utwórz folder output, jeśli nie istnieje
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Ustawienia yt-dlp, wymuszenie formatu MP4
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
        }

        # Pobierz metadane wideo
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_title = sanitize_filename(info_dict.get('title', 'video').replace(' ', '_'))
            video_filename = os.path.join(output_dir, f"{video_title}.mp4")

        # Znajdź unikalną nazwę pliku
        counter = 1
        while os.path.exists(video_filename):
            video_filename = os.path.join(output_dir, f"{video_title}_{counter:03d}.mp4")
            counter += 1

        # Pobieranie wideo
        ydl_opts['outtmpl'] = video_filename
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Przycięcie lub wyodrębnienie dźwięku
        if selected_format == "mp4":
            ffmpeg_extract_subclip(video_filename, start_time, end_time, targetname=output_filename)
        elif selected_format == "mp3":
            with VideoFileClip(video_filename) as video:
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile(output_filename)

        messagebox.showinfo("Sukces", f"Wycinek zapisano jako {output_filename}")

    except ValueError:
        messagebox.showerror("Błąd", "Czas początkowy i końcowy muszą być liczbami.")
    except FileNotFoundError as e:
        messagebox.showerror("Błąd", f"Nie znaleziono pliku: {str(e)}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
