# core/placement_strategies.py
# -*- coding: utf-8 -*-
"""
Xonalarni qatorlarga (rows) terish strategiyalari.

Bu modul genomdan kelgan xonalar ro'yxatini oladi va ularni bitta qanot
(masalan, chap qanot) ichida qanday qilib vertikal qatorlarga terishni biladi.
"""

import random
from typing import List, Dict
from core.models import PlacedRoom

# =============================================================================
# 1. XONALARNI QATORLARGA TERISH
# =============================================================================

def pack_wing_rooms(rooms: List[PlacedRoom], wing_width: float, rng: random.Random) -> List[Dict]:
    """
    Bitta qanotdagi xonalarni qatorlarga (rows) taqsimlaydi.
    Qaytaradi: [{"type": "...", "items": [room1, room2], "height": ...}, ...]
    """
    rows: List[Dict] = []
    i = 0
    n = len(rooms)
    
    while i < n:
        rm = rooms[i]
        
        # 1. Ikkita kichik nam xonani (S/U) yonma-yon qo'yish
        if (
            i + 1 < n
            and rm.category in ("wet", "service")
            and rooms[i + 1].category in ("wet", "service")
        ):
            r2 = rooms[i + 1]
            row_h = max(rm.h, r2.h, 1.8)
            rows.append({"type": "double_side_by_side", "items": [rm, r2], "height": row_h})
            i += 2
            
        # 2. Nam xonani (S/U) koridor bilan birga qo'yish (1-rasmdagidek)
        elif rm.category in ("wet", "service") and rm.w <= wing_width - 1.3 and i < n - 1:
            row_h = max(min(rm.h, 1.4), 1.2)
            rows.append({"type": "su_with_corridor", "items": [rm], "height": row_h})
            i += 1
            
        # 3. Oddiy xona (butun qatorni egallaydi)
        else:
            rows.append({"type": "single", "items": [rm], "height": rm.h})
            i += 1
            
    return rows


# =============================================================================
# 2. QATORLARNI BALANDLIKKA CHO'ZISH
# =============================================================================

def stretch_rows_to_height(rows: List[Dict], target_height: float) -> None:
    """
    Qatorlar yig'indisi umumiy uy balandligiga (target_height) teng bo'lishi uchun
    ularni proporsional ravishda cho'zadi yoki qisqartiradi.
    """
    if not rows:
        return
        
    curr_h = sum(r["height"] for r in rows)
    diff = target_height - curr_h
    if abs(diff) < 1e-3:
        return

    # Faqat oddiy xonalarni (yotoqxona, mehmonxona va h.k.) cho'zish mumkin.
    # Kichik S/U larni cho'zish noto'g'ri, chunki ularning o'lchami qat'iy.
    adjustable = [r for r in rows if r["type"] == "single" and r["items"][0].category not in ("wet", "service")]
    if not adjustable:
        adjustable = rows

    total_adj_h = sum(r["height"] for r in adjustable)
    for r in adjustable:
        share = r["height"] / total_adj_h if total_adj_h > 0 else 1.0 / len(adjustable)
        r["height"] = round(max(1.2, r["height"] + diff * share), 2)

    # Yaxlitlashda hosil bo'lgan xatolikni oxirgi qatorga qo'shish
    final_diff = target_height - sum(r["height"] for r in rows)
    rows[-1]["height"] = round(rows[-1]["height"] + final_diff, 2)
