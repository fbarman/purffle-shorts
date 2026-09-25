# Factory Shorts — Kurulumsuz Windows sürümü

`Factory Shorts.exe` dosyasını çift tıklayın. Python, Ollama veya ses modeli kurmanız gerekmez: hepsi bu klasörde bulunur. Windows 10/11 x64 ve Microsoft Edge gerekir. Klasörü bütün olarak taşıyın; yalnızca EXE'yi taşımayın. Modeller nedeniyle birkaç GB yer kaplar.

- Açılışta Google Trends Türkiye konuları listelenir ve sırayla konu başına 3 video üretilir. Liste 15 dakikada bir yenilenir; daha önce seçilmiş aynı tarihli konu yeniden kuyruğa alınmaz. Popülerlik kaynağı Google arama ilgisidir, YouTube izlenme sıralaması değildir.
- **Otomatik üretimi duraklat** yeni otomatik işleri durdurur. Başlamış video tamamlanır. Pencereyi kapatırsanız uygulama kapanır; devam eden video yarım kalabilir. Bitmiş dosyalar korunur. Yarım işler yeniden açılışta sürdürülmez.
- Kendi konunuzu yazıp 1–3 video seçebilirsiniz. Görsel/video kutusundan sürükleyerek veya seçerek en fazla 10 referans yükleyin (her biri en fazla 100 MB). Dosyalar yalnızca bu konu grubunda kullanılır; otomatik konulara karışmaz.
- Referans yüklemezseniz Ollama sahne çizimlerini tasarlar, uygulama en fazla 3 illüstrasyonu yerel olarak oluşturur ve sahnelere dağıtır. Bunlar geometrik çizimlerdir; fotogerçekçi görüntü veya üretken video değildir.
- Arka plan müziği konuya göre yerel olarak sentezlenir. Hazır şarkı, melodi kaydı veya ses örneği içermez; müzik için servis ücreti veya telif bedeli yoktur. Sakin, merak, enerjik, sinematik veya kapalı seçilebilir. Konuşma sırasında otomatik kısılır.
- Aşama paneli senaryo, Türkçe ses, görseller, altyazı, müzik ve video birleştirmeyi gösterir. Hata olursa otomatik üretim duraklar; hata panelde görünür.
- Videolar `output_videos` içinde; çalışma kayıtları `data/factory.log` içindedir. Referanslar `data/references` içinde saklanır. Uygulama video yayınlamaz.

İnternet yalnızca güncel popüler konu listesini almak için gerekir. Senaryo, ses, çizim, müzik ve video oluşturma bilgisayarda yapılır. İnternet yoksa kendi konunuzla üretim yapabilirsiniz. Güncel olayların doğruluğunu küçük yerel model garanti etmez; yayın öncesi senaryoyu ve görselleri kontrol edin. Süre ve altyazı zamanları yaklaşıktır.

## Lisanslar

Uygulama MIT (`LICENSE.txt`). Ollama MIT, Qwen3 Apache-2.0; Supertonic 3 ses modeli OpenRAIL-M koşullarıyla kullanılabilir (`models/supertonic-3/LICENSE`). Ticari kullanım bu koşullara tabidir. Yapay zekâ ses bildirimi videoda ve açıklamada korunur. Sağladığınız logo ve referansların hakları size aittir; uygulama bunlara yeni bir lisans vermez. Sentezlenen müzik hazır eser kopyalamaz; platformlardaki otomatik hak iddialarının hiç oluşmayacağı garanti edilemez.

Kaynak kod: https://github.com/fbarman/purffle-shorts/pull/1
