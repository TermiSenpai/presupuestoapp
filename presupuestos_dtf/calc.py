# -*- coding: utf-8 -*-
import math
from .models import CalcInput, CalcResult

def compute_layout(data: CalcInput) -> CalcResult:
    if data.orientation_deg not in (0, 90):
        raise ValueError("La orientación debe ser 0 o 90 grados.")

    w = data.image_width_cm if data.orientation_deg == 0 else data.image_height_cm
    h = data.image_height_cm if data.orientation_deg == 0 else data.image_width_cm

    designs_per_row = max(
        1,
        int(math.floor((data.roll_width_cm + data.margin_right_cm) / (w + data.margin_right_cm)))
    )
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
