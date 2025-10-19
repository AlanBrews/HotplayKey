import just_playback
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import keyboard
import os
import threading

def truncate_text(text, max_length=25):
        if len(text) > max_length:
            return text[:max_length - 3] + '...'
        return text

class AudioPlayer:
    def __init__(self):
        self.player = just_playback.Playback()
        self.is_playing = False
        self.hotkey = 'menu'
        self.file_path = ""
        self.volume = 0.75
        
        self.root = tk.Tk()
        self.root.title("HotPlaykey - Audio Player")
        self.root.geometry("270x300")
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        self.setup_hotkey()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="HotPlaykey Audio Player", 
                               font=("Arial", 16, "bold"), foreground="#FF9D00")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        file_frame = ttk.LabelFrame(main_frame, text="Audio File", padding="5")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.select_file)
        browse_btn.grid(row=0, column=1)
        
        volume_frame = ttk.LabelFrame(main_frame, text="Volume", padding="5")
        volume_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=1, orient=tk.HORIZONTAL, 
                                    command=self.set_volume)
        self.volume_scale.set(self.volume)
        self.volume_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        hotkey_frame = ttk.LabelFrame(main_frame, text="Hotkey Settings", padding="5")
        hotkey_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        hotkey_label = ttk.Label(hotkey_frame, text="Current hotkey: ")
        hotkey_label.grid(row=0, column=0, sticky=tk.W)
        
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        hotkey_display = ttk.Label(hotkey_frame, textvariable=self.hotkey_var, font=("Arial", 10, "bold"))
        hotkey_display.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        change_btn = ttk.Button(hotkey_frame, text="Change Hotkey", command=self.change_hotkey)
        change_btn.grid(row=0, column=2)
        
        self.status_var = tk.StringVar(value="Ready. Select an audio file to begin.")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        main_frame.columnconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
        volume_frame.columnconfigure(0, weight=1)
        hotkey_frame.columnconfigure(0, weight=0)
        hotkey_frame.columnconfigure(1, weight=1)
        
    def setup_hotkey(self):
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_playback)
            self.status_var.set(f"Hotkey set to: {self.hotkey}")
        except Exception as e:
            self.status_var.set(f"Error setting hotkey: {str(e)}")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Audio File (Not all audio types can be supported!)",
            filetypes=(
                ("Audio Files", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("OGG Files", "*.ogg"),
                ("FLAC Files", "*.flac"),
                ("M4A Files", "*.m4a"),
                ("All Files", "*.*")
            )
        )
        
        if file_path:
            try:
                self.player.load_file(file_path)
                self.file_path = file_path
                self.file_label.config(text=truncate_text(os.path.basename(file_path)))
                self.status_var.set(f"Loaded: {truncate_text(os.path.basename(file_path))}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load audio file: {str(e)}")
                self.status_var.set("Could not load audio file!")
    
    def toggle_playback(self):
        if not self.file_path:
            self.status_var.set("No audio file selected!")
            return
            
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            self.status_var.set("Playback stopped")
        else:
            self.player.play()
            self.is_playing = True
            self.status_var.set("Playing...")
    
    def stop_playback(self):
        self.player.stop()
        self.is_playing = False
        self.play_btn.config(text="Play")
        self.progress_var.set(0)
        self.status_var.set("Playback stopped")
    
    def set_volume(self, value):
        try:
            volume = float(value)
            self.player.set_volume(volume)
            self.volume = volume
        except:
            pass
    
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def change_hotkey(self):
        def wait_for_hotkey():
            self.status_var.set("Press a new hotkey combination...")
            recorded_hotkey = keyboard.read_hotkey(suppress=False)
            self.hotkey = recorded_hotkey
            self.hotkey_var.set(recorded_hotkey)
            
            keyboard.unhook_all_hotkeys()
            self.setup_hotkey()
            
            self.status_var.set(f"Hotkey changed to: {recorded_hotkey}")
        
        thread = threading.Thread(target=wait_for_hotkey)
        thread.daemon = True
        thread.start()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AudioPlayer()
    app.run()

