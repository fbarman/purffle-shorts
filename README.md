# PurffleShorts — Türkçe Video Fabrikası

Windows'ta **Ollama + Supertonic 3 + FFmpeg** ile Türkçe, sesli, altyazılı dikey videolar üretir. API anahtarı, abonelik ve video başına ödeme gerekmez. İlk indirmelerden sonra varsayılan üretim akışı bilgisayarda çalışır.

## Hızlı başlangıç

1. Bu sürümün ZIP dosyasını indirin ve yazılabilir bir klasöre çıkarın. ZIP içinden çalıştırmayın.
2. [Python 3.12 / Windows](https://www.python.org/downloads/windows/) kurulu olmalı. Kurulumda Python'u PATH'e ekleyin.
3. **KURULUM.cmd** dosyasını çift tıklayın. Ayrı Python ortamı, taşınabilir Ollama, qwen3:4b-instruct ve Supertonic 3 ses modeli hazırlanır. İlk kurulum internet gerektirir ve birkaç GB indirir.
4. **BASLAT.cmd** dosyasını açın. Panel http://127.0.0.1:8765 adresinde açılır.
5. Konu, hedef süre ve video sayısını seçin. **Üretim kuyruğuna ekle** düğmesine basın.
6. Panelden videoyu izleyin; MP4, altyazı, senaryo ve açıklamayı indirin.

**KONTROL.cmd**, model ve araçların durumunu gösterir. Otomatik YouTube yükleme kapalıdır. Panel açıkken konsol penceresini kapatmayın. Yeniden başlatmada bitmiş videolar korunur; bekleyen işler bellekte tutulur ve yeniden eklenmelidir.

## Neler üretir?

- Ollama ile Türkçe senaryo, başlık, açıklama ve etiketler.
- Supertonic 3 ile yerel Türkçe yapay zekâ seslendirmesi; hazır erkek/kadın sesleri.
- Yerel fotoğraf ve videolardan sahneler, yumuşak geçişler ve hareketli fotoğraflar.
- Medya yoksa hareketli renkli arka planlar. **Bu mod fotogerçekçi yapay zekâ görseli veya video klibi üretmez.**
- Videoya işlenmiş Türkçe altyazı, ayrıca SRT dosyası; i/ı/İ/I dönüşümleri desteklenir.
- 720×1280, 25 kare/saniye varsayılan MP4; 1080×1920 seçeneği.
- Bir istekte 1–20 video, sırayla üretim, en fazla 50 bekleyen iş.
- Tamamlanan videolar, kapak ve üretim geçmişi.

Hedef süre yaklaşık bir senaryo hedefidir; nihai uzunluk seslendirmeden hesaplanır. Yerel sesin **kelime zamanları tahminidir**, zorunlu hizalama değildir. Yayın öncesi telaffuz ve altyazıyı gözden geçirin.

## Görseller ve müzik

Kendi kullanım hakkınız olan fotoğraf/video dosyalarını **media/** klasörüne, müziği **music/** klasörüne koyun. Sahne seçimi dosya adındaki kelimelere bakar; örneğin octopus_deniz.jpg, space_uzay.mp4.

Desteklenen görseller: JPG, JPEG, PNG, WEBP; videolar: MP4, MOV, M4V, WEBM, MKV. Bir video içinde aynı dosya tekrar seçilmez. Yeterli dosya yoksa kalan sahneler renkli arka plan kullanır. Müzik yoksa yalnızca seslendirme kullanılır.

## Ayarlar

İlk kurulum **factory.local.json** oluşturur. Tekrar kurulum bu dosyanın üzerine yazmaz.

~~~json
{
  "llm_model": "qwen3:4b-instruct",
  "tts_engine": "supertonic",
  "tts_voice": "M1",
  "tts_model": "models/supertonic-3",
  "target_seconds": 40,
  "resolution": "720x1280",
  "channel_name": "Benim Kanalım",
  "caption_style": "bold",
  "niches": ["uzay ve gezegenler", "hayvanların ilginç özellikleri"]
}
~~~

Sesler: M1–M5 ve F1–F5; virgülle birden çok ses yazılırsa video başına rastgele seçilir. Ses hızı için "tts_rate": "+8%" kullanılabilir. 1080p için "resolution": "1080x1920" yapın.

16 GB RAM / GTX 1650 4 GB düzeyindeki bilgisayarlar için 4B model, 720p, sırayla üretim ve CPU seslendirme seçilmiştir. Ollama istek tamamlanınca GPU belleğini bırakır. Daha güçlü donanımda modeli değiştirebilirsiniz; önce o modeli yerel Ollama'ya indirin. Bulut modelleri fabrika modunda kabul edilmez.

Fabrika .env içindeki ücretli API ayarlarını ve sağlayıcı ortam değişkenlerini kullanmaz. Harici LLM, ücretli ses, uzaktan görsel, ücretli hizalama ve otomatik yükleme fabrika modunda engellenir. Ses üretimi başarısız olursa başka servise veya sessiz çıktıya otomatik geçmez.

## Dosyalar

~~~text
output_videos/
  tarih_baslik/
    short.mp4       — bitmiş video
    cover.jpg       — kapak
    captions.srt    — Türkçe altyazı
    script.json     — senaryo
    metadata.json   — başlık, açıklama, etiketler, kullanılan modeller
data/
  history.db       — üretim geçmişi
  logs/purffle.log — işlem günlüğü
models/            — Ollama ve Supertonic dosyaları
.tools/ollama/     — taşınabilir Ollama
~~~

Panel varsayılan olarak yalnızca bilgisayarınızdan erişilebilir. Oluşturma istekleri oturum anahtarıyla korunur. Açıklamaya ve videoya yapay zekâ seslendirmesi bildirimi eklenir.

## Komut satırı

Proje klasöründe PowerShell açın:

~~~powershell
.\.venv\Scripts\python.exe -m purffle_shorts.factory doctor
.\.venv\Scripts\python.exe -m purffle_shorts.factory make --topic "Ahtapotların üç kalbi" --count 3 --duration 40
.\.venv\Scripts\python.exe -m purffle_shorts.factory demo
.\.venv\Scripts\python.exe -m purffle_shorts.factory studio --port 8766
~~~

Demo, hazır Türkçe senaryoyu gerçek seslendirme ve video birleştirmeyle üretir; Ollama gerekmez, yerel ses modeli gerekir. Konulu üretim Ollama gerektirir. Konu boşsa seçilen kategoriyi daraltarak senaryoyu Ollama yazar.

Eski çok sağlayıcılı komutlar ileri kullanım için korunmuştur; ücretli servis koruması **fabrika giriş noktası** içindir. Eski python -m purffle_shorts make yerine python -m purffle_shorts.factory make kullanın. Önceki belgeler: [README.upstream.md](README.upstream.md).

## Ticari kullanım ve lisanslar

Bu sürüm, gelir elde edilen videolar için ticari olmayan kullanımla sınırlı Türkçe Piper/DFKI sesini kullanmaz. Varsayılan Supertonic 3 modeli **OpenRAIL-M**, SDK kodu **MIT** lisanslıdır. Model lisansı ücretli lisans istemez ve ticari kullanımı yasaklamaz; kullanım koşulları ve yapay zekâ üretimini açıklama yükümlülüğü geçerlidir. Model lisansı kurulumda models/supertonic-3/LICENSE dosyasına kaydedilir.

- [Supertonic 3 model lisansı](https://huggingface.co/supertone-oss-archive/supertonic-3/blob/aafc6e32416a594460b32413efc49d7fe4ce6d46/LICENSE)
- [Supertonic kaynak ve arşiv bilgisi](https://github.com/supertone-oss-archive/supertonic)
- [Qwen3 4B Instruct model ve lisansı](https://ollama.com/library/qwen3:4b-instruct)
- PurffleShorts kodu: [MIT](LICENSE). İndirilen araçlar ve modeller kendi lisanslarına tabidir.

Supertonic projesi Eylül 2026'da arşivlenmiştir; bu entegrasyon SDK ve modelin sabitlenmiş arşiv sürümlerini indirir, çalışma sırasında otomatik indirme/güncelleme yapmaz. Model dosyalarını saklayın.

Yazılım/API bedeli yoktur; bilgisayar, elektrik, depolama ve ilk indirmelerdeki internet kullanımı size aittir. Üretim, YouTube'da gelir elde etme garantisi değildir. Kullanılan müzik ve görüntülerin hakları ile yayınlanan bilgilerin doğruluğu ayrıca kontrol edilmelidir.

## Sorun giderme

- **Python bulunamadı:** Python 3.12 kurup kurulum dosyasını tekrar açın.
- **Ollama bağlantısı yok:** BASLAT.cmd kullanın. Günlük .tools/ollama-error.log dosyasındadır.
- **Model bulunamadı:** KURULUM.cmd'yi tekrar çalıştırın; model indirme kaldığı yerden devam edebilir.
- **Zaten kurulu Ollama:** 11434 portundaki mevcut sunucu kullanılır. Kurulum modeli o sunucuya indirir; iki sunucu aynı portta çalıştırılmaz.
- **Türkçe ses eksik:** KURULUM.cmd yerel ses dosyalarını yeniden tamamlar.
- **Belgeler klasörüne yazamıyor:** Projeyi yazma izniniz olan başka bir klasöre çıkarın. Güvenlik korumalarını kapatmanız gerekmez.
- **Bellek / hız:** 720p kullanın, başka GPU uygulamalarını kapatın. NVIDIA hızlandırmalı video için video_encoder ayarı h264_nvenc olabilir; varsayılan CPU kodlayıcı daha taşınabilirdir.
- **Port kullanımda:** Yukarıdaki --port 8766 komutunu kullanın.
- **Üretim kesildi:** Günlüğü kontrol edin; tamamlanan videolar kitaplıkta kalır. İş kuyruğu kalıcı değildir.

## Geliştirici doğrulaması

~~~powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,local]"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
~~~

Testler gerçek ücretli servis çağırmaz. Birim testlerine ek olarak çevrimdışı FFmpeg birleştirme, Türkçe karakterler, ücretli servis koruması, toplu kuyruk ve HTTP oturum doğrulaması sınanır.
