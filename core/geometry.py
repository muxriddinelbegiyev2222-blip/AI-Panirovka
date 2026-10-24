# core/geometry.py
# -*- coding: utf-8 -*-
"""
Geometriya va fazoviy matematika moduli.

AI (Genetik Algoritm) xonalarni tasodifiy joylashtirganda,
ularning ustma-ust tushmasligi va to'g'ri joylashishini ta'minlaydigan
funksiyalar to'plami.
"""

import math
from typing import List, Tuple, Optional
from core.models import PlacedRoom
from config.settings import PLAN_TOLERANCE

# Turdagi qisqartmalar
BBox = Tuple[float, float, float, float]  # (x1, y1, x2, y2)


# =============================================================================
# 1. BOUNDING BOX (AABB) OPERATSIYALARI
# =============================================================================

def bbox_intersection(a: BBox, b: BBox) -> float:
    """
    Ikki to'rtburchakning kesishish maydonini hisoblaydi.
    Agar kesishmasa, 0.0 qaytaradi.
    """
    x_overlap = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    y_overlap = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return x_overlap * y_overlap


def bbox_intersects(a: BBox, b: BBox, tol: float = PLAN_TOLERANCE) -> bool:
    """Ikki to'rtburchak kesishadimi-yo'qmi tekshiradi."""
    return not (
        a[2] <= b[0] + tol or
        b[2] <= a[0] + tol or
        a[3] <= b[1] + tol or
        b[3] <= a[1] + tol
    )


def bbox_area(b: BBox) -> float:
    """To'rtburchak maydoni."""
    return max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])


def bbox_center(b: BBox) -> Tuple[float, float]:
    """To'rtburchak markazi."""
    return ((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0)


def distance_between_bboxes(a: BBox, b: BBox) -> float:
    """
    Ikki to'rtburchak orasidagi eng qisqa masofa.
    Agar ular kesishsa, 0.0 qaytaradi.
    """
    dx = max(0.0, max(a[0], b[0]) - min(a[2], b[2]))
    dy = max(0.0, max(a[1], b[1]) - min(a[3], b[3]))
    return math.hypot(dx, dy)


# =============================================================================
# 2. XONALAR UCHUN MAXSUS FUNKSIYALAR
# =============================================================================

def check_overlap(rooms: List[PlacedRoom], tol: float = PLAN_TOLERANCE) -> List[Tuple[PlacedRoom, PlacedRoom, float]]:
    """
    Xonalar ro'yxatidagi barcha ustma-ust tushishlarni topadi.
    Qaytaradi: [(room_a, room_b, overlap_area), ...]
    """
    overlaps = []
    n = len(rooms)
    for i in range(n):
        for j in range(i + 1, n):
            area = bbox_intersection(rooms[i].bbox(), rooms[j].bbox())
            if area > (tol * tol):
                overlaps.append((rooms[i], rooms[j], area))
    return overlaps


def find_shared_wall(
    r1: PlacedRoom, 
    r2: PlacedRoom, 
    min_length: float = 0.65,
    tol: float = PLAN_TOLERANCE
) -> Optional[Tuple[str, float, float, float, bool]]:
    """
    Ikki xona orasidagi umumiy devorni topadi.
    
    Qaytaradi: 
        (orientation, wall_coordinate, segment_start, segment_end, r1_is_positive)
        orientation: 'H' (gorizontal) yoki 'V' (vertikal)
        wall_coordinate: devorning X yoki Y koordinatasi
        segment_start, segment_end: devorning boshlanish va tugash nuqtalari
        r1_is_positive: r1 devorning musbat tomonidami (True) yoki manfiydami (False)
    
    Agar umumiy devor topilmasa yoki minimal uzunlikdan qisqa bo'lsa, None qaytaradi.
    """
    # Vertikal devorlar (r1 o'ngda, r2 chapda yoki teskarisi)
    if abs((r1.x + r1.w) - r2.x) < tol:
        s, e = max(r1.y, r2.y), min(r1.y + r1.h, r2.y + r2.h)
        if e - s >= min_length:
            return ("V", r2.x, s, e, False)
            
    if abs(r1.x - (r2.x + r2.w)) < tol:
        s, e = max(r1.y, r2.y), min(r1.y + r1.h, r2.y + r2.h)
        if e - s >= min_length:
            return ("V", r1.x, s, e, True)

    # Gorizontal devorlar (r1 tepada, r2 pastda yoki teskarisi)
    if abs((r1.y + r1.h) - r2.y) < tol:
        s, e = max(r1.x, r2.x), min(r1.x + r1.w, r2.x + r2.w)
        if e - s >= min_length:
            return ("H", r2.y, s, e, False)
            
    if abs(r1.y - (r2.y + r2.h)) < tol:
        s, e = max(r1.x, r2.x), min(r1.x + r1.w, r2.x + r2.w)
        if e - s >= min_length:
            return ("H", r1.y, s, e, True)

    return None


def get_exterior_walls(room: PlacedRoom, total_w: float, total_h: float, tol: float = PLAN_TOLERANCE) -> List[str]:
    """
    Xonaning qaysi tomonlari tashqi (uy chegarasidagi) devorlarga tegishli ekanligini aniqlaydi.
    Qaytaradi: ['bottom', 'left', 'top', 'right'] dan iborat ro'yxat.
    """
    walls = []
    if abs(room.y - 0.0) < tol:
        walls.append("bottom")
    if abs((room.y + room.h) - total_h) < tol:
        walls.append("top")
    if abs(room.x - 0.0) < tol:
        walls.append("left")
    if abs((room.x + room.w) - total_w) < tol:
        walls.append("right")
    return walls


def is_inside_boundary(room: PlacedRoom, total_w: float, total_h: float, tol: float = PLAN_TOLERANCE) -> bool:
    """Xona uyning umumiy chegarasidan chiqib ketmaganligini tekshiradi."""
    return (
        room.x >= -tol and
        room.y >= -tol and
        (room.x + room.w) <= (total_w + tol) and
        (room.y + room.h) <= (total_h + tol)
    )


def calculate_adjacency_graph(rooms: List[PlacedRoom]) -> dict:
    """
    Xonalar orasidagi qo'shnichilik grafigini yaratadi (Graph Theory).
    Bu AI ga xonalarni qanday bog'lashni tushunishga yordam beradi.
    Qaytaradi: {room_id: [neighbor_id1, neighbor_id2, ...]}
    """
    graph = {room.id: [] for room in rooms}
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            if find_shared_wall(rooms[i], rooms[j], min_length=0.1):
                graph[rooms[i].id].append(rooms[j].id)
                graph[rooms[j].id].append(rooms[i].id)
    return graph
