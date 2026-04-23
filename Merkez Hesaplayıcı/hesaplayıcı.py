import customtkinter as ctk
import json
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Arayüz Ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MerkezHesaplayici(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("A-Terminal v6.2 - Professional Edition")
        self.geometry("1100x700")
        
        self.gecmis_data = [] 
        self.animasyon_id = None
        
        # Hata engelleyici kapanış protokolü
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_ui()

    def setup_ui(self):
        # Grid Yapılandırması
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        # SOL: Giriş Paneli
        self.frame_giris = ctk.CTkFrame(self)
        self.frame_giris.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.frame_giris, text="Parametreler", font=("Arial", 16, "bold")).pack(pady=10)
        self.entry_l = ctk.CTkEntry(self.frame_giris, placeholder_text="Toplam Uzunluk (L)")
        self.entry_l.pack(pady=5, padx=10, fill="x")
        self.entry_x = ctk.CTkEntry(self.frame_giris, placeholder_text="Kesim Noktası (x)")
        self.entry_x.pack(pady=5, padx=10, fill="x")
        
        self.btn = ctk.CTkButton(self.frame_giris, text="Simülasyonu Başlat", command=self.baslat_simulasyon)
        self.btn.pack(pady=10)
        
        self.btn_sifirla = ctk.CTkButton(self.frame_giris, text="Sıfırla", fg_color="#f39c12", command=self.sifirla)
        self.btn_sifirla.pack(pady=5, padx=10, fill="x")
        
        self.btn_3d = ctk.CTkButton(self.frame_giris, text="❒ 3D İncele", fg_color="#e67e22", command=self.ac_3d_modu)
        self.btn_3d.pack(pady=10, padx=10, fill="x")

        self.btn_temizle = ctk.CTkButton(self.frame_giris, text="Geçmişi Temizle", fg_color="#c0392b", command=self.temizle_gecmis)
        self.btn_temizle.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(self.frame_giris, text="Veri Yönetimi", font=("Arial", 12)).pack(pady=(20, 5))
        self.btn_export = ctk.CTkButton(self.frame_giris, text="Dışa Aktar (.json)", fg_color="#27ae60", command=self.veri_disa_aktar)
        self.btn_export.pack(pady=5, padx=10, fill="x")
        self.btn_import = ctk.CTkButton(self.frame_giris, text="İçe Aktar (.json)", fg_color="#2980b9", command=self.veri_ice_aktar)
        self.btn_import.pack(pady=5, padx=10, fill="x")

        # ORTA: Görselleştirme
        self.canvas = ctk.CTkCanvas(self, height=250, bg="#2b2b2b", highlightthickness=0)
        self.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.frame_sonuc = ctk.CTkFrame(self, fg_color="#1a1a1a", border_width=2, border_color="#00FF00")
        self.frame_sonuc.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.lbl_sonuc = ctk.CTkLabel(self.frame_sonuc, text="MERKEZ KAYMASI: 0.00 cm", font=("Consolas", 20, "bold"), text_color="#00FF00")
        self.lbl_sonuc.pack(pady=10)
        
        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 14, "bold"), text_color="#00FF00")
        self.log_box.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        # SAĞ: Geçmiş Kayıtlar
        self.gecmis_frame = ctk.CTkScrollableFrame(self, label_text="Geçmiş (Tıkla ve Yükle)")
        self.gecmis_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")

    # --- İşlevler ---
    def on_closing(self):
        try:
            if self.animasyon_id: self.after_cancel(self.animasyon_id)
            # Tüm bekleyen callback'leri temizle (hata engelleyici)
            for task in self.tk.call('after', 'info'):
                try: self.after_cancel(task)
                except: pass
        except: pass
        finally:
            self.quit()
            self.destroy()

    def baslat_simulasyon(self):
        if self.animasyon_id: self.after_cancel(self.animasyon_id)
        try:
            L = float(self.entry_l.get()); x = float(self.entry_x.get())
            self.ciz(L, x)
            if {"L": L, "x": x} not in self.gecmis_data:
                self.gecmis_data.append({"L": L, "x": x})
                self.gecmis_guncelle()
            self.lbl_sonuc.configure(text=f"KAYMA: {abs(L/2 - x):.2f} cm")
            self.log_yaz(f"SİSTEM: L={L}, x={x} işlendi.")
        except: self.log_yaz("HATA: Sayısal giriş!")

    def ciz(self, L, x):
        self.canvas.delete("all")
        start_x, y_pos, bar_height, scale = 50, 100, 40, 300 / L 
        k_pos = start_x + (x * scale)
        end_pos = start_x + (L * scale)
        # Bloklar
        self.canvas.create_rectangle(start_x, y_pos, k_pos, y_pos + bar_height, fill="#3498db", outline="white")
        self.canvas.create_rectangle(k_pos + 40, y_pos, end_pos + 40, y_pos + bar_height, fill="#e74c3c", outline="white")
        # Ölçüler
        self.canvas.create_text((start_x + k_pos)/2, y_pos + 20, text=f"{x:.1f} cm", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_text(((k_pos + 40) + (end_pos + 40))/2, y_pos + 20, text=f"{L-x:.1f} cm", fill="white", font=("Arial", 12, "bold"))
        # Ayırıcı
        self.canvas.create_line(k_pos, y_pos - 10, k_pos, y_pos + bar_height + 10, fill="yellow", width=3)

    def yukle_gecmis(self, L, x):
        self.entry_l.delete(0, 'end'); self.entry_l.insert(0, str(L))
        self.entry_x.delete(0, 'end'); self.entry_x.insert(0, str(x))
        self.baslat_simulasyon()

    def gecmis_guncelle(self):
        for widget in self.gecmis_frame.winfo_children(): widget.destroy()
        for item in self.gecmis_data:
            btn = ctk.CTkButton(self.gecmis_frame, text=f"L: {item['L']} | x: {item['x']}", 
                                fg_color="#444444", command=lambda l=item['L'], x=item['x']: self.yukle_gecmis(l, x))
            btn.pack(pady=2, padx=5, fill="x")

    def sifirla(self):
        self.entry_l.delete(0, 'end'); self.entry_x.delete(0, 'end')
        self.canvas.delete("all"); self.lbl_sonuc.configure(text="MERKEZ KAYMASI: 0.00 cm")

    def ac_3d_modu(self):
        if not self.entry_l.get(): return
        L, x = float(self.entry_l.get()), float(self.entry_x.get())
        pencere = ctk.CTkToplevel(self)
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        ax.bar3d(0,0,0, x, 1, 1, color='#3498db', alpha=0.8)
        ax.bar3d(x + 0.5, 0, 0, L - x, 1, 1, color='#e74c3c', alpha=0.8)
        FigureCanvasTkAgg(fig, master=pencere).get_tk_widget().pack(fill="both", expand=True)

    def log_yaz(self, m): self.log_box.insert("end", f"> {m}\n"); self.log_box.see("end")
    def temizle_gecmis(self): 
        for widget in self.gecmis_frame.winfo_children(): widget.destroy()
        self.gecmis_data = []
    def veri_disa_aktar(self): 
        yol = filedialog.asksaveasfilename(defaultextension=".json")
        if yol: 
            with open(yol, "w", encoding="utf-8") as f: json.dump({"history": self.gecmis_data}, f)
            self.log_yaz("SİSTEM: Veriler dışa aktarıldı.")
    def veri_ice_aktar(self): 
        yol = filedialog.askopenfilename()
        if yol: 
            with open(yol, "r", encoding="utf-8") as f: 
                self.gecmis_data = json.load(f)["history"]
                self.gecmis_guncelle()
            self.log_yaz("SİSTEM: Veriler içe aktarıldı.")

if __name__ == "__main__":
    app = MerkezHesaplayici()
    app.mainloop()