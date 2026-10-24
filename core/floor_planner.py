# core/floor_planner.py
# -*- coding: utf-8 -*-
"""
Qavat Planlovchisi (Floor Planner).

Bu modul genomni (FloorGenome) oladi va undan haqiqiy chizmani (FloorPlan)
yasaydi. Xonalarni koordinatalarga joylashtiradi, eshiklarni va derazalarni
o'rnatadi.
"""

import random
from typing import List, Dict, Optional

from core.models import (
    RoomRequest, FloorGenome, FloorPlan, PlacedRoom, DoorSpec, WindowSpec
)
from core.room_catalog import get_room_spec
from core.geometry import find_shared_wall, get_exterior_walls
from core.placement_strategies import pack_wing_rooms, stretch_rows_to_height
from config.settings import DEFAULT_EXT_WALL, DEFAULT_INT_WALL, PLAN_TOLERANCE


def build_floor_plan(
    genome: FloorGenome, 
    requests: List[RoomRequest], 
    variant_index: int = 1,
    strategy_name: str = "AI Evolyutsiyasi",
    rng: Optional[random.Random] = None
) -> FloorPlan:
    """Genomni haqiqiy chizma ko'rinishiga keltiradi."""
    if rng is None:
        rng = random.Random()

    req_map = {req.room_type: req for req in requests}

    # 1. PlacedRoom obyektlarini yaratish (Hali x,y yo'q)
    all_placed = {}
    for room_type, wing in genome.wing_assignment.items():
        if room_type == "xoll":
            continue
        req = req_map.get(room_type)
        if not req:
            continue
            
        spec = get_room_spec(room_type)
        w, h = req.width, req.height
        
        # Genomda aylantirish (rotatsiya) belgilangan bo'lsa, eni va bo'yini almashtiramiz
        if genome.rotations.get(room_type, False):
            w, h = h, w
            
        all_placed[room_type] = PlacedRoom(
            id=f"room_{room_type}",
            room_type=room_type,
            label=req.custom_label or spec.name_uz,
            category=spec.category,
            x=0.0, y=0.0, w=w, h=h,
            orig_w=req.width, orig_h=req.height,
            furniture_style=spec.furniture_style,
            needs_window=spec.needs_window,
            wing=wing,
            floor_index=genome.floor_index
        )

    left_rooms = [all_placed[rid] for rid in genome.left_order if rid in all_placed]
    right_rooms = [all_placed[rid] for rid in genome.right_order if rid in all_placed]
    top_rooms = [all_placed[rid] for rid in genome.top_order if rid in all_placed]

    # 2. Qanotlarning kengligini aniqlash
    W_left = max([r.w for r in left_rooms], default=0.0)
    W_right = max([r.w for r in right_rooms], default=0.0)
    
    W_center = genome.hall_w
    if top_rooms:
        top_sum_w = sum(r.w for r in top_rooms)
        W_center = max(W_center, top_sum_w)
        
    # Minimal kengliklarni ta'minlash
    W_left = max(W_left, 3.6) if left_rooms else 0.0
    W_right = max(W_right, 3.6) if right_rooms else 0.0
    W_center = max(W_center, 3.6)
    
    # 3. Qatorlarga terish (packing)
    left_rows = pack_wing_rooms(left_rooms, W_left, rng)
    right_rows = pack_wing_rooms(right_rooms, W_right, rng)

    H_left_raw = sum(row["height"] for row in left_rows)
    H_right_raw = sum(row["height"] for row in right_rows)
    
    # Tepa blok (Top band) balandligi
    H_top = max([r.h for r in top_rooms], default=0.0)
    min_hall_h = 5.5
    
    # Umumiy balandlik eng katta qanot yoki Tepa blok + Xoll yig'indisiga teng bo'ladi
    total_H = max(H_left_raw, H_right_raw, H_top + min_hall_h, 9.0)
    
    # Qatorlarni umumiy balandlikka proporsional cho'zish
    stretch_rows_to_height(left_rows, total_H)
    stretch_rows_to_height(right_rows, total_H)

    # 4. Koordinatalarni berish (Joylashtirish)
    placed_rooms = []
    
    # --- CHAP QANOT ---
    curr_y = 0.0
    for row in left_rows:
        rh = row["height"]
        if row["type"] == "single":
            rm = row["items"][0]
            rm.x, rm.y, rm.w, rm.h = 0.0, curr_y, W_left, rh
            placed_rooms.append(rm)
        elif row["type"] == "su_with_corridor":
            rm = row["items"][0]
            su_w = min(max(rm.orig_w, 1.8), W_left - 1.6)
            rm.x, rm.y, rm.w, rm.h = 0.0, curr_y, su_w, rh
            placed_rooms.append(rm)
            # S/U yonidagi koridor
            placed_rooms.append(PlacedRoom(
                id=f"corridor_{rm.id}", room_type="koridor", label="", category="transit",
                x=su_w, y=curr_y, w=W_left - su_w, h=rh,
                orig_w=W_left - su_w, orig_h=rh, furniture_style="H_branch",
                needs_window=False, wing="corridor"
            ))
        elif row["type"] == "double_side_by_side":
            r1, r2 = row["items"][0], row["items"][1]
            w1 = round(W_left * (r1.orig_w / (r1.orig_w + r2.orig_w)), 2)
            w2 = round(W_left - w1, 2)
            r1.x, r1.y, r1.w, r1.h = 0.0, curr_y, w1, rh
            r2.x, r2.y, r2.w, r2.h = w1, curr_y, w2, rh
            placed_rooms.extend([r1, r2])
        curr_y += rh

    # --- O'NG QANOT ---
    x_right_start = W_left + W_center
    curr_y = 0.0
    for row in right_rows:
        rh = row["height"]
        if row["type"] == "single":
            rm = row["items"][0]
            rm.x, rm.y, rm.w, rm.h = x_right_start, curr_y, W_right, rh
            placed_rooms.append(rm)
        elif row["type"] == "su_with_corridor":
            rm = row["items"][0]
            su_w = min(max(rm.orig_w, 1.8), W_right - 1.6)
            corr_w = W_right - su_w
            placed_rooms.append(PlacedRoom(
                id=f"corridor_{rm.id}", room_type="koridor", label="", category="transit",
                x=x_right_start, y=curr_y, w=corr_w, h=rh,
                orig_w=corr_w, orig_h=rh, furniture_style="H_branch",
                needs_window=False, wing="corridor"
            ))
            rm.x, rm.y, rm.w, rm.h = x_right_start + corr_w, curr_y, su_w, rh
            placed_rooms.append(rm)
        elif row["type"] == "double_side_by_side":
            r1, r2 = row["items"][0], row["items"][1]
            w1 = round(W_right * (r1.orig_w / (r1.orig_w + r2.orig_w)), 2)
            w2 = round(W_right - w1, 2)
            r1.x, r1.y, r1.w, r1.h = x_right_start, curr_y, w1, rh
            r2.x, r2.y, r2.w, r2.h = x_right_start + w1, curr_y, w2, rh
            placed_rooms.extend([r1, r2])
        curr_y += rh

    # --- TEPA BLOK VA MARKAZIY XOLL ---
    if top_rooms:
        tr_h = min(max(r.h for r in top_rooms), total_H * 0.38)
        sum_orig_w = sum(r.orig_w for r in top_rooms)
        cx = W_left
        for idx_t, tr in enumerate(top_rooms):
            tw = round(W_center * (tr.orig_w / sum_orig_w), 2) if idx_t < len(top_rooms) - 1 else round(W_left + W_center - cx, 2)
            tr.x, tr.y, tr.w, tr.h = cx, total_H - tr_h, tw, tr_h
            placed_rooms.append(tr)
            cx += tw
            
        hall_h = total_H - tr_h
        hall_room = PlacedRoom(
            id="central_hall", room_type="xoll", label="XOLL", category="transit",
            x=W_left, y=0.0, w=W_center, h=hall_h,
            orig_w=W_center, orig_h=hall_h, furniture_style="central_hall",
            needs_window=False, wing="center"
        )
        placed_rooms.append(hall_room)
    else:
        hall_room = PlacedRoom(
            id="central_hall", room_type="xoll", label="XOLL", category="transit",
            x=W_left, y=0.0, w=W_center, h=total_H,
            orig_w=W_center, orig_h=total_H, furniture_style="central_hall",
            needs_window=False, wing="center"
        )
        placed_rooms.append(hall_room)

    total_W = W_left + W_center + W_right

    # 5. Eshik va derazalarni generatsiya qilish
    doors = _generate_doors(placed_rooms, total_W, total_H)
    windows = _generate_windows(placed_rooms, total_W, total_H)

    return FloorPlan(
        variant_index=variant_index,
        strategy_name=strategy_name,
        strategy_desc="Genetik Algoritm orqali sintez qilindi",
        floor_index=genome.floor_index,
        total_width=round(total_W, 2),
        total_height=round(total_H, 2),
        ext_wall_thick=DEFAULT_EXT_WALL,
        int_wall_thick=DEFAULT_INT_WALL,
        rooms=placed_rooms,
        doors=doors,
        windows=windows
    )


