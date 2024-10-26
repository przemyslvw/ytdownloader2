import tkinter as tk
from helpers.video_info import fetch_video_length
from helpers.download_clip import download_and_extract

# Konfiguracja okna GUI
root = tk.Tk()
root.title("Pobieranie fragmentu YouTube")
root.geometry("400x350")

# Elementy interfejsu
tk.Label(root, text="Link do filmu:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

# Przycisk do pobrania długości filmu i ustawienia domyślnej nazwy pliku
check_button = tk.Button(root, text="Sprawdź film", command=lambda: fetch_video_length(url_entry, start_entry, end_entry, output_entry))
check_button.pack()

tk.Label(root, text="Czas początkowy (sekundy):").pack()
start_entry = tk.Entry(root, width=10)
start_entry.pack()

tk.Label(root, text="Czas końcowy (sekundy):").pack()
end_entry = tk.Entry(root, width=10)
end_entry.pack()

tk.Label(root, text="Nazwa zapisanego pliku:").pack()
output_entry = tk.Entry(root, width=20)
output_entry.pack()

# Dodanie opcji wyboru formatu
format_var = tk.StringVar(value="mp4")  # Ustawienie domyślnego formatu
tk.Label(root, text="Wybierz format pliku:").pack()
tk.Radiobutton(root, text="MP4", variable=format_var, value="mp4").pack()
tk.Radiobutton(root, text="MP3", variable=format_var, value="mp3").pack()

download_button = tk.Button(root, text="Pobierz i wytnij fragment", command=lambda: download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var))
download_button.pack()

# Uruchomienie GUI
root.mainloop()
