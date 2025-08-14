# presupuestos_dtf/app.py
import threading
import tkinter as tk
from tkinter import messagebox as mb
from .ui import PresupuestoApp
from .updater import check_for_update, download_and_replace

def run() -> None:
    root = tk.Tk()
    app = PresupuestoApp(root)

    def _check_update_bg():
        # Evita que un fallo de red rompa la app
        try:
            has_update, latest, url = check_for_update()
        except Exception as e:
            print("[Updater] check failed:", e)
            return

        if has_update and url:
            # Aviso claro: se cerrará y reabrirá automáticamente
            if mb.askyesno(
                "Actualización disponible",
                f"Hay una versión nueva ({latest}).\n"
                f"Se descargará y la aplicación se reiniciará automáticamente.\n\n"
                f"¿Actualizar ahora?"
            ):
                try:
                    download_and_replace(url)  # Gestiona descarga + reemplazo + relanzar
                except Exception as e:
                    mb.showerror("Error de actualización", f"No se pudo actualizar:\n{e}")

    # Comprobación en segundo plano para no bloquear la UI
    threading.Thread(target=_check_update_bg, daemon=True).start()

    root.mainloop()
