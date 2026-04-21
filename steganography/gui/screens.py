import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import numpy as np
# Ekstra modüller eklendi
from core import pvd_utils, pvd_encoder, pvd_decoder
from analysis import security, visualization

class TextEncodePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        self.title = tk.Label(self, text="Görsel İçine Metin Gizleme", font=("Arial", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title.pack(anchor="w", pady=(0, 30))
        
        self.top_frame = tk.Frame(self, bg="#f4f6f7")
        self.top_frame.pack(fill="x", pady=10)
        
        self.btn_select = tk.Button(self.top_frame, text="Görseli Seç", font=("Arial", 12, "bold"),
                                    bg="#3498db", fg="white", relief="flat", width=20, height=2, command=self.select_cover)
        self.btn_select.pack(side="left", padx=(0, 20))
       
        self.preview_frame = tk.Frame(self, width=350, height=220, bg="#bdc3c7")
        self.preview_frame.pack(anchor="w", pady=10)
        self.preview_frame.pack_propagate(False)
        
        self.lbl_preview = tk.Label(self.preview_frame, text="Görsel Bekleniyor...", bg="#bdc3c7", fg="#7f8c8d")
        self.lbl_preview.pack(expand=True)
        
        self.lbl_text = tk.Label(self, text="Gizlenecek Gizli Veri:", font=("Arial", 14, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.lbl_text.pack(anchor="w", pady=(20, 5))
        
        self.text_input = tk.Text(self, height=5, width=60, font=("Arial", 12))
        self.text_input.pack(anchor="w")
        
        self.btn_process = tk.Button(self, text="Başlat", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", 
                                     relief="flat", width=25, height=2, command=self.process)
        self.btn_process.pack(anchor="w", pady=30)

    def select_cover(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*")])
        if file_path:
            self.controller.cover_image_path = file_path
            
            img = Image.open(file_path)
            img = img.resize((350, 220), Image.Resampling.LANCZOS)
            my_image = ImageTk.PhotoImage(img)
            
            self.lbl_preview.image = my_image
            self.lbl_preview.configure(image=my_image, text="")
            self.controller.update_status("Kapak görseli yüklendi.")

    def process(self):
        if not self.controller.cover_image_path:
            messagebox.showwarning("Uyarı", "Kapak görseli seçin!")
            return

        secret_text = self.text_input.get("1.0", "end-1c").strip()
        if not secret_text:
            messagebox.showwarning("Uyarı", "Gizlenecek metni girin!")
            return
        
        self.controller.update_status("Veri şifreleniyor ve matris hesaplanıyor...")
        try:
            pixel_matrix = pvd_utils.load_image_as_matrix(self.controller.cover_image_path)
            
            # HATA DÜZELTİLDİ: key parametresi kaldırıldı, arka planla uyumlu hale getirildi.
            binary_message = pvd_encoder.text_to_bits(secret_text) 
            self.controller.stego_result_img = pvd_encoder.encode(pixel_matrix, binary_message)
            
            self.show_result_window()
        except Exception as e:
            messagebox.showerror("Hata", f"İşlem sırasında hata oluştu:\n{str(e)}")

    def show_result_window(self):
        dialog = tk.Toplevel(self)
        dialog.title("İşlem Başarılı")
        dialog.geometry("400x550")
        dialog.configure(bg="#f4f6f7")
        
        # DÜZELTME: grab_set() ve transient() kaldırıldı, böylece pencereler kilitlenmeyecek
        dialog.focus()
        
        tk.Label(dialog, text="Veri Başarıyla Gizlendi!", font=("Arial", 16, "bold"), bg="#f4f6f7", fg="#2ecc71").pack(pady=15)
        
        img = self.controller.stego_result_img.copy()
        img.thumbnail((300, 250)) 
        my_image = ImageTk.PhotoImage(img)
        
        label = tk.Label(dialog, image=my_image, bg="#f4f6f7")
        label.image = my_image 
        label.pack(pady=10)
        
        # DÜZELTME: show_analysis_dashboard fonksiyonuna 'dialog' değişkenini ebeveyn olarak gönderiyoruz
        tk.Button(dialog, text="Analiz Sonuçlarını Gör", bg="#9b59b6", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2,
                  command=lambda: self.show_analysis_dashboard(dialog)).pack(pady=5)
                  
        tk.Button(dialog, text="Görseli Kaydet", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2,
                  command=lambda: self.save_and_close(dialog)).pack(pady=5)

    def show_analysis_dashboard(self, parent_dialog):
        # DÜZELTME: Yeni pencereyi 'self' yerine 'parent_dialog' üzerine açıyoruz
        analysis_win = tk.Toplevel(parent_dialog)
        analysis_win.title("Güvenlik ve Analiz Raporu")
        analysis_win.geometry("400x400")
        analysis_win.configure(bg="#ffffff")
        
        # Yeni açılan pencereye odaklan
        analysis_win.focus()
        
        # Orijinal ve Stego matrislerini hazırla
        original_matrix = pvd_utils.load_image_as_matrix(self.controller.cover_image_path)
        stego_matrix = np.array(self.controller.stego_result_img.convert('RGB'))
        
        # Metrikleri Hesapla
        mse_val = security.mse(original_matrix, stego_matrix)
        psnr_val = security.psnr(original_matrix, stego_matrix)
        ssim_val = visualization.compute_ssim(original_matrix, stego_matrix)
        
        tk.Label(analysis_win, text="İstatistiksel Metrikler", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=15)
        tk.Label(analysis_win, text=f"Mean Squared Error (MSE): {mse_val:.4f}", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(analysis_win, text=f"PSNR (Gürültü Oranı): {psnr_val:.2f} dB", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(analysis_win, text=f"SSIM (Yapısal Benzerlik): {ssim_val:.4f}", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        
        tk.Label(analysis_win, text="Görsel Analiz Araçları", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=(20, 10))
        
        # Visualization Butonları
        tk.Button(analysis_win, text="Fark Haritasını Göster", width=25,
                  command=lambda: visualization.show_difference(original_matrix, stego_matrix)).pack(pady=5)
        tk.Button(analysis_win, text="Histogramları Karşılaştır", width=25,
                  command=lambda: visualization.show_histogram(original_matrix, stego_matrix)).pack(pady=5)
        tk.Button(analysis_win, text="Isı Haritası (Heatmap)", width=25,
                  command=lambda: visualization.show_heatmap(original_matrix, stego_matrix)).pack(pady=5)

    def save_and_close(self, dialog):
        save_path = filedialog.asksaveasfilename(
            parent=dialog, 
            defaultextension=".png", 
            filetypes=[("PNG Files", "*.png")], 
            initialfile="stego_output.png"
        )
        if save_path:
            self.controller.stego_result_img.save(save_path)
            dialog.destroy()
            self.controller.update_status("Sonuç görseli kaydedildi.")


class ImageEncodePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        self.secret_image_path = None  
        
        self.title = tk.Label(self, text="Görsel İçine Görsel Gizleme", font=("Arial", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title.pack(anchor="w", pady=(0, 20))
        
        self.images_frame = tk.Frame(self, bg="#f4f6f7")
        self.images_frame.pack(fill="x", pady=10)
        
        self.cover_frame = tk.Frame(self.images_frame, bg="#f4f6f7")
        self.cover_frame.pack(side="left", padx=(0, 20))
        
        self.btn_select_cover = tk.Button(self.cover_frame, text="Kapak Görseli Seç", font=("Arial", 11, "bold"), bg="#3498db", fg="white",
                                          relief="flat", width=20, height=2, command=self.select_cover)
        self.btn_select_cover.pack(pady=(0, 10))
        
        self.cover_preview_frame = tk.Frame(self.cover_frame, width=240, height=180, bg="#bdc3c7")
        self.cover_preview_frame.pack()
        self.cover_preview_frame.pack_propagate(False)
        
        self.lbl_cover_preview = tk.Label(self.cover_preview_frame, text="Kapak Görseli\nBekleniyor...", bg="#bdc3c7", fg="#7f8c8d")
        self.lbl_cover_preview.pack(expand=True)
        
        self.secret_frame = tk.Frame(self.images_frame, bg="#f4f6f7")
        self.secret_frame.pack(side="left")
        
        self.btn_select_secret = tk.Button(self.secret_frame, text="Gizlenecek Görseli Seç", font=("Arial", 11, "bold"), bg="#3498db", fg="white",
                                           relief="flat", width=22, height=2, command=self.select_secret)
        self.btn_select_secret.pack(pady=(0, 10))
        
        self.secret_preview_frame = tk.Frame(self.secret_frame, width=240, height=180, bg="#bdc3c7")
        self.secret_preview_frame.pack()
        self.secret_preview_frame.pack_propagate(False)
        
        self.lbl_secret_preview = tk.Label(self.secret_preview_frame, text="Gizlenecek Görsel\nBekleniyor...", bg="#bdc3c7", fg="#7f8c8d")
        self.lbl_secret_preview.pack(expand=True)
        
        self.btn_process = tk.Button(self, text="Gizleme İşlemini Başlat", font=("Arial", 14, "bold"), bg="#27ae60", fg="white",
                                     relief="flat", width=25, height=2, command=self.process)
        self.btn_process.pack(anchor="w", pady=30)

    def select_cover(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*")])
        if file_path:
            self.controller.cover_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((240, 180), Image.Resampling.LANCZOS)
            my_image = ImageTk.PhotoImage(img)
            self.lbl_cover_preview.image = my_image
            self.lbl_cover_preview.configure(image=my_image, text="") 

    def select_secret(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*")])
        if file_path:
            self.secret_image_path = file_path
            img = Image.open(file_path)
            img = img.resize((240, 180), Image.Resampling.LANCZOS)
            my_image = ImageTk.PhotoImage(img)
            self.lbl_secret_preview.image = my_image
            self.lbl_secret_preview.configure(image=my_image, text="")

    def process(self):
        if not self.controller.cover_image_path:
            messagebox.showwarning("Uyarı", "Lütfen bir kapak görseli seçin!")
            return
        if not self.secret_image_path:
            messagebox.showwarning("Uyarı", "Lütfen gizlenecek görseli seçin!")
            return
        
        self.controller.update_status("Matrisler hesaplanıyor ve şifreleniyor...")
        try:
            pixel_matrix = pvd_utils.load_image_as_matrix(self.controller.cover_image_path)
            
            # HATA DÜZELTİLDİ: key parametresi kaldırıldı.
            binary_message = pvd_encoder.image_to_bits(self.secret_image_path)
            
            self.controller.stego_result_img = pvd_encoder.encode(pixel_matrix, binary_message)
            self.show_result_window()
            self.controller.update_status("Görsel başarıyla şifrelenip gizlendi.")
            
        except Exception as e:
            messagebox.showerror("İşlem Hatası", f"Görsel gizlenirken bir hata oluştu:\n{str(e)}")
            self.controller.update_status("İşlem başarısız oldu.")

    def show_result_window(self):
        dialog = tk.Toplevel(self)
        dialog.title("İşlem Başarılı")
        dialog.geometry("400x550")
        dialog.configure(bg="#f4f6f7")
        
        # DÜZELTME: grab_set() ve transient() kaldırıldı, böylece pencereler kilitlenmeyecek
        dialog.focus()
        
        tk.Label(dialog, text="Veri Başarıyla Gizlendi!", font=("Arial", 16, "bold"), bg="#f4f6f7", fg="#2ecc71").pack(pady=15)
        
        img = self.controller.stego_result_img.copy()
        img.thumbnail((300, 250)) 
        my_image = ImageTk.PhotoImage(img)
        
        label = tk.Label(dialog, image=my_image, bg="#f4f6f7")
        label.image = my_image 
        label.pack(pady=10)
        
        # DÜZELTME: show_analysis_dashboard fonksiyonuna 'dialog' değişkenini ebeveyn olarak gönderiyoruz
        tk.Button(dialog, text="Analiz Sonuçlarını Gör", bg="#9b59b6", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2,
                  command=lambda: self.show_analysis_dashboard(dialog)).pack(pady=5)
                  
        tk.Button(dialog, text="Görseli Kaydet", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), relief="flat", width=20, height=2,
                  command=lambda: self.save_and_close(dialog)).pack(pady=5)

    def show_analysis_dashboard(self, parent_dialog):
        # DÜZELTME: Yeni pencereyi 'self' yerine 'parent_dialog' üzerine açıyoruz
        analysis_win = tk.Toplevel(parent_dialog)
        analysis_win.title("Güvenlik ve Analiz Raporu")
        analysis_win.geometry("400x400")
        analysis_win.configure(bg="#ffffff")
        
        # Yeni açılan pencereye odaklan
        analysis_win.focus()
        
        # Orijinal ve Stego matrislerini hazırla
        original_matrix = pvd_utils.load_image_as_matrix(self.controller.cover_image_path)
        stego_matrix = np.array(self.controller.stego_result_img.convert('RGB'))
        
        # Metrikleri Hesapla
        mse_val = security.mse(original_matrix, stego_matrix)
        psnr_val = security.psnr(original_matrix, stego_matrix)
        ssim_val = visualization.compute_ssim(original_matrix, stego_matrix)
        
        tk.Label(analysis_win, text="İstatistiksel Metrikler", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=15)
        tk.Label(analysis_win, text=f"Mean Squared Error (MSE): {mse_val:.4f}", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(analysis_win, text=f"PSNR (Gürültü Oranı): {psnr_val:.2f} dB", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(analysis_win, text=f"SSIM (Yapısal Benzerlik): {ssim_val:.4f}", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        
        tk.Label(analysis_win, text="Görsel Analiz Araçları", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=(20, 10))
        
        # Visualization Butonları
        tk.Button(analysis_win, text="Fark Haritasını Göster", width=25,
                  command=lambda: visualization.show_difference(original_matrix, stego_matrix)).pack(pady=5)
        tk.Button(analysis_win, text="Histogramları Karşılaştır", width=25,
                  command=lambda: visualization.show_histogram(original_matrix, stego_matrix)).pack(pady=5)
        tk.Button(analysis_win, text="Isı Haritası (Heatmap)", width=25,
                  command=lambda: visualization.show_heatmap(original_matrix, stego_matrix)).pack(pady=5)

    def save_and_close(self, dialog):
        save_path = filedialog.asksaveasfilename(
            parent=dialog,
            defaultextension=".png", 
            filetypes=[("PNG Files", "*.png")], 
            initialfile="stego_image_output.png"
        )
        if save_path:
            self.controller.stego_result_img.save(save_path)
            dialog.destroy()


class DecodePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6f7")
        self.controller = controller
        
        self.title = tk.Label(self, text="Veri Doğrulama (Decoder)", font=("Arial", 24, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.title.pack(anchor="w", pady=(0, 30))
        
        self.btn_select = tk.Button(self, text="Steganography Görseli Seç", font=("Arial", 12, "bold"), bg="#3498db", fg="white",
                                    relief="flat", width=25, height=2, command=self.select_stego)
        self.btn_select.pack(anchor="w", pady=10)
        
        self.lbl_file = tk.Label(self, text="Seçilen: Yok", bg="#f4f6f7", fg="#7f8c8d")
        self.lbl_file.pack(anchor="w", pady=5)
        
        self.btn_process = tk.Button(self, text="Veriyi Çıkar", font=("Arial", 14, "bold"), bg="#f39c12", fg="white",
                                     relief="flat", width=25, height=2, command=self.process_decode)
        self.btn_process.pack(anchor="w", pady=25)
        
        self.lbl_out = tk.Label(self, text="Çıkarılan Sonuç:", font=("Arial", 14, "bold"), bg="#f4f6f7", fg="#2c3e50")
        self.lbl_out.pack(anchor="w", pady=(10, 5))
        
        self.text_output = tk.Text(self, height=8, width=60, font=("Arial", 12))
        self.text_output.pack(anchor="w")

    def select_stego(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png")])
        if file_path:
            self.controller.cover_image_path = file_path
            self.lbl_file.configure(text=f"Seçilen: {os.path.basename(file_path)}")

    def process_decode(self):
        if not self.controller.cover_image_path:
            messagebox.showwarning("Uyarı", "Lütfen stego görseli seçin!")
            return
            
        self.controller.update_status("Veri çıkarılıyor...")
    
        try:
            pixel_matrix = pvd_utils.load_image_as_matrix(self.controller.cover_image_path)
            
            # HATA DÜZELTİLDİ: key parametresi kaldırıldı.
            extracted_data = pvd_decoder.decode(pixel_matrix)
            
            if isinstance(extracted_data, dict):
                if extracted_data["type"] == "text":
                    self.text_output.delete("1.0", "end")
                    self.text_output.insert("end", extracted_data["data"])
                    self.controller.update_status("Gizli metin başarıyla çıkarıldı.")
                
                elif extracted_data["type"] == "image":
                    self.text_output.delete("1.0", "end")
                    self.text_output.insert("end", "[SİSTEM]: Gizli bir görsel bulundu!\nLütfen açılan pencereden görseli kaydedin.")
                    
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".png", 
                        filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")], 
                        initialfile="cikarilan_gizli_gorsel.png"
                    )
                    
                    if save_path:
                        with open(save_path, "wb") as f:
                            f.write(extracted_data["data"])
                        messagebox.showinfo("Başarılı", "Gizli görsel başarıyla kaydedildi!")
                    else:
                        self.controller.update_status("Gizli görseli kaydetme işlemi iptal edildi.")
                else:
                    self.text_output.delete("1.0", "end")
                    self.text_output.insert("end", "Veri türü anlaşılamadı veya dosya bozuk.")
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Veri çıkarılırken bir hata oluştu:\n{str(e)}")
            self.controller.update_status("Veri çıkarma işlemi başarısız.")