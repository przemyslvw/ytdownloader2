# YT downloader 2

# YT Downloader 2

## Wymagania wstępne

- Python 3.8 lub nowszy
- FFmpeg
- Git (opcjonalnie, do klonowania repozytorium)

## Instalacja

### Metoda 1: Instalacja z repozytorium (zalecana)

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/przemyslvw/ytdownloader2.git
   cd ytdownloader2
   ```

2. Stwórz i aktywuj wirtualne środowisko Pythona:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # lub
   # venv\Scripts\activate  # Windows
   ```

3. Zainstaluj pakiet w trybie edytowalnym z zależnościami:
   ```bash
   pip install -e .
   ```

### Metoda 2: Instalacja bezpośrednia

```bash
pip install git+https://github.com/przemyslvw/ytdownloader2.git
```

### Instalacja zależności developerskich (opcjonalnie)

Jeśli chcesz współtworzyć projekt, zainstaluj dodatkowe zależności:

```bash
pip install -e ".[dev]"
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
