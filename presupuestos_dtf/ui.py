# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from .constants import MIN_VAL, APP_TITLE, WINDOW_SIZE
from . import __version__
from .config import load_config, save_config
from .models import CalcInput
from .calc import compute_layout

class PresupuestoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(f"{APP_TITLE} — v{__version__}")
        root.geometry(WINDOW_SIZE)
        root.resizable(False, False)

        cfg = load_config()

        # Config persistente
        self.roll_width_cm = tk.DoubleVar(value=cfg["roll_width_cm"])
        self.price_per_meter = tk.DoubleVar(value=cfg["price_per_meter"])
        self.margin_top_cm = tk.DoubleVar(value=cfg["margin_top_cm"])
        self.margin_right_cm = tk.DoubleVar(value=cfg["margin_right_cm"])

        # Entradas cálculo
        self.image_width_cm = tk.DoubleVar(value=1)
        self.image_height_cm = tk.DoubleVar(value=1)
        self.num_copies = tk.IntVar(value=1)

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.calc_tab = self._build_calc_tab(self.notebook)
        self.config_tab = self._build_config_tab(self.notebook)
        self.notebook.select(self.calc_tab)

        # Atajos
        self.root.bind("<Return>", self._on_return)
        self.root.bind("<KP_Enter>", self._on_return)

        # Guardar al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # -------- Tabs -------- #
    def _build_config_tab(self, notebook: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Configuración")

        ttk.Label(frame, text="Ancho máximo del rollo (cm):").grid(row=0, column=0, sticky=tk.W, padx=6, pady=8)
        ttk.Entry(frame, textvariable=self.roll_width_cm, width=12).grid(row=0, column=1, padx=6, pady=8)

        ttk.Label(frame, text="Precio por metro (€):").grid(row=1, column=0, sticky=tk.W, padx=6, pady=8)
        ttk.Entry(frame, textvariable=self.price_per_meter, width=12).grid(row=1, column=1, padx=6, pady=8)

        ttk.Label(frame, text="Margen superior (cm):").grid(row=2, column=0, sticky=tk.W, padx=6, pady=8)
        ttk.Entry(frame, textvariable=self.margin_top_cm, width=12).grid(row=2, column=1, padx=6, pady=8)

        ttk.Label(frame, text="Margen derecho (cm):").grid(row=3, column=0, sticky=tk.W, padx=6, pady=8)
        ttk.Entry(frame, textvariable=self.margin_right_cm, width=12).grid(row=3, column=1, padx=6, pady=8)

        ttk.Label(frame, text="Mínimo numérico: 0,10. Copias mínimas: 1.", wraplength=480)\
            .grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=6, pady=6)

        ttk.Button(frame, text="Guardar configuración", command=self._save_current_config)\
            .grid(row=5, column=1, sticky=tk.E, padx=6, pady=12)
        return frame

    def _build_calc_tab(self, notebook: ttk.Notebook) -> ttk.Frame:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Cálculo")

        input_box = ttk.LabelFrame(frame, text="Datos del diseño")
        input_box.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        ttk.Label(input_box, text="Ancho imagen (cm):").grid(row=0, column=0, sticky=tk.W, padx=6, pady=6)
        ttk.Entry(input_box, textvariable=self.image_width_cm, width=12).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(input_box, text="Alto imagen (cm):").grid(row=0, column=2, sticky=tk.W, padx=6, pady=6)
        ttk.Entry(input_box, textvariable=self.image_height_cm, width=12).grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(input_box, text="Número de copias:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=6)
        ttk.Entry(input_box, textvariable=self.num_copies, width=12).grid(row=1, column=1, padx=6, pady=6)

        ttk.Button(input_box, text="Calcular", command=self.on_calcular)\
            .grid(row=1, column=3, padx=6, pady=6, sticky=tk.E)

        self.result_frame = ttk.Frame(frame)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)
        return frame

    # -------- Atajos -------- #
    def _on_return(self, event=None):
        current_idx = self.notebook.index(self.notebook.select())
        if current_idx == self.notebook.index(self.calc_tab):
            self.on_calcular()
        else:
            self._save_current_config()

    # -------- Persistencia -------- #
    def _save_current_config(self) -> None:
        ok, err = self._validate_config_only()
        if not ok:
            messagebox.showerror("Error de configuración", err)
            return
        save_config(
            float(self.roll_width_cm.get()),
            float(self.price_per_meter.get()),
            float(self.margin_top_cm.get()),
            float(self.margin_right_cm.get())
        )
        messagebox.showinfo("OK", "Configuración guardada.")

    def _on_close(self) -> None:
        ok, _ = self._validate_config_only()
        if ok:
            save_config(
                float(self.roll_width_cm.get()),
                float(self.price_per_meter.get()),
                float(self.margin_top_cm.get()),
                float(self.margin_right_cm.get())
            )
        self.root.destroy()

    def _validate_config_only(self) -> tuple[bool, str]:
        try:
            roll_width = float(self.roll_width_cm.get())
            price = float(self.price_per_meter.get())
            margin_top = float(self.margin_top_cm.get())
            margin_right = float(self.margin_right_cm.get())
        except Exception:
            return False, "Introduce números válidos en configuración."
        bad = []
        for name, val in [
            ("Ancho del rollo", roll_width),
            ("Precio/metro", price),
            ("Margen superior", margin_top),
            ("Margen derecho", margin_right),
        ]:
            if val < MIN_VAL:
                bad.append(f"{name} ≥ {MIN_VAL:g}")
        if bad:
            return False, "Valores mínimos no válidos:\n- " + "\n- ".join(bad)
        return True, ""

    # -------- Cálculo -------- #
    def _validate_inputs(self) -> tuple[bool, str]:
        try:
            roll_width = float(self.roll_width_cm.get())
            price = float(self.price_per_meter.get())
            width = float(self.image_width_cm.get())
            height = float(self.image_height_cm.get())
            margin_top = float(self.margin_top_cm.get())
            margin_right = float(self.margin_right_cm.get())
            copies = int(self.num_copies.get())
        except Exception:
            return False, "Introduce números válidos."

        bad = []
        for name, val in [
            ("Ancho del rollo", roll_width),
            ("Precio/metro", price),
            ("Ancho imagen", width),
            ("Alto imagen", height),
            ("Margen superior", margin_top),
            ("Margen derecho", margin_right),
        ]:
            if val < MIN_VAL:
                bad.append(f"{name} ≥ {MIN_VAL:g}")
        if copies < 1:
            bad.append("Copias ≥ 1")
        if bad:
            return False, "Valores mínimos no válidos:\n- " + "\n- ".join(bad)
        return True, ""

    def on_calcular(self) -> None:
        ok, err = self._validate_inputs()
        if not ok:
            messagebox.showerror("Error de entrada", err)
            return

        for w in self.result_frame.winfo_children():
            w.destroy()

        roll_width = float(self.roll_width_cm.get())
        price = float(self.price_per_meter.get())
        width = float(self.image_width_cm.get())
        height = float(self.image_height_cm.get())
        margin_top = float(self.margin_top_cm.get())
        margin_right = float(self.margin_right_cm.get())
        copies = int(self.num_copies.get())

        inputs = [
            CalcInput(roll_width, price, width, height, margin_top, margin_right, copies, 0),
            CalcInput(roll_width, price, width, height, margin_top, margin_right, copies, 90),
        ]
        results = [compute_layout(i) for i in inputs]

        frames = []
        frames.append(ttk.LabelFrame(self.result_frame, text="Rotación 0° (vertical)"))
        frames[-1].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        frames.append(ttk.LabelFrame(self.result_frame, text="Rotación 90° (horizontal)"))
        frames[-1].pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        for res, frm in zip(results, frames):
            ttk.Label(frm, text=f"Ancho del rollo: {roll_width:.2f} cm").pack(anchor=tk.W, padx=6, pady=3)
            ttk.Label(frm, text=f"Diseños por fila: {res.designs_per_row}").pack(anchor=tk.W, padx=6, pady=3)
            ttk.Label(frm, text=f"Filas necesarias: {res.rows_needed}").pack(anchor=tk.W, padx=6, pady=3)
            ttk.Label(frm, text=f"Aprovechamiento: {res.usage_percent:.2f}%").pack(anchor=tk.W, padx=6, pady=3)
            ttk.Label(frm, text=f"Longitud: {res.total_height_cm:.2f} cm (≈ {res.total_height_m:.3f} m)").pack(anchor=tk.W, padx=6, pady=3)
            ttk.Label(frm, text=f"Coste estimado: {res.cost:.2f} €").pack(anchor=tk.W, padx=6, pady=3)
