import os
import re
import subprocess
import json
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
from tkinter import messagebox


def sanitize_filename(filename):
    """
    Usuwa niedozwolone znaki z nazwy pliku.
    """
    return re.sub(r'[<>:"/\\|?*\u0000-\u001F]', '', filename)


def get_video_info(url):
    """
    Pobiera metadane filmu za pomocą yt-dlp.exe i zwraca jako dict.
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
        messagebox.showerror("Błąd", f"Błąd przy pobieraniu metadanych:\n{e.output}")
        raise


def download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var):
    try:
        url = url_entry.get()
        start_time = int(start_entry.get())
        end_time = int(end_entry.get())
        output_filename = sanitize_filename(output_entry.get())
        selected_format = format_var.get()

        if start_time < 0 or end_time <= start_time:
            messagebox.showerror("Błąd", "Nieprawidłowy czas początkowy lub końcowy.")
            return

        if not output_filename:
            output_filename = "clip"

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Pobierz info o filmie
        info_dict = get_video_info(url)

        print("=== FORMATY DOSTĘPNE DLA TEGO FILMU ===")
        for f in info_dict.get('formats', []):
            print(f"{f['format_id']} - {f.get('ext')} - {f.get('format_note')} - {f.get('resolution')} - {f.get('fps')}")

        video_title = sanitize_filename(info_dict.get('title', 'video').replace(' ', '_'))
        temp_video_path = os.path.join(output_dir, f"{video_title}.mp4")
        final_output_path = os.path.join(output_dir, f"{output_filename}.{selected_format}")

        # Pobierz film przy pomocy yt-dlp.exe
        subprocess.run(
            ["yt-dlp.exe", "-f", "best", "-o", temp_video_path, url],
            check=True
        )

        # Wytnij fragment
        if selected_format == "mp4":
            ffmpeg_extract_subclip(temp_video_path, start_time, end_time, targetname=final_output_path)
        elif selected_format == "mp3":
            with VideoFileClip(temp_video_path) as video:
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile(final_output_path)

        # Usuń plik tymczasowy
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

        messagebox.showinfo("Sukces", f"Wycinek zapisano jako {final_output_path}")

    except ValueError:
        messagebox.showerror("Błąd", "Czas początkowy i końcowy muszą być liczbami.")
    except FileNotFoundError as e:
        messagebox.showerror("Błąd", f"Nie znaleziono pliku: {str(e)}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Błąd", f"Błąd yt-dlp:\n{e.output}")
    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
