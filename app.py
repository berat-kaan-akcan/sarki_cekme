import customtkinter as ctk
import os
import subprocess
import json
import threading
import time
import sys
import tkinter.messagebox as messagebox
from ytmusicapi import YTMusic

# --- Arayüz Ayarları ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Spotify to YouTube Music Aktarıcı")
        self.geometry("600x650")
        self.resizable(False, False)
        
        self.yt = None
        self.playlists = []
        
        # --- UI Elemanları ---
        
        # 1. Spotify Bölümü
        self.frame_spotify = ctk.CTkFrame(self)
        self.frame_spotify.pack(pady=10, padx=20, fill="x")
        
        self.lbl_spotify = ctk.CTkLabel(self.frame_spotify, text="1. Spotify Çalma Listesi Linki:", font=ctk.CTkFont(weight="bold"))
        self.lbl_spotify.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.entry_spotify = ctk.CTkEntry(self.frame_spotify, placeholder_text="https://open.spotify.com/playlist/...", width=400)
        self.entry_spotify.pack(pady=5, padx=10, side="left", expand=True, fill="x")
        
        self.btn_fetch = ctk.CTkButton(self.frame_spotify, text="Şarkıları Çek", command=self.fetch_songs_thread, width=120)
        self.btn_fetch.pack(pady=5, padx=10, side="right")
        
        # 2. YouTube Music Seçenekleri Bölümü
        self.frame_ytm = ctk.CTkFrame(self)
        self.frame_ytm.pack(pady=10, padx=20, fill="x")
        
        self.lbl_ytm = ctk.CTkLabel(self.frame_ytm, text="2. YouTube Music Aktarım Seçeneği:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ytm.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.radio_var = ctk.IntVar(value=0)
        
        # Yeni Liste Seçeneği
        self.radio_new = ctk.CTkRadioButton(self.frame_ytm, text="Yeni Liste Oluştur", variable=self.radio_var, value=0, command=self.toggle_options)
        self.radio_new.pack(pady=5, padx=10, anchor="w")
        
        self.entry_new_name = ctk.CTkEntry(self.frame_ytm, placeholder_text="Yeni Liste Adı", width=300)
        self.entry_new_name.pack(pady=5, padx=30, anchor="w")
        self.entry_new_name.insert(0, "Spotify'dan Aktarılan Liste")
        
        # Mevcut Liste Seçeneği
        self.radio_exist = ctk.CTkRadioButton(self.frame_ytm, text="Mevcut Listeye Ekle", variable=self.radio_var, value=1, command=self.toggle_options)
        self.radio_exist.pack(pady=5, padx=10, anchor="w")
        
        self.combo_playlists = ctk.CTkComboBox(self.frame_ytm, values=["Lütfen bekleyin, listeler yükleniyor..."], width=300)
        self.combo_playlists.pack(pady=5, padx=30, anchor="w")
        self.combo_playlists.configure(state="disabled")
        
        # 3. Aktarım Butonu
        self.btn_transfer = ctk.CTkButton(
            self, 
            text="▶ YOUTUBE MUSIC'E AKTAR", 
            command=self.transfer_thread, 
            height=45, 
            font=ctk.CTkFont(weight="bold", size=15), 
            fg_color="#FF0000", 
            hover_color="#CC0000"
        )
        self.btn_transfer.pack(pady=15, padx=20, fill="x")
        
        # 4. Log Konsolu (İşlem Durumu)
        self.frame_log = ctk.CTkFrame(self)
        self.frame_log.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.lbl_log = ctk.CTkLabel(self.frame_log, text="İşlem Durumu (Log):", font=ctk.CTkFont(weight="bold"))
        self.lbl_log.pack(pady=(10,0), padx=10, anchor="w")
        
        self.textbox = ctk.CTkTextbox(self.frame_log, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        # İlk Başlatma Ayarları
        self.toggle_options()
        self.log("Uygulama başlatıldı. YouTube Music bağlantısı arka planda kontrol ediliyor...")
        
        # YouTube API bağlantısını arayüzü dondurmamak için arka planda başlat
        threading.Thread(target=self.init_ytm, daemon=True).start()

    # Log kutusuna yazı yazdırma
    def log(self, message):
        self.after(0, self._log_gui, message)
        
    def _log_gui(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def show_error(self, title, message):
        self.log(f"HATA: {message}")
        self.after(0, lambda: messagebox.showerror(title, message))

    def show_info(self, title, message):
        self.log(message)
        self.after(0, lambda: messagebox.showinfo(title, message))

    def show_warning(self, title, message):
        self.log(f"UYARI: {message}")
        self.after(0, lambda: messagebox.showwarning(title, message))
        
    # Yeni / Mevcut liste seçeneklerini açıp kapatma
    def toggle_options(self):
        if self.radio_var.get() == 0:
            self.entry_new_name.configure(state="normal")
            self.combo_playlists.configure(state="disabled")
        else:
            self.entry_new_name.configure(state="disabled")
            self.combo_playlists.configure(state="normal")

    # YouTube Music Bağlantısı
    def init_ytm(self):
        auth_file = "headers_auth.json"
        
        # Eğer headers.txt varsa otomatik olarak JSON'a çevir (setup_ytm.py işlevi)
        if os.path.exists("headers.txt") and not os.path.exists(auth_file):
            self.log("headers.txt bulundu, giriş dosyası oluşturuluyor...")
            try:
                import ytmusicapi
                import utils
                headers_raw = utils.get_raw_headers("headers.txt")
                ytmusicapi.setup(filepath=auth_file, headers_raw=headers_raw)
                self.log("Giriş dosyası başarıyla oluşturuldu!\n")
            except Exception as e:
                self.show_error("Bağlantı Hatası", f"headers.txt JSON'a dönüştürülemedi.\nLütfen çerezleri doğru kopyaladığınızdan emin olun.\nDetay: {e}")
                return
                
        if not os.path.exists(auth_file):
            self.show_warning("Giriş Yapılmadı", "YouTube Music hesabınıza bağlanmak için çerezler (headers.txt) bulunamadı.\nLütfen 1. Adımdaki talimatları izleyerek headers.txt dosyasını doldurun ve uygulamayı yeniden başlatın.")
            return
            
        try:
            self.yt = YTMusic(auth_file)
            self.log("YouTube Music hesabına başarıyla bağlanıldı.")
            self.fetch_playlists()
        except Exception as e:
            self.show_error("Bağlantı Hatası", f"YouTube Music'e bağlanılamadı. Çerezlerinizin süresi dolmuş olabilir.\nDetay: {e}")
            
    # Kullanıcının mevcut listelerini çekme
    def fetch_playlists(self):
        if not self.yt: return
        try:
            self.playlists = self.yt.get_library_playlists(limit=50)
            playlist_names = [f"{pl.get('title', 'İsimsiz')} ({pl.get('count', '?')} şarkı)" for pl in self.playlists]
            if playlist_names:
                self.after(0, self._update_combo, playlist_names, playlist_names[0])
            else:
                self.after(0, self._update_combo, ["Hesabınızda liste bulunamadı"], "Hesabınızda liste bulunamadı")
        except Exception as e:
            self.log(f"Çalma listeleri çekilirken hata oluştu: {e}")

    def _update_combo(self, values, set_val):
        self.combo_playlists.configure(values=values)
        self.combo_playlists.set(set_val)

    # Şarkı Çekme İşlemi (Arayüz donmaması için Thread içinde)
    def fetch_songs_thread(self):
        threading.Thread(target=self.fetch_songs, daemon=True).start()
        
    def fetch_songs(self):
        url = self.entry_spotify.get().strip()
        if not url:
            self.show_warning("Eksik Bilgi", "Lütfen Spotify çalma listesi linki girin!")
            return
            
        if "spotify.com" not in url and "spotify.link" not in url:
            self.show_error("Geçersiz Link", "Lütfen geçerli bir Spotify linki girin!\nÖrnek: https://open.spotify.com/playlist/...")
            return
            
        self.btn_fetch.configure(state="disabled")
        self.log(f"\n[1/2] Spotify'dan şarkılar indiriliyor... (Bu biraz sürebilir)")
        
        temp_file = "temp_songs.spotdl"
        if os.path.exists(temp_file): 
            os.remove(temp_file)
        
        # CMD penceresinin açılmasını engellemek için (Windows)
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW
            
        try:
            # spotdl komutunu çalıştır
            result = subprocess.run(
                ["spotdl", "save", url, "--save-file", temp_file], 
                capture_output=True, text=True, encoding="utf-8", 
                creationflags=creationflags
            )
            
            if not os.path.exists(temp_file):
                err_detail = result.stderr if result.stderr else "Bilinmeyen Hata"
                self.show_error("İndirme Hatası", f"Şarkı listesi çekilemedi. Linki kontrol edin veya gizli liste olmadığından emin olun.\nDetay: {err_detail}")
                self.after(0, lambda: self.btn_fetch.configure(state="normal"))
                return
                
            # JSON'u oku ve txt dosyasına yaz
            with open(temp_file, "r", encoding="utf-8") as f:
                songs_data = json.load(f)
                
            with open("songs.txt", "w", encoding="utf-8") as out:
                count = 0
                for song in songs_data:
                    artists = ", ".join(song.get("artists", []))
                    title = song.get("name", "")
                    if artists and title:
                        out.write(f"{title} {artists}\n")
                        count += 1
                        
            self.show_info("İşlem Başarılı", f"Toplam {count} şarkı başarıyla çekildi!\nŞimdi 2. Adıma (YouTube'a Aktar) geçebilirsiniz.")
            
        except FileNotFoundError:
            self.show_error("Eksik Bileşen", "'spotdl' bilgisayarınızda yüklü değil.\nLütfen terminali açıp 'pip install spotdl' komutunu çalıştırın.")
        except json.JSONDecodeError:
            self.show_error("Veri Hatası", "Spotify linki işlenemedi (Bozuk Veri).\nLinkin doğru olduğundan ve listenin herkese açık (public) olduğundan emin olun.")
        except Exception as e:
            self.show_error("Beklenmeyen Hata", f"Şarkılar çekilirken beklenmeyen bir hata oluştu:\n{e}")
        finally:
            if os.path.exists(temp_file): 
                os.remove(temp_file)
            self.after(0, lambda: self.btn_fetch.configure(state="normal"))

    # YouTube Music'e Aktarma İşlemi (Thread içinde)
    def transfer_thread(self):
        threading.Thread(target=self.transfer_songs, daemon=True).start()
        
    def transfer_songs(self):
        if not self.yt:
            self.show_warning("Bağlantı Yok", "YouTube Music hesabınıza henüz bağlanılamadı.\nLütfen çerezlerinizi kontrol edip uygulamayı yeniden başlatın.")
            return
            
        if not os.path.exists("songs.txt"):
            self.show_warning("Şarkı Yok", "Aktarılacak şarkı bulunamadı.\nLütfen önce 1. Adımı (Şarkıları Çek) tamamlayın.")
            return
            
        with open("songs.txt", "r", encoding="utf-8") as f:
            songs = [line.strip() for line in f if line.strip()]
            
        if not songs:
            self.show_warning("Boş Liste", "Şarkı listesi boş!\nSpotify linkini kontrol edip şarkıları tekrar çekmeyi deneyin.")
            return
            
        self.btn_transfer.configure(state="disabled")
        
        is_new = self.radio_var.get() == 0
        playlist_id = None
        
        if is_new:
            name = self.entry_new_name.get().strip() or "Spotify'dan Aktarılan Liste"
            self.log(f"\n[2/2] YTM'de yeni liste oluşturuluyor: {name}")
            try:
                playlist_id = self.yt.create_playlist(name, "Spotify'dan aktarıldı.")
                self.log(f"Liste oluşturuldu.")
            except Exception as e:
                self.show_error("Liste Oluşturulamadı", f"YouTube'da yeni liste oluşturulurken hata yaşandı:\n{e}")
                self.after(0, lambda: self.btn_transfer.configure(state="normal"))
                return
        else:
            selected_str = self.combo_playlists.get()
            if selected_str not in self.combo_playlists._values or "bulunamadı" in selected_str or "yükleniyor" in selected_str:
                self.show_error("Geçersiz Seçim", "Lütfen mevcut çalma listelerinizden geçerli birini seçin.")
                self.after(0, lambda: self.btn_transfer.configure(state="normal"))
                return
                
            selected_idx = self.combo_playlists._values.index(selected_str)
            playlist_id = self.playlists[selected_idx]['playlistId']
            self.log(f"\n[2/2] YTM'deki mevcut listeye ekleniyor: {selected_str}")

        self.log(f"Toplam {len(songs)} şarkı YouTube'da aranıp ekleniyor...")
        video_ids = []
        for song in songs:
            try:
                res = self.yt.search(song, filter="songs")
                if res:
                    video_ids.append(res[0]['videoId'])
                    self.log(f" [+] Bulundu: {song}")
                else:
                    self.log(f" [-] BULUNAMADI: {song}")
            except Exception as e:
                self.log(f" [!] Hata ({song}): {e}")
                
            # Arayüzün güncellenmesine izin ver ve API'yi yorma
            time.sleep(0.1) 
            
        if video_ids:
            self.log(f"\nBulunan {len(video_ids)} şarkı YouTube Music'e aktarılıyor...")
            chunk_size = 50
            for i in range(0, len(video_ids), chunk_size):
                chunk = video_ids[i:i + chunk_size]
                try:
                    self.yt.add_playlist_items(playlist_id, chunk, duplicates=True)
                except Exception as e:
                    self.log(f"Ekleme sırasında hata (chunk): {e}")
            self.show_info("Aktarım Tamamlandı", f"İşlem tamamlandı! 🎉\nBulunan {len(video_ids)} şarkı YouTube Music'e başarıyla aktarıldı.")
        else:
            self.show_warning("Sonuç Yok", "Aramada hiçbir şarkı bulunamadı.\nBölgesel kısıtlamalar veya şarkıların YouTube'da olmaması sebep olabilir.")
            
        self.after(0, lambda: self.btn_transfer.configure(state="normal"))

if __name__ == "__main__":
    app = App()
    app.mainloop()
