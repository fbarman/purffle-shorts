$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:OLLAMA_HOST = "127.0.0.1:11434"
$env:OLLAMA_MODELS = Join-Path (Get-Location) "models\ollama"
$env:OLLAMA_NO_CLOUD = "1"
$env:OLLAMA_NUM_PARALLEL = "1"
try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3
    return
} catch {}
$ollamaExe = Join-Path (Get-Location) ".tools\ollama\ollama.exe"
if (-not (Test-Path -LiteralPath $ollamaExe)) { throw "Ollama eksik. Once KURULUM.cmd dosyasini calistirin." }
Start-Process -FilePath $ollamaExe -ArgumentList "serve" -WindowStyle Hidden -RedirectStandardOutput ".tools\ollama-out.log" -RedirectStandardError ".tools\ollama-error.log"
for ($attempt=0; $attempt -lt 30; $attempt++) {
    try {
        $null = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2
        return
    } catch { Start-Sleep -Seconds 1 }
}
throw "Ollama baslatilamadi. .tools\ollama-error.log dosyasini inceleyin."
