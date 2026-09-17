# Spotify to YouTube Music Çalma Listesi Aktarıcı

Bu proje, Spotify'daki çalma listelerinizi saniyeler içinde YouTube Music hesabınıza aktarmanızı sağlayan araçlardan oluşur. 

> [!IMPORTANT]
> YouTube'un son güncellemelerinden dolayı harici uygulamalarda (OAuth) "400 Bad Request" hatası alınmaktadır. Bu nedenle uygulama **tarayıcı çerezleri (headers.txt)** üzerinden çalışmaktadır.

---

## ⚙️ Ortak Kurulum ve Hazırlık (Zorunlu)

İster masaüstü uygulamasını ister komut satırını kullanın, önce YouTube Music hesabınıza bağlanmak için çerezleri (headers) kaydetmeniz gerekir.

**Nasıl Yapılır?**
1. Tarayıcınızdan [YouTube Music](https://music.youtube.com)'e girin (ve giriş yapmış olduğunuzdan emin olun).
2. F12 tuşuna basarak (veya Sağ Tık -> İncele) **Geliştirici Araçlarını** açın.
3. **Network (Ağ)** sekmesine geçin. Sayfayı yenileyin (F5).
4. Sol taraftaki isimlerden `browse` veya `next` gibi bir isteği bulup sağ tıklayın: `Copy` -> `Copy as cURL (bash)`.
5. Proje klasöründe **`headers.txt` adında yeni bir dosya oluşturun**.
6. Kopyaladığınız bu metnin içindeki (sadece `-H` ile başlayan) header kısımlarını oluşturduğunuz `headers.txt` dosyasının içine yapıştırın ve kaydedin. *(Not: Her iki kullanım yöntemi de bu dosyayı otomatik olarak okuyup JSON'a çevirecektir).*

Gerekli kütüphaneleri kurmak için:
```bash
pip install -r requirements.txt
```

---

## 🚀 Kullanım Yöntemi 1: Masaüstü Uygulaması (GUI - Önerilen)

Tüm işlemleri tek bir pencerede ve arka planda logları göreceğiniz şekilde yönetebilirsiniz.

**Çalıştırmak için:**
```bash
python app.py
```
- Spotify çalma listenizin linkini yapıştırıp **"Şarkıları Çek"** butonuna basın.
- Çekme işlemi bitince **Yeni Liste Oluştur** veya açılır menüden **Mevcut Listeye Ekle** seçeneğini seçin.
- Kırmızı **YouTube Music'e Aktar** butonuna basın.

---

## 💻 Kullanım Yöntemi 2: Komut Satırı (CLI)

Uygulamayı tamamen siyah ekrandan (terminal üzerinden) kullanmak isteyenler için:

### 1. Spotify'dan Şarkıları Çekme
Bu script, Spotify linkini alıp içindeki şarkıları otomatik olarak `songs.txt` dosyasına kaydeder.
```bash
python get_spotify_songs.py
```
*(Ekranda sorulduğunda Spotify listesinin linkini yapıştırıp Enter'a basın).*

### 2. Şarkıları YouTube Music'e Aktarma
`songs.txt` hazırlandıktan sonra, aktarımı yapmak için iki seçenekten birini seçin:

**Yeni bir çalma listesi oluşturarak aktarmak için:**
```bash
python spotify_to_ytm.py
```
*(Yeni listenin ismini kodun içindeki `YTM_PLAYLIST_NAME` değişkenini düzenleyerek belirleyebilirsiniz).*

**Şarkıları hesabınızdaki var olan mevcut bir listeye eklemek için:**
```bash
python update_ytm_playlist.py
```
*(Program size hesabınızdaki listeleri sıralayarak, hangi listeye eklemek istediğinizi rakamla soracaktır).*

---
## 📁 Projedeki Dosyalar

- `app.py`: Ana masaüstü arayüz uygulaması (GUI).
- `get_spotify_songs.py`: Spotify linkinden şarkıları indiren terminal scripti.
- `spotify_to_ytm.py`: Şarkıları yeni bir listeye ekleyen terminal scripti.
- `update_ytm_playlist.py`: Şarkıları mevcut listeye ekleyen terminal scripti.
- `headers.txt`: Tarayıcıdan kopyaladığınız çerezleri koyacağınız dosya. (Siz kaydettikten sonra sistem otomatik olarak `headers_auth.json`'a dönüştürür).
- `songs.txt`: Aktarılacak şarkıların listesini barındıran geçici metin dosyası.
