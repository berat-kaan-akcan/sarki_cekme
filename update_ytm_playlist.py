import os
import time
from ytmusicapi import YTMusic

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
    auth_file = "headers_auth.json"
    
    if os.path.exists("headers.txt") and not os.path.exists(auth_file):
        print("headers.txt bulundu, giriş dosyası (headers_auth.json) oluşturuluyor...")
        try:
            import ytmusicapi
            ytmusicapi.setup(filepath=auth_file, headers_raw=open("headers.txt", "r", encoding="utf-8").read())
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
        print(f"Giriş başarısız: {e}")
        return
        
    print("\nMevcut çalma listeleriniz getiriliyor...")
    try:
        playlists = yt.get_library_playlists(limit=50)
    except Exception as e:
        print(f"Çalma listeleri getirilirken hata oluştu: {e}")
        return
        
    if not playlists:
        print("Hesabınızda hiçbir çalma listesi bulunamadı.")
        return

    print("\nLütfen şarkıların ekleneceği çalma listesini seçin:")
    for i, pl in enumerate(playlists):
        title = pl.get('title', 'İsimsiz Liste')
        count = pl.get('count', 'Bilinmeyen')
        print(f"{i + 1}. {title} ({count} şarkı)")
        
    while True:
        try:
            choice = int(input(f"\nSeçiminiz (1-{len(playlists)}): "))
            if 1 <= choice <= len(playlists):
                selected_playlist = playlists[choice - 1]
                break
            else:
                print("Geçersiz bir numara girdiniz.")
        except ValueError:
            print("Lütfen geçerli bir sayı girin.")
            
    playlist_id = selected_playlist['playlistId']
    playlist_name = selected_playlist.get('title', 'İsimsiz Liste')
    
    print(f"\nŞarkılar '{playlist_name}' listesine eklenecek.")
    print(f"Toplam {len(songs)} şarkı aranıyor...")
    
    video_ids = []
    for song in songs:
        try:
            search_results = yt.search(song, filter="songs")
            if search_results:
                video_ids.append(search_results[0]['videoId'])
                print(f"[✓] Bulundu: {song}")
            else:
                print(f"[X] BULUNAMADI: {song}")
        except Exception as e:
            print(f"[!] Hata oluştu ({song}): {e}")
            
        time.sleep(0.1) # API'yi yormamak için kısa bekleme
            
    if not video_ids:
        print("\nHiçbir şarkı bulunamadığı için işlem iptal edildi.")
        return
        
    print(f"\nToplam {len(video_ids)} şarkı '{playlist_name}' listesine ekleniyor...")
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i + chunk_size]
        try:
            yt.add_playlist_items(playlist_id, chunk, duplicates=True)
            print(f"  {i+1}-{min(i+chunk_size, len(video_ids))} arası şarkılar eklendi.")
        except Exception as e:
            print(f"  Hata oluştu (şarkı ekleme sırasında): {e}")
            
    print("\nİşlem tamamlandı! Şarkılarınız mevcut YouTube Music listenize başarıyla eklendi.")

if __name__ == "__main__":
    main()
