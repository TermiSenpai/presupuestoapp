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
EXECUTABLE_NAME = "DTF_Pricing_Calculator.exe"  # coherente con tu .bat
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # opcional

# --- Funciones internas ---
def _ver_tuple(s: str) -> tuple[int, ...]:
    """Convierte una cadena de versión en tupla comparable."""
    core = s.lstrip("v").split("-")[0]  # quita 'v' y sufijos tipo -beta
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
        resp = requests.get(url, headers=_gh_headers(), timeout=8)
        resp.raise_for_status()
        data = resp.json()

        latest_version = data["tag_name"]
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

def download_and_replace(download_url):
    """Descarga la nueva versión y reemplaza el ejecutable actual."""
    tmp_file = os.path.join(tempfile.gettempdir(), EXECUTABLE_NAME)
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_file, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    current_exe = sys.argv[0]
    backup = current_exe + ".bak"
    try:
        if os.path.exists(backup):
            os.remove(backup)
    except:
        pass

    os.replace(current_exe, backup)
    shutil.move(tmp_file, current_exe)

    print("[Updater] Update installed. Restarting...")
    subprocess.Popen([current_exe])
    sys.exit(0)

# --- Prueba manual ---
if __name__ == "__main__":
    ok, latest, url = check_for_update()
    print(f"current={__version__} latest={latest} has_update={ok} url={url}")