# =============================================================================
# YORDAMCHI FUNKSIYALAR: ESHIK VA DERAZALAR
# =============================================================================

def _generate_doors(rooms: List[PlacedRoom], total_w: float, total_h: float) -> List[DoorSpec]:
    doors = []
    transit_rooms = [r for r in rooms if r.category == "transit"]
    hall = next((r for r in transit_rooms if r.room_type == "xoll"), None)

    # 1. Asosiy kirish eshigi
    if hall:
        doors.append(DoorSpec(
            x=hall.x + hall.w / 2.0, y=0.0, width=1.4, orientation="H",
            swing_dir="+y", hinge_side="left", is_double=True, is_exterior=True
        ))

    # 2. Har bir xona uchun eshik (Koridor yoki Xoll bilan umumiy devor orqali)
    for rm in rooms:
        if rm.category == "transit":
            continue

        spec = get_room_spec(rm.room_type)
        d_width = min(spec.door_width, min(rm.w, rm.h) * 0.55)
        d_width = max(0.70, round(d_width, 2))

        placed = False
        # Eng avval koridor va xollga qidiramiz
        for tr in transit_rooms:
            shared = find_shared_wall(rm, tr)
            if shared:
                orient, wall_coord, seg_start, seg_end, rm_is_pos = shared
                if seg_end - seg_start >= d_width + 0.14:
                    door_pos = seg_start + (seg_end - seg_start) / 2.0
                    swing = "+y" if rm_is_pos else "-y" if orient == "H" else "+x" if rm_is_pos else "-x"
                    
                    doors.append(DoorSpec(
                        x=door_pos if orient == "H" else wall_coord,
                        y=wall_coord if orient == "H" else door_pos,
                        width=d_width, orientation=orient, swing_dir=swing, hinge_side="left"
                    ))
                    placed = True
                    break
        
        # Agar koridorga eshik ochib bo'lmasa, qo'shni xonaga ochamiz
        if not placed:
            for neighbor in rooms:
                if neighbor.id == rm.id or neighbor.category == "transit":
                    continue
                shared = find_shared_wall(rm, neighbor)
                if shared:
                    orient, wall_coord, seg_start, seg_end, rm_is_pos = shared
                    if seg_end - seg_start >= d_width + 0.10:
                        door_pos = seg_start + (seg_end - seg_start) / 2.0
                        swing = "+y" if rm_is_pos else "-y" if orient == "H" else "+x" if rm_is_pos else "-x"
                        doors.append(DoorSpec(
                            x=door_pos if orient == "H" else wall_coord,
                            y=wall_coord if orient == "H" else door_pos,
                            width=d_width, orientation=orient, swing_dir=swing, hinge_side="right"
                        ))
                        break
    return doors


