param([switch]$SkipModel)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
function Run-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Komut basarisiz: $Executable (kod $LASTEXITCODE)" }
}
try {
    if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
        $pythonCommand = $null
        if (Get-Command py -ErrorAction SilentlyContinue) {
            $candidate = & py -3 -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0) { $pythonCommand = $candidate | Select-Object -Last 1 }
        }
        if (-not $pythonCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
            $candidate = & python -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0) { $pythonCommand = $candidate | Select-Object -Last 1 }
        }
        if (-not $pythonCommand) { throw "Python 3.12 bulunamadi. https://www.python.org/downloads/windows/ adresinden kurup KURULUM.cmd dosyasini tekrar acin." }
        Run-Checked $pythonCommand @("-c", "import sys; assert (3,10) <= sys.version_info < (3,15), 'Python 3.10-3.14 gerekli; 3.12 onerilir'")
        Run-Checked $pythonCommand @("-m","venv",".venv")
    }
    $pythonExe = Join-Path (Get-Location) ".venv\Scripts\python.exe"
    Run-Checked $pythonExe @("-m","pip","install","-e",".[local]")
    Run-Checked $pythonExe @("windows\prepare.py","voice")
    if (-not $SkipModel) {
        Run-Checked $pythonExe @("windows\prepare.py","ollama")
        & (Join-Path $PSScriptRoot "start-ollama.ps1")
        Run-Checked (Join-Path (Get-Location) ".tools\ollama\ollama.exe") @("pull","qwen3:4b-instruct")
    }
    Run-Checked $pythonExe @("windows\prepare.py","config")
    Write-Host "Kurulum tamam. BASLAT.cmd dosyasini acin."
} catch {
    Write-Host ("Kurulum durdu: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
