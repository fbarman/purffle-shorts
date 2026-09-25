$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& .venv/Scripts/python.exe -m PyInstaller --noconfirm --onedir --windowed --name 'Factory Shorts' --icon purffle_shorts/assets/logo.ico --add-data 'purffle_shorts/assets;purffle_shorts/assets' --collect-all supertonic --collect-all onnxruntime --collect-all imageio_ffmpeg --collect-all soundfile --hidden-import numpy factory_desktop.py
if ($LASTEXITCODE -ne 0) { throw 'EXE derlenemedi.' }
$target = Join-Path (Get-Location) 'dist/Factory Shorts'
Copy-Item -LiteralPath '.tools/ollama' -Destination (Join-Path $target 'ollama') -Recurse -Force
Copy-Item -LiteralPath 'models' -Destination (Join-Path $target 'models') -Recurse -Force
Copy-Item -LiteralPath 'LICENSE' -Destination (Join-Path $target 'LICENSE.txt') -Force
Copy-Item -LiteralPath 'PORTABLE-OKU.md' -Destination (Join-Path $target 'Beni Oku.md') -Force
