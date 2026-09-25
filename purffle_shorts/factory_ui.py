"""Türkçe fabrika paneli."""
PAGE = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factory Shorts</title>
<style>
:root{color-scheme:dark;--bg:#090a0c;--card:#14161b;--line:#2b2e36;--muted:#acb1bf;--accent:#c4f086}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#f0f4fc;font:16px/1.5 "Segoe UI",sans-serif}
header{padding:26px 5%;border-bottom:1px solid var(--line)}h1{font-size:28px;margin:0}p{color:var(--muted);margin:8px 0}
main{max-width:1440px;padding:24px;margin:auto;display:grid;grid-template-columns:370px 1fr;gap:24px}
section{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;margin-bottom:20px}
h2{font-size:20px;margin:0 0 16px}label{display:block;margin:14px 0 6px}
input,select,textarea{width:100%;background:var(--bg);color:#fff;border:1px solid var(--line);border-radius:9px;padding:11px;font:inherit}
button,.download{border:0;border-radius:9px;padding:12px 16px;background:var(--accent);color:#142208;font:600 15px "Segoe UI";cursor:pointer;text-decoration:none;display:inline-block}
button:disabled{opacity:.5;cursor:wait}a{color:var(--accent)}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.small{font-size:13px;color:var(--muted)}.error{color:#ffacac}.ok{color:var(--accent)}#go{width:100%;margin-top:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px}.video{background:var(--bg);border-radius:12px;padding:12px}
video{width:100%;aspect-ratio:9/16;max-height:430px;background:#000;border-radius:8px}h3{font-size:16px}
.actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}.job{border-top:1px solid var(--line);padding:14px 0}
.drop{border:2px dashed #555e6d;padding:16px;border-radius:12px}.drop.over{border-color:var(--accent)}progress{width:100%;accent-color:var(--accent)}.trend{padding:10px 0;border-top:1px solid var(--line)}pre{white-space:pre-wrap;word-break:break-word;max-height:200px;overflow:auto;font-size:12px}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px}#message{min-height:24px}
@media(max-width:850px){main{grid-template-columns:1fr;padding:14px}header{padding:20px}h1{font-size:24px}}
</style></head><body>
<header><img src="/logo.jpg" alt="Factory Shorts logosu" width="72" height="72" style="float:left;border-radius:50%;margin-right:18px"><p class="small">TAMAMEN YEREL · TÜRKÇE · ÜCRETSİZ</p><h1>Factory Shorts</h1>
<p>Konunu seç. Türkçe sesli, altyazılı dikey videonu bilgisayarında üret.</p></header>
<main><div><section><h2>Yeni video</h2>
<label for="topic">Konu</label><textarea id="topic" rows="3" maxlength="500" placeholder="Örneğin: Ahtapotların neden üç kalbi var?"></textarea>
<p class="small">Boş bırakırsan Türkçe konu kategorilerinden birini seçer.</p>
<div class="row"><div><label for="duration">Hedef süre</label><select id="duration"><option value="20">20 saniye</option><option value="40" selected>40 saniye</option><option value="60">60 saniye</option><option value="90">90 saniye</option></select></div>
<div><label for="count">Video sayısı</label><input id="count" type="number" min="1" max="3" value="3"></div></div>
<label for="style">Anlatım biçimi</label><select id="style"><option value="">Otomatik</option><option value="facts">İlginç bilgiler</option><option value="story">Kısa hikâye</option><option value="listicle">Üç maddelik liste</option><option value="myth">Doğru bilinen yanlışlar</option><option value="quiz">Soru ve cevap</option><option value="explainer">Kolay anlatım</option></select>
<label for="caption_style">Altyazı görünümü</label><select id="caption_style"><option value="bold">Kalın ve belirgin</option><option value="boxed">Kutulu</option><option value="neon">Neon</option><option value="clean">Sade</option><option value="karaoke">Kelime vurgulu</option><option value="minimal">Minimal</option></select>
<label for="music">Arka plan müziği</label><select id="music"><option value="auto">Konuya göre otomatik beste</option><option value="calm">Sakin · Doğa</option><option value="wonder">Merak · Bilim</option><option value="bright">Enerjik · Spor</option><option value="dramatic">Sinematik</option><option value="off">Müzik kapalı</option></select><p class="small">Hazır şarkı veya ses örneği kullanmadan yerel olarak bestelenir. Konuşurken otomatik kısılır.</p><label for="references">Referans görsel veya video</label><div class="drop"><input id="references" type="file" multiple accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/webm,.mkv"><p class="small">Dosyaları seç veya bu kutuya sürükle. En fazla 10 dosya, dosya başına 100 MB. Bu konu için kullanılacak.</p><div id="uploads" aria-live="polite"></div><button id="clear" type="button">Seçimi temizle</button></div><p class="small">Referans yoksa Ollama konuya özel çizim tasarlar. Video başına en fazla 3 yerel illüstrasyon oluşturulur; fotoğraf gerçekçiliğinde değildir.</p><button id="go">Üretim kuyruğuna ekle</button><p id="message" role="status" aria-live="polite"></p>
<p class="small">Süre yaklaşık hedeftir. Videolar sırayla üretilir. Otomatik yayınlama kapalıdır.</p>
</section><section><h2>Çalışma durumu</h2><div id="checks">Kontrol ediliyor…</div>
<p class="small" id="mode"></p><p class="small">Referanslarını yukarıdaki kutudan yükle. Otomatik konular kendi yerel illüstrasyonlarını üretir.</p>
<p class="small">Seslendirme Supertonic 3 ile bilgisayarınızda yapılır. Kelime zamanları tahminidir; yayınlamadan önce kontrol edin.</p>
<button id="refresh">Yeniden kontrol et</button></section></div>
<div><section><h2>Popüler konular · Türkiye</h2><p class="small">Google Trends arama ilgisi sırası; 15 dakikada bir yenilenir. Her konu için 3 video. Panel açıkken otomatik üretim çalışır.</p><button id="auto">Durum alınıyor…</button><p id="autoStatus" role="status"></p><div id="trends"></div></section><section><h2>Üretim aşamaları</h2><p class="small">Senaryo → Türkçe ses → Görseller → Altyazı → Müzik → Video</p><div id="jobs" aria-live="polite">Henüz iş yok.</div></section>
<section><h2>Video kitaplığı</h2><p class="small">Çıktılar output_videos klasöründe saklanır. Yayınlamadan önce metni ve videoyu kontrol et.</p><div class="grid" id="videos">Kitaplık yükleniyor…</div></section></div></main>
<script>
const TOKEN="__TOKEN__",$=id=>document.getElementById(id),labels={queued:"Sırada",running:"Üretiliyor",done:"Tamamlandı",failed:"Başarısız",rendered:"Hazır",cancelled:"Durduruldu"};
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function api(url,body){
 const r=await fetch(url,body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json","X-Studio-Token":TOKEN},body:JSON.stringify(body)});
 const d=await r.json();if(!r.ok)throw Error(d.error||"İstek başarısız");return d;
}
async function info(){try{const i=await api("/api/info");
 $("mode").textContent="Model: "+i.llm+" · Ses: "+i.tts+" · Çıktı: "+i.resolution;
 $("checks").innerHTML=(i.checks||[]).map(c=>'<p class="'+(c.ok?'ok':'error')+'">'+(c.ok?'✓ ':'! ')+esc(c.name)+'<br><span class="small">'+esc(c.detail)+'</span></p>').join("");
}catch(e){$("checks").textContent="Bağlantı kurulamadı: "+e.message}}
async function jobs(){try{const js=await api("/api/jobs");
 $("jobs").innerHTML=js.length?js.map(j=>'<div class="job"><strong>'+esc(labels[j.status]||j.status)+'</strong> · #'+j.id+' '+esc(j.params.topic||"Otomatik konu")+
 '<p>'+esc(j.stage||'Sırada')+'</p><progress max="7" value="'+(j.status==='done'?7:Math.max(0,['Sırada','Senaryo hazırlanıyor','Türkçe ses üretiliyor','Görseller hazırlanıyor','Altyazılar hazırlanıyor','Müzik besteleniyor','Video birleştiriliyor'].indexOf(j.stage)))+'"></progress>'+
 (j.result?.title?'<p>'+esc(j.result.title)+'</p>':'')+
 (j.result?.error?'<p class="error">'+esc(j.result.error)+'</p>':'')+
 (j.log?.length?'<details '+(j.status==='failed'?'open':'')+'><summary>İşlem ayrıntıları</summary><pre>'+esc(j.log.join("\n"))+'</pre></details>':'')+'</div>').join(""):"Henüz iş yok.";
}catch(e){$("message").textContent="Panel bağlantısı kesildi. BASLAT.cmd ile tekrar açın."}}
let libraryState="";
async function videos(){try{const vs=await api("/api/videos"),key=JSON.stringify(vs);if(key===libraryState)return;libraryState=key;
 $("videos").innerHTML=vs.length?vs.map(v=>'<article class="video">'+(v.has_video?'<video controls preload="none" src="/files/'+v.id+'/short.mp4" poster="/files/'+v.id+'/cover.jpg"></video>':'')+
 '<h3>'+esc(v.title)+'</h3><p class="small">'+esc(labels[v.status]||v.status)+' · '+Number(v.duration||0).toFixed(1)+' saniye</p>'+
 (v.has_video?'<div class="actions"><a class="download" href="/files/'+v.id+'/short.mp4" download>MP4 indir</a><a href="/files/'+v.id+'/captions.srt" download>Altyazı</a><a href="/files/'+v.id+'/script.json" download>Senaryo</a><a href="/files/'+v.id+'/metadata.json" download>Açıklama</a></div>':'')+'</article>').join(""):"İlk videon burada görünecek.";
}catch(e){$("message").textContent=e.message}}
$("go").onclick=async()=>{const count=Number($("count").value);if(!Number.isInteger(count)||count<1||count>3){$("message").textContent="Video sayısı 1–3 olmalıdır.";return;}
 $("go").disabled=true;try{const d=await api("/api/make",{topic:$("topic").value.trim(),duration:$("duration").value,style:$("style").value,caption_style:$("caption_style").value,media_set:mediaSet,music:$("music").value,count});
 $("message").textContent=d.jobs.length+" video kuyruğa eklendi.";await jobs();
 }catch(e){$("message").textContent=e.message}finally{$("go").disabled=false}};
let mediaSet="",uploading=false,autoEnabled=true;
async function uploadFiles(files){
 if(uploading)return;uploading=true;$("go").disabled=true;$("clear").disabled=true;
 try{for(const f of files){
  if(f.size>100*1024*1024)throw Error(f.name+": 100 MB sınırını aşıyor");
  $("message").textContent=f.name+" yükleniyor…";
  const r=await fetch("/api/reference",{method:"POST",headers:{"X-Studio-Token":TOKEN,"X-File-Name":encodeURIComponent(f.name),"X-Media-Set":mediaSet},body:f});
  const d=await r.json();if(!r.ok)throw Error(d.error);mediaSet=d.media_set;
  const line=document.createElement("p");line.className="small";line.textContent="✓ "+d.name;$("uploads").append(line);
 }$("message").textContent="Referanslar hazır.";}catch(e){$("message").textContent=e.message}
 finally{uploading=false;$("go").disabled=false;$("clear").disabled=false;$("references").value="";}
}
$("references").onchange=e=>uploadFiles(e.target.files);
const drop=document.querySelector('.drop');drop.ondragover=e=>{e.preventDefault();drop.classList.add('over')};drop.ondragleave=()=>drop.classList.remove('over');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('over');uploadFiles(e.dataTransfer.files)};
$("clear").onclick=()=>{mediaSet="";$("uploads").replaceChildren();$("message").textContent="Sonraki üretimde otomatik illüstrasyon kullanılacak."};
async function automatic(){try{const d=await api('/api/automatic');autoEnabled=d.enabled;
 $("auto").textContent=d.enabled?'Otomatik üretimi duraklat':'Otomatik üretimi başlat';
 $("autoStatus").textContent=d.error||(d.enabled?'Açık · Konu başına 3 video sırayla üretilecek.':'Duraklatıldı. Başlamış video tamamlanır.');
 $("trends").innerHTML=d.items.length?d.items.map((t,i)=>'<div class="trend">'+(i+1)+'. '+esc(t.title)+' <span class="small">'+esc(t.traffic)+' '+(t.used?'· Kuyruğa alındı':'')+'</span></div>').join(''):'Güncel konular alınıyor…';
}catch(e){$("autoStatus").textContent=e.message}}
$("auto").onclick=async()=>{try{await api('/api/automatic',{enabled:!autoEnabled});await automatic()}catch(e){$("autoStatus").textContent=e.message}};
async function heartbeat(){try{await api('/api/heartbeat',{})}catch(e){/* server stopped */}}
heartbeat();automatic();setInterval(heartbeat,20000);setInterval(automatic,15000);
$("refresh").onclick=info;info();jobs();videos();setInterval(jobs,3000);setInterval(videos,10000);
</script></body></html>"""
