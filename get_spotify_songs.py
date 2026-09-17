import os
import subprocess
import json
import sys

def main():
    print("=== Spotify Çalma Listesi İndirici ===")
    spotify_url = input("Lütfen Spotify çalma listesi linkini yapıştırın: ").strip()
    
    if not spotify_url:
        print("Link boş olamaz!")
        return
        
    print("\nSpotify'dan şarkı listesi çekiliyor (Bu işlem listenin uzunluğuna göre biraz sürebilir)...")
    
    temp_file = "temp_songs.spotdl"
    
    # Eski temp dosyası varsa sil
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    # spotdl komutunu çalıştır
    try:
        result = subprocess.run(
            ["spotdl", "save", spotify_url, "--save-file", temp_file],
            capture_output=True,
            text=True
        )
    except FileNotFoundError:
        print("HATA: 'spotdl' yüklü değil veya bulunamadı. Lütfen terminalde 'pip install spotdl' komutunu çalıştırarak yükleyin.")
        return
        
    if not os.path.exists(temp_file):
        print("HATA: Şarkı listesi çekilemedi.")
        if result.stderr:
            print("Detay:", result.stderr)
        return
        
    print("Liste başarıyla indirildi. Şarkı isimleri ayıklanıyor...")
    
    # JSON dosyasını oku ve songs.txt'ye yaz
    try:
        with open(temp_file, "r", encoding="utf-8") as f:
            songs_data = json.load(f)
            
        with open("songs.txt", "w", encoding="utf-8") as out:
            count = 0
            for song in songs_data:
                # Sanatçıları virgülle birleştir
                artists = ", ".join(song.get("artists", []))
                title = song.get("name", "")
                
                if artists and title:
                    line = f"{title} {artists}\n"
                    out.write(line)
                    count += 1
                    
        print(f"\nBaşarılı! Toplam {count} şarkı 'songs.txt' dosyasına kaydedildi.")
        print("Artık 'python spotify_to_ytm.py' veya 'python update_ytm_playlist.py' çalıştırarak YouTube Music'e aktarabilirsiniz.")
        
    except Exception as e:
        print(f"Dosya işlenirken hata oluştu: {e}")
        
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    main()
