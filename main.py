#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import math
import os
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk, messagebox

MIN_VAL = 0.10
DEFAULT_ROLL_WIDTH_CM = 57.0
DEFAULT_PRICE_PER_METER = 11.0
DEFAULT_MARGIN_TOP_CM = 0.5
DEFAULT_MARGIN_RIGHT_CM = 0.5
APP_DIRNAME = "PresupuestosDTF"
CONFIG_FILENAME = "config.json"


def get_config_path() -> Path:
    if sys.platform.startswith("win"):
        base = os.getenv("APPDATA", str(Path.home()))
        cfg_dir = Path(base) / APP_DIRNAME
    else:
        cfg_dir = Path.home() / f".{APP_DIRNAME}"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / CONFIG_FILENAME


def load_config() -> dict:
    p = get_config_path()
    if p.exists():
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "roll_width_cm": float(data.get("roll_width_cm", DEFAULT_ROLL_WIDTH_CM)),
                    "price_per_meter": float(data.get("price_per_meter", DEFAULT_PRICE_PER_METER)),
                    "margin_top_cm": float(data.get("margin_top_cm", DEFAULT_MARGIN_TOP_CM)),
                    "margin_right_cm": float(data.get("margin_right_cm", DEFAULT_MARGIN_RIGHT_CM)),
                }
        except Exception:
            pass
    return {
        "roll_width_cm": DEFAULT_ROLL_WIDTH_CM,
        "price_per_meter": DEFAULT_PRICE_PER_METER,
        "margin_top_cm": DEFAULT_MARGIN_TOP_CM,
        "margin_right_cm": DEFAULT_MARGIN_RIGHT_CM,
    }


def save_config(roll_width_cm: float, price_per_meter: float, margin_top_cm: float, margin_right_cm: float) -> None:
    data = {
        "roll_width_cm": roll_width_cm,
        "price_per_meter": price_per_meter,
        "margin_top_cm": margin_top_cm,
        "margin_right_cm": margin_right_cm,
    }
    try:
        with get_config_path().open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showwarning("Aviso", f"No se pudo guardar la configuración:\n{e}")


@dataclass(frozen=True)
class CalcInput:
    roll_width_cm: float
    price_per_meter: float
    image_width_cm: float
    image_height_cm: float
    margin_top_cm: float
    margin_right_cm: float
    num_copies: int
    orientation_deg: int  # 0 o 90


@dataclass(frozen=True)
class CalcResult:
    orientation_deg: int
    designs_per_row: int
    rows_needed: int
    usage_percent: float
    total_height_cm: float
    total_height_m: float
    cost: float


def compute_layout(data: CalcInput) -> CalcResult:
    if data.orientation_deg not in (0, 90):
        raise ValueError("La orientación debe ser 0 o 90 grados.")

    w = data.image_width_cm if data.orientation_deg == 0 else data.image_height_cm
    h = data.image_height_cm if data.orientation_deg == 0 else data.image_width_cm

    designs_per_row = max(1, int(math.floor((data.roll_width_cm + data.margin_right_cm) / (w + data.margin_right_cm))))
    rows_needed = int(math.ceil(data.num_copies / designs_per_row))

    used_in_row = w * min(designs_per_row, data.num_copies) + data.margin_right_cm * (min(designs_per_row, data.num_copies) - 1)
    usage_percent = min(used_in_row / data.roll_width_cm * 100.0, 100.0)

    total_height_cm = h * rows_needed + data.margin_top_cm * (rows_needed - 1)
    total_height_m = total_height_cm / 100.0
    cost = total_height_m * data.price_per_meter

    return CalcResult(
        orientation_deg=data.orientation_deg,
        designs_per_row=designs_per_row,
        rows_needed=rows_needed,
        usage_percent=usage_percent,
        total_height_cm=total_height_cm,
        total_height_m=total_height_m,
        cost=cost,
    )


class PresupuestoApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Calculadora de presupuestos DTF")
        root.geometry("820x560")
        root.resizable(False, False)

        # Cargar configuración persistente
        cfg = load_config()

        # Variables de configuración (persisten)
        self.roll_width_cm = tk.DoubleVar(value=cfg["roll_width_cm"])
        self.price_per_meter = tk.DoubleVar(value=cfg["price_per_meter"])
        self.margin_top_cm = tk.DoubleVar(value=cfg["margin_top_cm"])
        self.margin_right_cm = tk.DoubleVar(value=cfg["margin_right_cm"])

        # Entradas de cálculo
        self.image_width_cm = tk.DoubleVar(value=1)
        self.image_height_cm = tk.DoubleVar(value=1)
        self.num_copies = tk.IntVar(value=1)

        # Notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.calc_tab = self._build_calc_tab(self.notebook)
        self.config_tab = self._build_config_tab(self.notebook)

        # Seleccionar Cálculo como pestaña inicial
        self.notebook.select(self.calc_tab)

        # Bind de Enter/KP_Enter según pestaña activa
        self.root.bind("<Return>", self._on_return)
        self.root.bind("<KP_Enter>", self._on_return)

        # Guardar al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----------------------- Tabs ----------------------- #
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

        ttk.Label(
            frame,
            text="Mínimo numérico: 0,10. Copias mínimas: 1.",
            wraplength=480,
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=6, pady=6)

        ttk.Button(frame, text="Guardar configuración", command=self._save_current_config).grid(
            row=5, column=1, sticky=tk.E, padx=6, pady=12
        )
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

        ttk.Button(input_box, text="Calcular", command=self.on_calcular).grid(row=1, column=3, padx=6, pady=6, sticky=tk.E)

        self.result_frame = ttk.Frame(frame)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        return frame

    # ------------------ Atajo Enter ------------------ #
    def _on_return(self, event=None):
        # Decide según la pestaña activa
        current_idx = self.notebook.index(self.notebook.select())
        if current_idx == self.notebook.index(self.calc_tab):
            self.on_calcular()
        else:
            self._save_current_config()

    # ------------------ Persistencia ------------------ #
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

    # -------------------- Cálculo -------------------- #
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


def main() -> None:
    root = tk.Tk()
    PresupuestoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
