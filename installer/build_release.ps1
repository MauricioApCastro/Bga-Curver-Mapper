$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "== BGA Mapper build profissional ==" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath ".\.venv")) {
    Write-Host "Criando ambiente virtual .venv..."
    python -m venv .venv
}

Write-Host "Instalando/atualizando dependências..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Limpando build anterior..."
Remove-Item -LiteralPath "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath "dist" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "release" -Force | Out-Null

Write-Host "Gerando aplicativo empacotado com PyInstaller..."
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean BGA_Mapper.spec

$innoCandidates = @(@(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path -LiteralPath $_) })

if ($innoCandidates.Count -gt 0) {
    Write-Host "Gerando instalador com Inno Setup..."
    & $innoCandidates[0] "installer\BGA_Mapper.iss"
    Write-Host "Instalador pronto em: release" -ForegroundColor Green
} else {
    Write-Host "Inno Setup não encontrado. O app empacotado está em: dist\BGA Mapper" -ForegroundColor Yellow
    Write-Host "Instale o Inno Setup 6 e rode este script novamente para gerar o instalador .exe."
}