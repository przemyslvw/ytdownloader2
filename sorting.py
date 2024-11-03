import os
import shutil

# Funkcja do sortowania plików
def sort_files(directory):
    # Definiowanie katalogów docelowych
    folders = {
        "DOKUMENTY": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "FILMY": [".mp4", ".avi", ".mov", ".mkv"],
        "OBRAZY": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "MUZYKA": [".mp3", ".wav", ".flac", ".aac"],
        "ZDJĘCIA": []  # specjalna kategoria na pliki zaczynające się od "IMG_" i "VID_"
    }
    
    # Tworzenie katalogów docelowych jeśli nie istnieją
    for folder in folders.keys():
        folder_path = os.path.join(directory, folder)
        os.makedirs(folder_path, exist_ok=True)

    # Iteracja przez wszystkie pliki w katalogu
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Pomijanie katalogów
        if os.path.isdir(file_path):
            continue
        
        # Obsługa plików "IMG_" oraz "VID_"
        if filename.startswith("IMG_") or filename.startswith("VID_"):
            shutil.move(file_path, os.path.join(directory, "ZDJĘCIA", filename))
            continue
        
        # Pobieranie rozszerzenia pliku
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Przypisywanie pliku do odpowiedniego katalogu na podstawie rozszerzenia
        moved = False
        for folder, extensions in folders.items():
            if file_extension in extensions:
                shutil.move(file_path, os.path.join(directory, folder, filename))
                moved = True
                break
        
        # Jeśli plik nie pasuje do żadnej kategorii, pozostaje w katalogu głównym
        if not moved:
            print(f"Nieznany typ pliku: {filename}")

# Wywołanie funkcji z wybranym katalogiem
directory = input("Podaj ścieżkę do katalogu do posortowania: ")
sort_files(directory)
