import os
import re
import subprocess
import json
import tempfile
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
    Pobiera metadane filmu za pomocą yt-dlp i zwraca jako dict.
    """
    try:
        yt_dlp_command = [
            "yt-dlp",
            "--no-warnings",
            "--ignore-errors",
            "--no-check-certificate",
            "--geo-bypass",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "--referer", "https://www.youtube.com/",
            "--dump-json",
            "--no-download",
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
            error_msg = result.stderr if result.stderr else "Pusta odpowiedź z serwera YouTube"
            raise Exception(f"Błąd: {error_msg}")
            
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print("Odpowiedź serwera (debug):")
            print(result.stdout[:500])  # Wyświetl pierwsze 500 znaków odpowiedzi
            raise Exception(f"Nieprawidłowa odpowiedź z serwera YouTube: {str(e)}")
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Nieznany błąd podczas pobierania informacji o filmie"
        raise Exception(f"Błąd podczas wykonywania yt-dlp: {error_msg}")


def download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var):
    try:
        url = url_entry.get().strip()
        if not url:
            messagebox.showerror("Błąd", "Proszę podać link do filmu")
            return

        # Pobierz informacje o filmie
        try:
            video_info = get_video_info(url)
            video_title = video_info.get('title', 'film')
            video_title = sanitize_filename(video_title)
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać informacji o filmie: {str(e)}")
            return

        # Sprawdź i przetwórz czasy
        try:
            start_time = float(start_entry.get().replace(',', '.'))
            end_time = float(end_entry.get().replace(',', '.'))
            
            if start_time < 0 or end_time <= start_time:
                raise ValueError("Nieprawidłowe wartości czasu")
                
        except ValueError as e:
            messagebox.showerror("Błąd", "Nieprawidłowy format czasu. Użyj liczb (np. 12.5)")
            return

        # Przygotuj ścieżki plików
        output_dir = os.path.dirname(os.path.abspath(output_entry.get())) if output_entry.get() else "./output"
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = output_entry.get() or f"{video_title}_fragment"
        output_filename = os.path.splitext(output_filename)[0]  # Usuń rozszerzenie jeśli istnieje
        selected_format = format_var.get()
        final_output_path = os.path.join(output_dir, f"{output_filename}.{selected_format}")
        
        # Unikalna nazwa pliku tymczasowego
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_video_path = temp_file.name

        # Pobierz film z użyciem yt-dlp z dodatkowymi opcjami
        yt_dlp_command = [
            "yt-dlp",
            "--no-warnings",
            "--ignore-errors",
            "--no-check-certificate",
            "--geo-bypass",
            "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "--output", temp_video_path,
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "--referer", "https://www.youtube.com/",
            url
        ]
        
        try:
            subprocess.run(yt_dlp_command, check=True)

            # Wytnij fragment
            if selected_format == "mp4":
                ffmpeg_extract_subclip(temp_video_path, start_time, end_time, targetname=final_output_path)
            elif selected_format == "mp3":
                with VideoFileClip(temp_video_path) as video:
                    audio = video.subclip(start_time, end_time).audio
                    audio.write_audiofile(final_output_path, logger=None)

            messagebox.showinfo("Sukces", f"Wycinek został zapisany jako:\n{final_output_path}")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Błąd", f"Błąd podczas pobierania filmu. Kod błędu: {e.returncode}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił nieoczekiwany błąd: {str(e)}")
        finally:
            # Sprzątanie plików tymczasowych
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            except Exception as e:
                print(f"Ostrzeżenie: Nie udało się usunąć pliku tymczasowego: {e}")

    except Exception as e:
        messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {str(e)}")
        
    finally:
        # Upewnij się, że plik tymczasowy zostanie usunięty nawet w przypadku błędu
        if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except:
                pass