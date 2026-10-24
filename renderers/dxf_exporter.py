# renderers/dxf_exporter.py
# -*- coding: utf-8 -*-
"""
AutoCAD DXF Eksportchisi.

Bu modul uy rejasini avtomatik ravishda chiziqlar va matnlardan iborat
DXF (Drawing Exchange Format) fayliga aylantiradi.
"""

import os
from typing import List
from core.models import FloorPlan


class DXFExporter:
    @staticmethod
    def export(plan: FloorPlan, filepath: str) -> str:
        lines: List[str] = []

        def add(code: int, val):
            lines.append(str(code))
            lines.append(str(val))

        add(0, "SECTION")
        add(2, "ENTITIES")

        def draw_rect_mm(x_m, y_m, w_m, h_m, layer: str, color: int = 7):
            x1, y1 = round(x_m * 1000, 1), round(y_m * 1000, 1)
            x2, y2 = round((x_m + w_m) * 1000, 1), round((y_m + h_m) * 1000, 1)
            pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
            for i in range(4):
                add(0, "LINE")
                add(8, layer)
                add(62, color)
                add(10, pts[i][0])
                add(20, pts[i][1])
                add(30, 0.0)
                add(11, pts[i+1][0])
                add(21, pts[i+1][1])
                add(31, 0.0)

        def draw_text_mm(x_m, y_m, text_str: str, height_mm: float, layer: str, color: int = 7):
            add(0, "TEXT")
            add(8, layer)
            add(62, color)
            add(10, round(x_m * 1000, 1))
            add(20, round(y_m * 1000, 1))
            add(30, 0.0)
            add(40, height_mm)
            add(1, text_str.replace("\n", " "))

        # Tashqi va ichki devorlar
        ew = plan.ext_wall_thick
        draw_rect_mm(-ew, -ew, plan.total_width + 2*ew, plan.total_height + 2*ew, "WALLS_EXT", 7)
        
        for rm in plan.rooms:
            draw_rect_mm(rm.x, rm.y, rm.w, rm.h, "WALLS_INT", 7)
            if rm.label:
                draw_text_mm(rm.x + rm.w*0.25, rm.y + rm.h*0.5, f"{rm.label} ({int(rm.w*1000)}x{int(rm.h*1000)})", 200.0, "ROOM_LABELS", 3)

        # Derazalar
        for win in plan.windows:
            if win.orientation == "H":
                draw_rect_mm(win.x - win.length/2, win.y - 0.1, win.length, 0.2, "WINDOWS", 4)
            else:
                draw_rect_mm(win.x - 0.1, win.y - win.length/2, 0.2, win.length, "WINDOWS", 4)

        # Eshiklar
        for d in plan.doors:
            draw_rect_mm(d.x - d.width/2, d.y - 0.1, d.width, 0.2, "DOORS", 30)
            
        # Zinapoyalar
        for st in plan.staircases:
            draw_rect_mm(st.x, st.y, st.w, st.h, "STAIRS", 5)

        add(0, "ENDSEC")
        add(0, "EOF")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return filepath
