# -*- coding: utf-8 -*-
import json
import os
import sys
from pathlib import Path
from tkinter import messagebox
from .constants import (
    APP_DIRNAME, CONFIG_FILENAME,
    DEFAULT_ROLL_WIDTH_CM, DEFAULT_PRICE_PER_METER,
    DEFAULT_MARGIN_TOP_CM, DEFAULT_MARGIN_RIGHT_CM,
)

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
