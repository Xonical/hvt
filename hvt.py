from tkinter import Tk, Label, Button, messagebox, Frame, Toplevel, font
import tkinter as tk
import random
import winsound
import subprocess
import threading
import sys


try:
    import keyboard
    # Hier Code für die Verwendung von keyboard
except ImportError:
    print("pynput-Modul nicht installiert. Installation wird gestartet ...")
    subprocess.call(["pip", "install", "keyboard"])
    import keyboard
    # Hier Code für die Verwendung von keyboard

class AppThread(threading.Thread):
    
    def __init__(self, queue=None):
        self.queue = queue
        self.key = None
        self.count = 0
        
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        # Collect events until released
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            self.update_queue(key.char)
        except AttributeError:
            print('special key {0} pressed'.format(
                key))
            
    def on_release(self, key):
        return
        # print('{0} released'.format(
            # key))
        # if key == keyboard.Key.esc:
            # # Stop listener
            # return False
        
    def update_queue(self, count):
        self.queue.put(count)
        self.queue.join()

# Danke ChatGPT :-)
class IBANGenerator:
    def __init__(self):
        self.bank_codes = {
            '10070000': 'Deutsche Bank',
            '20030000': 'Commerzbank',
            '70020270': 'BayernLB',
            '50060400': 'DekaBank',
            '20050000': 'HSH Nordbank',
            '50050201': 'Frankfurter Sparkasse',
            '70050000': 'Stadtsparkasse München',
            '50020000': 'Sparkasse Niedersachsen',
            '25060414': 'Volksbanken Raiffeisenbanken in Niedersachsen',
        }
    
    def generate(self):
        # Generiere eine zufällige Bankleitzahl (Bankcode)
        bank_code = random.choice(list(self.bank_codes.keys()))
        
        # Generiere eine zufällige Kontonummer mit 10-stelligen Zahlen
        account_number = ''.join(random.choices('0123456789', k=10))
        
        # Berechne die Prüfziffer
        check_digit = self.calculate_check_digit(bank_code, account_number)
        
        # Kombiniere die einzelnen Teile zur IBAN
        iban = f'DE{check_digit}{bank_code}{account_number}'
        
        return iban, self.bank_codes[bank_code]
    
    def calculate_check_digit(self, bank_code, account_number):
        # Füge führende Nullen hinzu, falls die Kontonummer weniger als 10 Stellen hat
        account_number = account_number.zfill(10)
        
        # Kombiniere Bankleitzahl (Bankcode) und Kontonummer
        combined = f'{bank_code}{account_number}131400'
        
        # Berechne die Prüfziffer basierend auf der Modulo-97 Methode
        remainder = int(combined) % 97
        check_digit = str(98 - remainder).zfill(2)
        
        return check_digit

class Toast:
    def __init__(self, root, msg):
        self.root = root
        self.msg = msg
        
        self.toast = tk.Toplevel(root)
        self.toast.geometry("200x100+300+300")
        self.toast.configure(background="black")
        
        self.label = tk.Label(self.toast, text=msg, fg="white", bg="black")
        self.label.pack(pady=20)
        
    def show(self, duration=2000):
        self.toast.after(duration, self.hide)
        self.toast.mainloop()
        
    def hide(self):
        self.toast.destroy()

class MyButton(tk.Button):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.config(
            relief=tk.FLAT,
            bg='#4CAF50',
            activebackground='#45a049',
            fg='white',
            activeforeground='white',
            font=('Arial', 12, 'bold')
        )

class ApplicationWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Tools")
        self.geometry("468x140")
        self.minsize(120, 80)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.iban_generator = IBANGenerator()
        # BEG Zeile IBAN # 
        entry_font = font.Font(family="Consolas", size=12)
        self.entry = tk.Entry(self)
        self.entry["font"] = entry_font
        self.entry.grid(row=0, column=0, padx=(10,5), sticky="nsew")
        
        self.button2 = MyButton(self, text="Neu", width=10, command=self.generate_iban).grid(row=0, column=1, padx=(5,5), sticky="ns")
        self.button3 = MyButton(self, text="Kopieren", width=10, command=self.copy_iban).grid(row=0, column=2, padx=(5,10), sticky="ns")
        # END Zeile IBAN #
        
        # BEG Datenbank #
        self.btn_db = MyButton(self, text="DB ersetzen", width=10, command=self.run_dbr)
        self.btn_db.grid(row=1, column=2, padx=(5,10), pady=(30,10), sticky="s")
        # END Datenbank # 

        self.grid = self.grid_size()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        # Zeilenkonfiguration
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # Frame (Status) unten erstellen
        bottom_frame = tk.Frame(self, height=50, bg='lightgray')  # Erstellen des Frame-Widgets mit einer Höhe von 50 Pixeln und einem Hintergrund von 'lightgray'
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky='swe')  # Platzieren des Frames in der zweiten Zeile des Grids, über drei Spalten, so dass er sich horizontal erstreckt
        self.lbl_message = tk.Label(bottom_frame, bg='lightgray')
        self.lbl_message.pack(side='top', padx=10, pady=10)
        self.generate_iban()

    def on_closing(self):
        # Verhindere das Schließen. Verstecke das Fenster nur.
        self.withdraw()

    def clear_status_message(self):
        self.lbl_message.config(text="")  # den Text löschen

    def generate_iban(self):
        self.entry.delete(0, tk.END)  # den vorhandenen Text im Entry-Widget löschen
        self.entry.insert(0,self.iban_generator.generate()[0])
        self.bank = self.iban_generator.generate()[1]
        
    def copy_iban(self):
        self.clipboard_clear()
        self.clipboard_append(self.entry.get())
        self.update() # now it stays on the clipboard after the window is closed
        self.lbl_message.config(text=str("Zufällige IBAN von \"" + self.bank + "\" in die Zwischenablage kopiert"))
        self.after(4000, self.clear_status_message)

    def run_dbr(self):
        script_path = 'dbr.py'
        # Kommando, um das externe Skript auszuführen
        command = ['python', script_path]
        # Ausführung des externen Skripts und Abfangen der Ausgaben
        output = subprocess.check_output(command, universal_newlines=True)
        print(output)

    def manage_app_window(self):
        self.deiconify()

    def change_visibility(self):
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.update()
            self.deiconify()

    def center_window(self, window):
        self.update_idletasks()
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))



class MainWindow(object):
    def __init__(self):
        super().__init__()  # Ruft den Konstruktor der Elternklasse auf
        self.root = tk.Tk()

        # Erstelle das Hauptfenster
        self.root.overrideredirect(True)# Rahmenloses Fenster

        button = tk.Button(self.root, text="X", bg="red", fg="white", width=1, height=1, padx=5, pady=5, relief="flat", command=self.close_window)
        button.config(font=("Arial", 14, "bold"))
        button.config(activebackground=button['background'])
        button.pack()

        # Bestimme die Bildschirmgröße
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Bestimme die Fenstergröße
        window_width = 40
        window_height = 30

        # Berechne die Position des Fensters
        x = screen_width - window_width
        y = 0

        # Setze die Position des Fensters
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Setze das Fenster on-top
        self.root.attributes("-topmost", True)

        self.root.bind("<B3-Motion>",self.move_window)
        self.root.bind("<ButtonPress-3>", self.start_move)

    def run(self):
        self.root.mainloop()

    def close_window(self):
        sys.exit(0)

    def move_window(self, event):
        x = self.root.winfo_pointerx() - self.root._offsetx
        y = self.root.winfo_pointery() - self.root._offsety
        self.root.geometry(f"+{x}+{y}")

    def start_move(self, event):
        self.root._offsetx = event.x
        self.root._offsety = event.y



def HotkeyPressed():
    app_window.change_visibility()


if __name__ == "__main__":
    keyboard.add_hotkey('ctrl+<', HotkeyPressed)
    main_window = MainWindow()
    app_window = ApplicationWindow()
    main_window.run()
