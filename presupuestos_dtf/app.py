# -*- coding: utf-8 -*-
import tkinter as tk
from .ui import PresupuestoApp

def run() -> None:
    root = tk.Tk()
    PresupuestoApp(root)
    root.mainloop()
