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
            "--no-check-certificate",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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

def download_video(url, output_path, use_cookies=False):
    """
    Pobiera film z YouTube z obsługą błędów i automatycznymi fallbackami.
    
    Args:
        url: URL filmu do pobrania
        output_path: Ścieżka do zapisu pliku (z placeholderem %(ext)s)
        use_cookies: Czy użyć ciasteczek z przeglądarki
    
    Returns:
        tuple: (success: bool, output_path: str, error: str)
    """
    # Formaty do próbowania w kolejności
    format_attempts = [
        # Najlepsza jakość do 1080p, MP4 + M4A
        "bestvideo[ext=mp4][height<=1080][fps<=60]+bestaudio[ext=m4a]/best[ext=mp4][height<=1080]/best[height<=1080]",
        # Dowolna jakość MP4
        "best[ext=mp4]",
        # Ostateczne rozwiązanie - cokolwiek dostępne
        "best"
    ]
    
    for attempt, format_str in enumerate(format_attempts, 1):
        try:
            logger.info(f"Próba {attempt}: Pobieranie w formacie: {format_str}")
            
            cmd = [
                "yt-dlp",
                "-f", format_str,
                "--output", output_path,
                "--newline",
                "--no-part",
                "--geo-bypass",
                "--no-check-certificate",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--referer", "https://www.youtube.com/",
                "--merge-output-format", "mp4",
                "--force-overwrites",
                "--no-mtime",
                "--retries", "5",
                "--fragment-retries", "5",
                "--buffer-size", "16K",
                "--http-chunk-size", "1M",
                "--no-warnings",
                "--ignore-errors"
            ]
            
            if use_cookies:
                cmd.extend(["--cookies-from-browser", "firefox"])
                
            cmd.append(url)
            
            logger.info(f"Wykonywanie komendy: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                text=True
            )
            
            # Wyświetl postęp w czasie rzeczywistym
            output = []
            for line in process.stdout:
                line = line.strip()
                output.append(line)
                logger.info(f"[yt-dlp] {line}")
                
            process.wait()
            
            if process.returncode == 0:
                # Znajdź faktyczną ścieżkę do pobranego pliku
                final_path = output_path.replace('%(ext)s', 'mp4')
                if os.path.exists(final_path):
                    return True, final_path, None
                    
            # Jeśli doszliśmy tutaj, coś poszło nie tak
            error_msg = f"Błąd podczas próby {attempt}: "
            error_msg += "\n".join(line for line in output if 'error' in line.lower() or 'failed' in line.lower())
            logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Błąd podczas próby {attempt}: {str(e)}"
            logger.exception(error_msg)
    
    return False, None, "Wszystkie próby pobrania filmu zakończyły się niepowodzeniem"

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
        temp_video_path = os.path.join(temp_dir, "video.%(ext)s")

        try:
            # Pobierz film z użyciem yt-dlp
            logger.info("Pobieranie filmu z YouTube...")
            
            # Użyj nowej funkcji do pobierania
            success, downloaded_file, error_msg = download_video(
                url, 
                temp_video_path,
                use_cookies=use_browser_cookies
            )
            
            if not success or not downloaded_file:
                logger.error(f"Nie udało się pobrać filmu: {error_msg}")
                messagebox.showerror("Błąd", f"Nie udało się pobrać filmu: {error_msg}")
                return
                
            logger.info(f"Pomyślnie pobrano plik: {downloaded_file}")
            
            # Sprawdź rozmiar pliku
            file_size = os.path.getsize(downloaded_file) / (1024 * 1024)  # w MB
            if file_size < 0.1:  # Jeśli plik jest mniejszy niż 100KB, prawdopodobnie coś poszło nie tak
                raise Exception("Pobrany plik jest zbyt mały, prawdopodobnie wystąpił błąd podczas pobierania")
                
            logger.info(f"Rozmiar pobranego pliku: {file_size:.2f} MB")
            
            # Przygotuj docelową ścieżkę
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # Sprawdź i przetwórz czasy
            try:
                start_time = float(start_entry.get().replace(',', '.'))
                end_time = float(end_entry.get().replace(',', '.'))
                
                if start_time < 0 or end_time <= start_time:
                    raise ValueError("Czas końcowy musi być większy od początkowego i dodatni")
                    
                # Przygotuj komendę do przycięcia filmu
                cmd = [
                    "ffmpeg",
                    "-y",  # Nadpisz plik wyjściowy, jeśli istnieje
                    "-i", downloaded_file,
                    "-ss", str(start_time),
                    "-to", str(end_time),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-strict", "experimental",
                    "-b:a", "192k",
                    "-movflags", "+faststart",
                    final_output_path
                ]
                
                logger.info(f"Przycinanie filmu: {' '.join(cmd)}")
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    text=True
                )
                
                # Wyświetl postęp w czasie rzeczywistym
                for line in process.stdout:
                    line = line.strip()
                    if 'time=' in line and 'bitrate=' in line:
                        logger.info(f"[ffmpeg] {line}")
                        
                process.wait()
                
                if process.returncode != 0:
                    raise Exception(f"Błąd podczas przycinania filmu (kod {process.returncode})")
                    
                logger.info(f"Pomyślnie zapisano plik: {final_output_path}")
                messagebox.showinfo("Sukces", f"Pomyślnie zapisano plik:\n{final_output_path}")
                
            except ValueError as e:
                messagebox.showerror("Błąd", f"Nieprawidłowy format czasu: {str(e)}")
                return
                
        except Exception as e:
            logger.exception("Błąd podczas przetwarzania filmu")
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas przetwarzania filmu: {str(e)}")
            return
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Krytyczny błąd: {error_msg}")
        messagebox.showerror("Błąd krytyczny", f"Wystąpił krytyczny błąd: {error_msg}")
        
    finally:
        # Sprzątanie po sobie
        if process and hasattr(process, 'poll') and process.poll() is None:
            try:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except (subprocess.TimeoutExpired, AttributeError):
                    try:
                        process.kill()
                    except:
                        pass
            except Exception as e:
                logger.error(f"Błąd podczas zatrzymywania procesu: {str(e)}")
        
        if temp_dir and os.path.exists(temp_dir):
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # Usuń wszystkie pliki w katalogu tymczasowym
                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path, ignore_errors=True)
                        except Exception as e:
                            logger.warning(f"Nie udało się usunąć {file_path}: {str(e)}")
                    
                    # Spróbuj usunąć katalog
                    os.rmdir(temp_dir)
                    logger.info("Pomyślnie usunięto pliki tymczasowe")
                    break
                    
                except OSError as e:
                    if attempt == max_attempts - 1:  # Ostatnia próba
                        logger.error(f"Nie udało się usunąć katalogu tymczasowego {temp_dir}: {str(e)}")
                        # Próba zmiany uprawnień i ponowne usunięcie
                        try:
                            os.chmod(temp_dir, 0o777)
                            for root, dirs, files in os.walk(temp_dir, topdown=False):
                                for name in files:
                                    os.chmod(os.path.join(root, name), 0o777)
                                for name in dirs:
                                    os.chmod(os.path.join(root, name), 0o777)
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            logger.info("Pomyślnie usunięto katalog tymczasowy po zmianie uprawnień")
                        except Exception as e2:
                            logger.error(f"Błąd podczas usuwania katalogu po zmianie uprawnień: {str(e2)}")
                    time.sleep(1)  # Poczekaj chwilę przed ponowną próbą