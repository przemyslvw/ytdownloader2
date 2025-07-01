# YT downloader 2

## Wymagania wstępne

1. Python 3.6 lub nowszy
2. FFmpeg

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone [adres-repozytorium]
   cd ytdownloader2
   ```

2. Stwórz i aktywuj wirtualne środowisko Pythona:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # lub
   # venv\Scripts\activate  # Windows
   ```

3. Zainstaluj wymagane pakiety:
   ```bash
   pip install -r requirements.txt
   ```

## Instalacja FFmpeg

### Windows:
1. Pobierz FFmpeg ze strony: https://ffmpeg.org/download.html
2. Wypakuj do `C:\ffmpeg`
3. Dodaj `C:\ffmpeg\bin` do zmiennej środowiskowej Path
4. Sprawdź instalację:
   ```bash
   ffmpeg -version
   ```

### Linux (Debian/Ubuntu):
```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS (z użyciem Homebrew):
```bash
brew install ffmpeg
```

## Uruchomienie

```bash
python main.py
```

## Rozwiązywanie problemów

Jeśli wystąpi błąd `ModuleNotFoundError` dla `moviepy.editor`:
```bash
pip uninstall -y moviepy
pip install moviepy==1.0.3
```

Jeśli wystąpi błąd zależności, spróbuj zainstalować brakujące pakiety ręcznie:
```bash
pip install ttkthemes
```

## Wymagane pakiety (zapisane w requirements.txt)
- yt-dlp
- moviepy
- ttkthemes
