import os
import time
from ytmusicapi import YTMusic

# YouTube Music Playlist Bilgileri
YTM_PLAYLIST_NAME = "Spotify'dan Aktarılan Liste"
YTM_PLAYLIST_DESC = "Bu liste ekran görüntülerinden okunarak YouTube Music'e aktarılmıştır."

def main():
    songs_file = "songs.txt"
    
    if not os.path.exists(songs_file):
        print(f"HATA: {songs_file} dosyası bulunamadı!")
        print("Lütfen önce şarkıların kaydedildiği dosyanın oluşturulduğundan emin olun.")
        return
        
    with open(songs_file, "r", encoding="utf-8") as f:
        songs = [line.strip() for line in f if line.strip()]
        
    if not songs:
        print("Şarkı listesi boş olduğu için işlem iptal edildi.")
        return
        
    print(f"Toplam {len(songs)} şarkı okunarak işleme başlanıyor...\n")
    
    # 2. YouTube Music'e bağlan
    auth_file = "headers_auth.json"
    
    if os.path.exists("headers.txt") and not os.path.exists(auth_file):
        print("headers.txt bulundu, giriş dosyası (headers_auth.json) oluşturuluyor...")
        try:
            import ytmusicapi
            import utils
            headers_raw = utils.get_raw_headers("headers.txt")
            ytmusicapi.setup(filepath=auth_file, headers_raw=headers_raw)
            print("Giriş dosyası başarıyla oluşturuldu!\n")
        except Exception as e:
            print(f"HATA: headers.txt dönüştürülemedi: {e}")
            return
            
    if not os.path.exists(auth_file):
        print(f"HATA: {auth_file} veya headers.txt dosyası bulunamadı!")
        print("Lütfen klasördeki 'headers.txt' dosyasına çerezleri yapıştırın ve uygulamayı tekrar çalıştırın.")
        return
        
    print("YouTube Music'e bağlanılıyor...")
    try:
        yt = YTMusic(auth_file)
    except Exception as e:
        print(f"HATA: YouTube Music'e bağlanırken hata oluştu: {e}")
        return
    
    # 3. YTM'de yeni liste oluştur
    print(f"\n'{YTM_PLAYLIST_NAME}' adında yeni bir liste oluşturuluyor...")
    playlist_id = yt.create_playlist(YTM_PLAYLIST_NAME, YTM_PLAYLIST_DESC)
    
    # 4. Şarkıları ara ve listeye ekle
    video_ids = []
    print("\nŞarkılar YouTube Music'te aranıyor...")
    for song in songs:
        try:
            # Sadece şarkıları (songs) aramak için filter="songs" kullanıyoruz
            search_results = yt.search(song, filter="songs")
            if search_results:
                video_ids.append(search_results[0]['videoId'])
                print(f"[✓] Bulundu: {song}")
            else:
                print(f"[X] BULUNAMADI: {song}")
        except Exception as e:
            print(f"[!] Hata oluştu ({song}): {e}")
            
        time.sleep(0.1) # API'yi yormamak için kısa bekleme
            
    # YTM API'si tek seferde çok fazla şarkı eklerken hata verebilir, 50'şerli gruplar halinde ekleyelim
    print(f"\nToplam {len(video_ids)} şarkı YouTube Music listesine ekleniyor...")
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        yt.add_playlist_items(playlist_id, chunk, duplicates=True)
        
    print("\nİşlem tamamlandı! Şarkılarınız YouTube Music'e başarıyla aktarıldı.")

if __name__ == "__main__":
    main()
