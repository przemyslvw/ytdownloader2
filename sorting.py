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
    
    # Dodanie folderu "INNE" do przechowywania niepasujących plików i folderów
    other_folder = os.path.join(directory, "INNE")
    os.makedirs(other_folder, exist_ok=True)

    # Tworzenie katalogów docelowych jeśli nie istnieją
    for folder in folders.keys():
        folder_path = os.path.join(directory, folder)
        os.makedirs(folder_path, exist_ok=True)

    # Iteracja przez wszystkie pliki i katalogi w głównym katalogu
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Pomijanie głównych folderów docelowych, aby nie przenosić ich do "INNE"
        if filename in folders.keys() or filename == "INNE":
            continue

        # Obsługa plików "IMG_" oraz "VID_"
        if os.path.isfile(file_path) and (filename.startswith("IMG_") or filename.startswith("VID_")):
            shutil.move(file_path, os.path.join(directory, "ZDJĘCIA", filename))
            continue
        
        # Pobieranie rozszerzenia pliku
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Przypisywanie pliku do odpowiedniego katalogu na podstawie rozszerzenia
        moved = False
        if os.path.isfile(file_path):  # Przenoszenie tylko plików, nie katalogów
            for folder, extensions in folders.items():
                if file_extension in extensions:
                    shutil.move(file_path, os.path.join(directory, folder, filename))
                    moved = True
                    break

        # Jeśli plik lub katalog nie pasuje do żadnej kategorii, przenieś do "INNE"
        if not moved:
            shutil.move(file_path, os.path.join(other_folder, filename))

# Wywołanie funkcji z wybranym katalogiem
directory = input("Podaj ścieżkę do katalogu do posortowania: ")
sort_files(directory)
