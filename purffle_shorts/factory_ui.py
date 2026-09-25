"""Türkçe fabrika paneli."""
PAGE = r"""<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Türkçe Video Fabrikası</title>
<style>
:root{color-scheme:dark;--bg:#0c101b;--card:#151c2d;--line:#2b3751;--muted:#aebbd0;--accent:#b8f677}
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
pre{white-space:pre-wrap;word-break:break-word;max-height:200px;overflow:auto;font-size:12px}
:focus-visible{outline:3px solid var(--accent);outline-offset:3px}#message{min-height:24px}
@media(max-width:850px){main{grid-template-columns:1fr;padding:14px}header{padding:20px}h1{font-size:24px}}
</style></head><body>
<header><p class="small">PURFFLESHORTS · YEREL OLLAMA</p><h1>Türkçe Video Fabrikası</h1>
<p>Konunu seç. Türkçe sesli, altyazılı dikey videonu bilgisayarında üret.</p></header>
<main><div><section><h2>Yeni video</h2>
<label for="topic">Konu</label><textarea id="topic" rows="3" maxlength="500" placeholder="Örneğin: Ahtapotların neden üç kalbi var?"></textarea>
<p class="small">Boş bırakırsan Türkçe konu kategorilerinden birini seçer.</p>
<div class="row"><div><label for="duration">Hedef süre</label><select id="duration"><option value="20">20 saniye</option><option value="40" selected>40 saniye</option><option value="60">60 saniye</option><option value="90">90 saniye</option></select></div>
<div><label for="count">Video sayısı</label><input id="count" type="number" min="1" max="20" value="1"></div></div>
<label for="style">Anlatım biçimi</label><select id="style"><option value="">Otomatik</option><option value="facts">İlginç bilgiler</option><option value="story">Kısa hikâye</option><option value="listicle">Üç maddelik liste</option><option value="myth">Doğru bilinen yanlışlar</option><option value="quiz">Soru ve cevap</option><option value="explainer">Kolay anlatım</option></select>
<label for="caption_style">Altyazı görünümü</label><select id="caption_style"><option value="bold">Kalın ve belirgin</option><option value="boxed">Kutulu</option><option value="neon">Neon</option><option value="clean">Sade</option><option value="karaoke">Kelime vurgulu</option><option value="minimal">Minimal</option></select>
<button id="go">Üretim kuyruğuna ekle</button><p id="message" role="status" aria-live="polite"></p>
<p class="small">Süre yaklaşık hedeftir. Videolar sırayla üretilir. Otomatik yayınlama kapalıdır.</p>
</section><section><h2>Çalışma durumu</h2><div id="checks">Kontrol ediliyor…</div>
<p class="small" id="mode"></p><p class="small">Görseller için kendi video ve fotoğraflarını <b>media</b> klasörüne koy. Klasör boşsa hareketli renkli arka plan kullanılır; yapay zekâ ile fotoğraf veya video üretilmez.</p>
<p class="small">Seslendirme Supertonic 3 ile bilgisayarınızda yapılır. Kelime zamanları tahminidir; yayınlamadan önce kontrol edin.</p>
<button id="refresh">Yeniden kontrol et</button></section></div>
<div><section><h2>Üretim kuyruğu</h2><div id="jobs" aria-live="polite">Henüz iş yok.</div></section>
<section><h2>Video kitaplığı</h2><p class="small">Çıktılar output_videos klasöründe saklanır. Yayınlamadan önce metni ve videoyu kontrol et.</p><div class="grid" id="videos">Kitaplık yükleniyor…</div></section></div></main>
<script>
const TOKEN="__TOKEN__",$=id=>document.getElementById(id),labels={queued:"Sırada",running:"Üretiliyor",done:"Tamamlandı",failed:"Başarısız",rendered:"Hazır"};
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
$("go").onclick=async()=>{const count=Number($("count").value);if(!Number.isInteger(count)||count<1||count>20){$("message").textContent="Video sayısı 1–20 olmalıdır.";return;}
 $("go").disabled=true;try{const d=await api("/api/make",{topic:$("topic").value.trim(),duration:$("duration").value,style:$("style").value,caption_style:$("caption_style").value,count});
 $("message").textContent=d.jobs.length+" video kuyruğa eklendi.";await jobs();
 }catch(e){$("message").textContent=e.message}finally{$("go").disabled=false}};
$("refresh").onclick=info;info();jobs();videos();setInterval(jobs,3000);setInterval(videos,10000);
</script></body></html>"""
