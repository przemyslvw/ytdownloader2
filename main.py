import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from helpers.video_info import fetch_video_length
from helpers.download_clip import download_and_extract

# Konfiguracja nowoczesnego okna GUI z ThemedTk
root = ThemedTk(theme="arc")
root.title("Pobieranie fragmentu YouTube")
root.geometry("450x500")
root.resizable(False, False)

# Nowoczesny styl dla elementów interfejsu
style = ttk.Style()
style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
style.configure("TLabel", font=("Arial", 10))
style.configure("TEntry", padding=5)

# Funkcje animacji ładowania
def show_loading_animation():
    loading_label = ttk.Label(root, text="Ładowanie...", font=("Arial", 10, "italic"), foreground="blue")
    loading_label.pack(pady=5)
    root.update_idletasks()
    return loading_label

def hide_loading_animation(loading_label):
    loading_label.destroy()

def fetch_video_length_with_loading(url_entry, start_entry, end_entry, output_entry):
    loading_label = show_loading_animation()
    fetch_video_length(url_entry, start_entry, end_entry, output_entry)
    hide_loading_animation(loading_label)

# Elementy interfejsu
ttk.Label(root, text="Link do filmu:").pack(pady=5)
url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

check_button = ttk.Button(root, text="Sprawdź film", command=lambda: fetch_video_length_with_loading(url_entry, start_entry, end_entry, output_entry))
check_button.pack(pady=10)

ttk.Label(root, text="Czas początkowy (sekundy):").pack(pady=5)
start_entry = ttk.Entry(root, width=10)
start_entry.pack(pady=5)

ttk.Label(root, text="Czas końcowy (sekundy):").pack(pady=5)
end_entry = ttk.Entry(root, width=10)
end_entry.pack(pady=5)

ttk.Label(root, text="Nazwa zapisanego pliku:").pack(pady=5)
output_entry = ttk.Entry(root, width=20)
output_entry.pack(pady=5)

# Dodanie opcji wyboru formatu z nowoczesnym wyglądem
format_var = tk.StringVar(value="mp4")
ttk.Label(root, text="Wybierz format pliku:").pack(pady=5)
format_frame = ttk.Frame(root)
format_frame.pack()
ttk.Radiobutton(format_frame, text="MP4", variable=format_var, value="mp4").grid(row=0, column=0, padx=10)
ttk.Radiobutton(format_frame, text="MP3", variable=format_var, value="mp3").grid(row=0, column=1, padx=10)

def download_and_extract_with_loading(url_entry, start_entry, end_entry, output_entry, format_var):
    loading_label = show_loading_animation()
    download_and_extract(url_entry, start_entry, end_entry, output_entry, format_var)
    hide_loading_animation(loading_label)

download_button = ttk.Button(root, text="Pobierz i wytnij fragment", command=lambda: download_and_extract_with_loading(url_entry, start_entry, end_entry, output_entry, format_var))
download_button.pack(pady=20)

# Uruchomienie GUI
root.mainloop()
