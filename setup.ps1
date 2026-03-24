param(
    [switch]$WithDatabase,
    [switch]$RecreateVenv,
    [switch]$SkipInstall,
    [string]$PythonCommand = "python"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPath = Join-Path $projectRoot ".venv"
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$requirementsFile = if ($WithDatabase) { "requirements_with_db.txt" } else { "requirements.txt" }

Write-Host "[1/5] Project root: $projectRoot"

if (-not (Test-Path $requirementsFile)) {
    throw "File $requirementsFile tidak ditemukan di root project."
}

if ($RecreateVenv -and (Test-Path $venvPath)) {
    Write-Host "[2/5] Menghapus virtual environment lama..."
    Remove-Item $venvPath -Recurse -Force
}

if (-not (Test-Path $venvPath)) {
    Write-Host "[2/5] Membuat virtual environment baru (.venv)..."
    & $PythonCommand -m venv $venvPath
} else {
    Write-Host "[2/5] Virtual environment sudah ada, lanjut..."
}

if (-not (Test-Path $pythonExe)) {
    throw "Python di venv tidak ditemukan: $pythonExe"
}

Write-Host "[3/5] Upgrade pip di dalam venv..."
& $pythonExe -m pip install --upgrade pip

if ($SkipInstall) {
    Write-Host "[4/5] Skip install dependency (sesuai parameter -SkipInstall)."
} else {
    Write-Host "[4/5] Install dependency dari $requirementsFile ..."
    & $pythonExe -m pip install -r $requirementsFile
}

Write-Host "[5/5] Selesai."
Write-Host ""
Write-Host "Aktifkan venv dengan:" -ForegroundColor Green
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Contoh pemakaian:" -ForegroundColor Green
Write-Host "- setup standar      : .\setup.ps1" -ForegroundColor Yellow
Write-Host "- setup + database   : .\setup.ps1 -WithDatabase" -ForegroundColor Yellow
Write-Host "- reset venv total   : .\setup.ps1 -RecreateVenv" -ForegroundColor Yellow
