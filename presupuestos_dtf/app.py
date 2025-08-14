# presupuestos_dtf/app.py
import threading
import tkinter as tk
from .ui import PresupuestoApp
from .updater import check_for_update, download_and_replace

def run() -> None:
    root = tk.Tk()
    app = PresupuestoApp(root)

    def _check_update():
        has_update, latest, url = check_for_update()
        if has_update and url:
            import tkinter.messagebox as mb
            if mb.askyesno("Update available",
                           f"A new version ({latest}) is available.\nInstall now?"):
                download_and_replace(url)

    # comprobación en segundo plano para no bloquear la UI
    threading.Thread(target=_check_update, daemon=True).start()

    root.mainloop()
