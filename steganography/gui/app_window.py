import tkinter as tk
from gui import screens

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("STEGANOGRAPHY Sistemi")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f4f6f7") # Genel arka plan
        
        # Global State (Sayfalar Arası Veri)
        self.cover_image_path = None
        self.secret_image_path = None
        self.stego_result_img = None 
        
        self.setup_ui()

    def setup_ui(self):
        # Ana Konteyner (Grid Sistemi)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # --- SOL MENÜ (SIDEBAR) ---
        self.sidebar = tk.Frame(self.root, width=220, bg="#2c3e50")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Genişliği sabit tut
        
        # Logo
        self.logo_label = tk.Label(self.sidebar, text="STEGANOGRAPHY", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        self.logo_label.pack(pady=(40, 30))

        # Menü Butonları
        self.btn_text = self.create_nav_button("Metin Gizle", lambda: self.show_page(screens.TextEncodePage, self.btn_text))
        self.btn_image = self.create_nav_button("Görsel Gizle", lambda: self.show_page(screens.ImageEncodePage, self.btn_image))
        self.btn_decode = self.create_nav_button("Veri Çöz", lambda: self.show_page(screens.DecodePage, self.btn_decode))

        # --- SAĞ İÇERİK ALANI ---
        self.main_frame = tk.Frame(self.root, bg="#f4f6f7")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
        # Başlangıç Sayfası
        self.current_page = None
        self.show_page(screens.TextEncodePage, self.btn_text)

    def create_nav_button(self, text, command):
        btn = tk.Button(self.sidebar, text=text, bg="#34495e", fg="white", 
                        activebackground="#2980b9", activeforeground="white", 
                        font=("Arial", 14), relief="flat", anchor="w", padx=20, command=command)
        btn.pack(fill="x", padx=15, pady=10)
        return btn

    def show_page(self, page_class, active_btn):
        # Aktif buton vurgusu
        for btn in [self.btn_text, self.btn_image, self.btn_decode]:
            btn.configure(bg="#34495e")
        active_btn.configure(bg="#2980b9") # Mavi vurgu
        
        # Sayfa Değişimi
        if self.current_page:
            self.current_page.destroy()
            
        self.current_page = page_class(self.main_frame, self)
        self.current_page.pack(fill="both", expand=True)

    def update_status(self, message):
        print(f"Durum: {message}")