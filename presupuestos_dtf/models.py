# -*- coding: utf-8 -*-
from dataclasses import dataclass

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
