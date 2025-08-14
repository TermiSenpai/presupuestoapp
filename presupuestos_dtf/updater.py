# presupuestos_dtf/updater.py
import os
import sys
import tempfile
import shutil
import subprocess
import zipfile
from pathlib import Path
import requests

# --- Resolver __version__ tanto si se ejecuta como paquete como script ---
try:
    from . import __version__  # type: ignore
except Exception:
    pkg_root = Path(__file__).resolve().parents[1]
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    try:
        from presupuestos_dtf import __version__  # type: ignore
    except Exception:
        __version__ = "0.0.0"

# --- Config ---
GITHUB_USER = "TermiSenpai"
GITHUB_REPO = "presupuestoapp"
ASSET_ZIP_NAME = "DTF_Pricing_Calculator_win64.zip"   # <--- el ZIP que subes a la release
EXE_NAME = "DTF_Pricing_Calculator.exe"               # <--- exe dentro de la carpeta onedir
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")               # opcional para evitar rate-limit
TIMEOUT = 30

# --- Utilidades ---
def _ver_tuple(s: str) -> tuple[int, ...]:
    core = s.lstrip("v").split("-")[0]
    return tuple(int(x) for x in core.split("."))

def _gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

# --- API ---
def _latest_release():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    r = requests.get(url, headers=_gh_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def check_for_update():
    """Devuelve (hay_update, tag, asset_zip_url)."""
    try:
        data = _latest_release()
        tag = data["tag_name"]
        asset_url = None
        for a in data.get("assets", []):
            if a.get("name") == ASSET_ZIP_NAME:
                asset_url = a.get("browser_download_url")
                break
        is_newer = _ver_tuple(tag) > _ver_tuple(__version__)
        return is_newer, tag, asset_url
    except Exception as e:
        print(f"[Updater] check error: {e}")
        return False, None, None

# --- Descarga y staging del ZIP ---
def _download_zip(url: str) -> Path:
    dst = Path(tempfile.gettempdir()) / ASSET_ZIP_NAME
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            shutil.copyfileobj(r.raw, f)
            f.flush(); os.fsync(f.fileno())
    return dst

def _extract_to_stage(zip_path: Path) -> Path:
    stage = Path(tempfile.mkdtemp(prefix="dtf_stage_"))
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(stage)  # el ZIP que generas no debe llevar carpeta raíz
    try:
        zip_path.unlink(missing_ok=True)
    except Exception:
        pass
    return stage

# --- Reemplazo seguro con .bat: mata/espera, robocopy /MIR y relanza ---
_REPLACER_BAT = r"""@echo off
setlocal enableextensions
set "INSTALL=%~1"
set "STAGE=%~2"
set "PID=%~3"
set "EXE=%~4"

REM Matar y esperar al proceso antiguo (hasta 45 s)
taskkill /PID %PID% /T /F >nul 2>&1
powershell -NoProfile -Command "try { Wait-Process -Id %PID% -Timeout 45 } catch {}" >nul 2>&1

REM Pequeña espera por antivirus/IO
timeout /t 2 /nobreak >nul

REM Copia espejo: borra lo que sobra y copia lo nuevo
robocopy "%STAGE%" "%INSTALL%" /MIR /R:2 /W:1 >nul

REM Relanzar
start "" "%INSTALL%\%EXE%"

REM Limpiar staging
rmdir /s /q "%STAGE%" >nul 2>&1

endlocal
exit /b 0
"""

def _launch_replacer(install_dir: Path, stage_dir: Path):
    bat = Path(tempfile.gettempdir()) / "dtf_zip_replacer.bat"
    bat.write_text(_REPLACER_BAT, encoding="utf-8")
    pid = os.getpid()
    subprocess.Popen(
        ["cmd.exe", "/c", str(bat), str(install_dir), str(stage_dir), str(pid), EXE_NAME],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    os._exit(0)  # cerrar la app actual para soltar locks

# --- Punto de entrada para la app ---
def download_and_replace(download_url: str):
    """
    NUEVO FLUJO (onedir + ZIP):
    1) Descarga el ZIP del release.
    2) Extrae a 'stage'.
    3) Lanza un .bat que mata/espera, hace robocopy /MIR a la carpeta de instalación y relanza el .exe.
    """
    zip_path = _download_zip(download_url)
    stage = _extract_to_stage(zip_path)

    # Carpeta de instalación (en --onedir es el directorio donde vive el .exe y las DLLs)
    here = Path(sys.argv[0]).resolve()
    install_dir = here.parent if here.suffix.lower() == ".exe" else Path.cwd()

    _launch_replacer(install_dir, stage)

# --- Prueba manual ---
if __name__ == "__main__":
    ok, tag, url = check_for_update()
    print(f"current={__version__} latest={tag} has_update={ok} url={url}")
