# presupuestos_dtf/updater.py
import os
import sys
import tempfile
import shutil
import subprocess
import requests

# --- Resolver __version__ tanto si se ejecuta como paquete como script ---
try:
    # Cuando se ejecuta como módulo: python -m presupuestos_dtf.updater
    from . import __version__  # type: ignore
except Exception:
    # Cuando se ejecuta directamente: python presupuestos_dtf/updater.py
    import pathlib
    pkg_root = pathlib.Path(__file__).resolve().parents[1]  # carpeta raíz del proyecto
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    try:
        from presupuestos_dtf import __version__  # type: ignore
    except Exception:
        __version__ = "0.0.0"  # fallback

# --- Configuración ---
GITHUB_USER = "TermiSenpai"
GITHUB_REPO = "presupuestoapp"
EXECUTABLE_NAME = "DTF_Pricing_Calculator.exe"  # debe coincidir con el asset de la release
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # opcional

# --- Utilidades ---
def _ver_tuple(s: str) -> tuple[int, ...]:
    """Convierte una cadena de versión en tupla comparable (soporta prefijo v y sufijos -beta)."""
    core = s.lstrip("v").split("-")[0]
    return tuple(int(x) for x in core.split("."))

def _gh_headers():
    """Encabezados para la API de GitHub (con token si está disponible)."""
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

# --- API ---
def check_for_update():
    """Comprueba si hay una versión más reciente disponible en GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    try:
        resp = requests.get(url, headers=_gh_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()

        latest_version = data["tag_name"]  # ej. "v1.1.0"
        asset_url = None
        for asset in data.get("assets", []):
            if asset.get("name") == EXECUTABLE_NAME:
                asset_url = asset.get("browser_download_url")
                break

        is_newer = _ver_tuple(latest_version) > _ver_tuple(__version__)
        return is_newer, latest_version, asset_url
    except Exception as e:
        print(f"[Updater] check error: {e}")
        return False, None, None

# --- Reemplazo seguro en Windows con .bat auxiliar ---
_WINDOWS_REPLACER_BAT = r"""@echo off
setlocal enableextensions
set EXE=%~1
set NEW=%~2
set BAK=%EXE%.bak

REM Espera breve para que el proceso principal termine
timeout /t 1 /nobreak >nul

:waitloop
REM Intenta renombrar el ejecutable actual a .bak (si está en uso, reintenta)
move /y "%EXE%" "%BAK%" >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto waitloop
)

REM Mueve el nuevo ejecutable a su lugar
move /y "%NEW%" "%EXE%" >nul 2>&1

REM Lanza la nueva versión
start "" "%EXE%"

REM Limpia el backup (.bak) tras arrancar la nueva versión
del /f /q "%BAK%" >nul 2>&1

endlocal
exit /b 0
"""

def _launch_windows_replacer(current_exe: str, tmp_file: str):
    """Crea y lanza un .bat que reemplaza el exe y relanza la app (Windows)."""
    bat_path = os.path.join(tempfile.gettempdir(), "dtf_replacer.bat")
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(_WINDOWS_REPLACER_BAT)

        # Ejecuta el .bat; luego forzamos salida del proceso actual para liberar el lock
        subprocess.Popen(
            ["cmd.exe", "/c", bat_path, os.path.abspath(current_exe), os.path.abspath(tmp_file)],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    except Exception as e:
        print(f"[Updater] replacer launch error: {e}")
    finally:
        # IMPORTANTE: terminar TODO el proceso (no solo el hilo) para soltar el bloqueo.
        os._exit(0)

def download_and_replace(download_url: str):
    """
    Descarga la nueva versión. En Windows, delega el reemplazo a un .bat auxiliar
    que espera a que la app se cierre, renombra a .bak, mueve el nuevo exe, borra el .bak y relanza.
    """
    tmp_file = os.path.join(tempfile.gettempdir(), EXECUTABLE_NAME)

    # Descarga a %TEMP%
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    current_exe = sys.argv[0]

    if os.name == "nt":
        _launch_windows_replacer(current_exe, tmp_file)
    else:
        # Fallback no-Windows: requiere que el proceso principal se cierre antes del replace.
        backup = current_exe + ".bak"
        try:
            if os.path.exists(backup):
                os.remove(backup)
        except Exception:
            pass
        os.replace(current_exe, backup)
        shutil.move(tmp_file, current_exe)
        print("[Updater] Update installed. Restarting...")
        subprocess.Popen([current_exe])
        os._exit(0)

# --- Prueba manual ---
if __name__ == "__main__":
    ok, latest, url = check_for_update()
    print(f"current={__version__} latest={latest} has_update={ok} url={url}")
