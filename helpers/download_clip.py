import os
import re
import subprocess
import json
import tempfile
import logging
from moviepy.video.io.VideoFileClip import VideoFileClip
from tkinter import messagebox

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            "--geo-bypass",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--referer", "https://www.youtube.com/",
            "--dump-json",
            url
        ]
        
        logger.info(f"Wykonywanie komendy: {' '.join(yt_dlp_command)}")
        result = subprocess.run(yt_dlp_command, capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            raise Exception("Pusta odpowiedź z serwera")
            
        try:
            video_info = json.loads(result.stdout)
            if not isinstance(video_info, dict) or 'title' not in video_info:
                logger.error(f"Nieprawidłowa struktura odpowiedzi: {video_info}")
                raise Exception("Nie można odczytać informacji o filmie. Sprawdź poprawność linku.")
            return video_info
        except json.JSONDecodeError as e:
            logger.error("Nie można sparsować odpowiedzi JSON")
            if result.stderr:
                logger.error(f"Błąd stderr: {result.stderr}")
            if result.stdout:
                logger.error(f"Odpowiedź stdout (początek): {result.stdout[:500]}")
            raise Exception("Nieprawidłowa odpowiedź z serwera YouTube. Spróbuj ponownie później.")
            
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Nieznany błąd podczas pobierania informacji o filmie"
        logger.error(f"Błąd yt-dlp (kod {e.returncode}): {error_msg}")
        if "HTTP Error 429" in error_msg:
            raise Exception("Zbyt wiele żądań. Proszę spróbować ponownie później.")
        elif "This video is not available" in error_msg:
            raise Exception("Film jest niedostępny lub został usunięty.")
        else:
            raise Exception(f"Błąd podczas łączenia z YouTube: {error_msg}")
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd: {str(e)}")
        raise Exception(f"Wystąpił błąd: {str(e)}")

def download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var, use_browser_cookies=False):
    """
    Pobiera i wycina fragment filmu z YouTube.
    
    Args:
        url_entry: Pole z adresem URL filmu
        start_entry: Pole z czasem początkowym w sekundach
        end_entry: Pole z czasem końcowym w sekundach
        output_entry: Pole z nazwą pliku wyjściowego
        format_var: Zmienna z wybranym formatem wyjściowym
        use_browser_cookies: Czy użyć ciasteczek z przeglądarki (domyślnie False)
    """
    process = None
    temp_dir = None
    
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
            logger.info(f"Pobieranie filmu: {video_title}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się pobrać informacji o filmie: {str(e)}")
            return

        # Sprawdź i przetwórz czasy
        try:
            start_time = float(start_entry.get().replace(',', '.'))
            end_time = float(end_entry.get().replace(',', '.'))
            
            if start_time < 0 or end_time <= start_time:
                raise ValueError("Czas końcowy musi być większy od początkowego i dodatni")
                
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
        
        # Utwórz katalog tymczasowy
        temp_dir = tempfile.mkdtemp()
        temp_video_path = os.path.join(temp_dir, "temp_video.%(ext)s")

        try:
            # Pobierz film z użyciem yt-dlp
            logger.info("Pobieranie filmu z YouTube...")
            yt_dlp_command = [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--output", temp_video_path,
                "--newline",
                "--no-part",
                "--geo-bypass",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--referer", "https://www.youtube.com/",
                *(["--cookies-from-browser", "firefox"] if use_browser_cookies else []),
                "--merge-output-format", "mp4",
                "--force-overwrites",
                "--no-mtime",
                "--no-check-certificate",
                "--extractor-args", "youtube:player_client=android",
                "--extractor-args", "youtube:player_skip=webpage",
                "--extractor-args", "youtube:player_backend=web",
                "--extractor-args", "youtube:include_hls=1",
                "--extractor-args", "youtube:include_dash_mp4=1",
                "--throttled-rate", "100K",
                "--socket-timeout", "30",
                "--source-address", "0.0.0.0",
                "--force-ipv4",
                "--retries", "10",
                "--fragment-retries", "10",
                "--buffer-size", "16K",
                "--http-chunk-size", "1M",
                "--no-check-formats",
                "--no-warnings",
                "--ignore-errors",
                url
            ]
            
            # Uruchom proces z wyjściem w czasie rzeczywistym
            process = subprocess.Popen(
                yt_dlp_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                text=True
            )
            
            # Wyświetl postęp w konsoli
            for line in process.stdout:
                logger.info(line.strip())
                
            # Poczekaj na zakończenie procesu
            process.wait()
            
            # Sprawdź kod wyjścia
            if process.returncode != 0:
                error_output = ""
                if process.stderr:
                    error_output = process.stderr
                elif process.stdout:
                    error_output = process.stdout
                raise subprocess.CalledProcessError(
                    process.returncode, 
                    yt_dlp_command,
                    output=error_output,
                    stderr=error_output
                )
            
            # Znajdź rzeczywistą nazwę pliku (yt-dlp może dodać rozszerzenie)
            actual_video_path = temp_video_path % {'ext': 'mp4'}
            if not os.path.exists(actual_video_path):
                # Spróbuj znaleźć plik z innym rozszerzeniem
                for f in os.listdir(temp_dir):
                    if f.startswith("temp_video."):
                        actual_video_path = os.path.join(temp_dir, f)
                        break
            
            if not os.path.exists(actual_video_path) or os.path.getsize(actual_video_path) == 0:
                raise Exception("Pobrany plik wideo jest pusty lub nie istnieje")
                
            logger.info("Pobieranie zakończone pomyślnie")

            # Wytnij fragment
            logger.info(f"Przetwarzanie wideo: wycinanie fragmentu od {start_time}s do {end_time}s")
            
            if selected_format == "mp4":
                try:
                    # Najpierw sprawdź czy plik wejściowy istnieje i ma odpowiedni rozmiar
                    if not os.path.exists(actual_video_path):
                        raise FileNotFoundError(f"Plik wideo nie istnieje: {actual_video_path}")
                        
                    file_size = os.path.getsize(actual_video_path)
                    if file_size == 0:
                        raise ValueError(f"Plik wideo jest pusty: {actual_video_path}")
                    
                    logger.info(f"Przetwarzanie pliku o rozmiarze: {file_size / (1024*1024):.2f} MB")
                    
                    # Użyj trybu copy dla szybszego przetwarzania
                    cmd = [
                        'ffmpeg',
                        '-y',
                        '-ss', str(start_time),
                        '-i', actual_video_path,
                        '-to', str(end_time - start_time),
                        '-c:v', 'copy',  # Użyj copy dla szybszego przetwarzania
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        '-movflags', '+faststart',
                        final_output_path
                    ]
                    
                    logger.info(f"Uruchamianie ffmpeg: {' '.join(cmd)}")
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    logger.info(f"ffmpeg zakończony z kodem {result.returncode}")
                    
                    # Sprawdź czy plik wyjściowy został utworzony
                    if not os.path.exists(final_output_path) or os.path.getsize(final_output_path) == 0:
                        raise Exception("Nie udało się utworzyć pliku wyjściowego")
                        
                except subprocess.CalledProcessError as e:
                    logger.error(f"Błąd ffmpeg (kod {e.returncode}): {e.stderr}")
                    raise Exception(f"Błąd przetwarzania wideo: {e.stderr}")
                
            elif selected_format == "mp3":
                video = VideoFileClip(actual_video_path)
                audio = video.subclip(start_time, end_time).audio
                audio.write_audiofile(
                    final_output_path,
                    codec='libmp3lame',
                    bitrate='192k',
                    logger=None
                )
                video.close()
                audio.close()

            logger.info(f"Plik został zapisany jako: {final_output_path}")
            messagebox.showinfo("Sukces", f"Wycinek został zapisany jako:\n{final_output_path}")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Błąd podczas pobierania filmu (kod {e.returncode})"
            logger.error(error_msg)
            messagebox.showerror("Błąd", error_msg)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Nieoczekiwany błąd: {error_msg}")
            messagebox.showerror("Błąd", f"Wystąpił nieoczekiwany błąd: {error_msg}")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Krytyczny błąd: {error_msg}")
        messagebox.showerror("Błąd krytyczny", f"Wystąpił krytyczny błąd: {error_msg}")
        
    finally:
        # Zatrzymaj proces, jeśli jeszcze działa
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Sprzątanie plików tymczasowych
        if temp_dir and os.path.exists(temp_dir):
            try:
                for file in os.listdir(temp_dir):
                    try:
                        file_path = os.path.join(temp_dir, file)
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        logger.warning(f"Nie udało się usunąć pliku {file}: {e}")
                os.rmdir(temp_dir)
                logger.info("Usunięto pliki tymczasowe")
            except Exception as e:
                logger.warning(f"Nie udało się usunąć plików tymczasowych: {e}")