def _generate_windows(rooms: List[PlacedRoom], total_w: float, total_h: float) -> List[WindowSpec]:
    windows = []
    for rm in rooms:
        if rm.category == "transit" or not rm.needs_window:
            continue

        ext_walls = get_exterior_walls(rm, total_w, total_h)
        for wall in ext_walls:
            if wall == "bottom":
                w_len = min(1.8, rm.w * 0.5)
                windows.append(WindowSpec(x=rm.x + rm.w/2, y=0.0, length=w_len, orientation="H", wall_side="bottom", room_id=rm.id))
                break # Bitta deraza yetarli
            elif wall == "top":
                w_len = min(1.8, rm.w * 0.5)
                windows.append(WindowSpec(x=rm.x + rm.w/2, y=total_h, length=w_len, orientation="H", wall_side="top", room_id=rm.id))
                break
            elif wall == "left":
                w_len = min(1.8, rm.h * 0.5)
                windows.append(WindowSpec(x=0.0, y=rm.y + rm.h/2, length=w_len, orientation="V", wall_side="left", room_id=rm.id))
                break
            elif wall == "right":
                w_len = min(1.8, rm.h * 0.5)
                windows.append(WindowSpec(x=total_w, y=rm.y + rm.h/2, length=w_len, orientation="V", wall_side="right", room_id=rm.id))
                break
    return windows
