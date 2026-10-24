# core/validator.py
# -*- coding: utf-8 -*-
"""
Qavat rejasini tekshirish va validatsiya qilish moduli.

Bu modul chizmaning arxitektura qonunlariga va SHNQ me'yorlariga
qat'iy mos kelishini ta'minlaydi.
"""

from typing import List
from core.models import FloorPlan, ValidationReport, ValidationIssue
from core.geometry import check_overlap, is_inside_boundary
from core.room_catalog import get_room_spec
from config.settings import PLAN_TOLERANCE, MAX_ROOM_COUNT


def validate_floor_plan(plan: FloorPlan) -> ValidationReport:
    """Bitta qavat chizmasini har tomonlama tekshiradi."""
    report = ValidationReport()
    
    # 1. Xonalar soni yetarlimi?
    if len(plan.rooms) > MAX_ROOM_COUNT:
        report.add(ValidationIssue(
            severity="warning", code="TOO_MANY_ROOMS",
            message=f"Xonalar soni juda ko'p ({len(plan.rooms)} ta). Bu AI ishlashini sekinlashtirishi mumkin.",
            floor_index=plan.floor_index
        ))

    # 2. Ustma-ust tushish (Overlap) tekshiruvi
    overlaps = check_overlap(plan.rooms, tol=PLAN_TOLERANCE)
    for r1, r2, area in overlaps:
        report.add(ValidationIssue(
            severity="error", code="OVERLAP",
            message=f"Xonalar ustma-ust tushgan: {r1.id} va {r2.id} ({area:.2f} m²)",
            room_ids=(r1.id, r2.id),
            floor_index=plan.floor_index
        ))

    # 3. Uy chegarasidan chiqib ketish tekshiruvi
    for rm in plan.rooms:
        if not is_inside_boundary(rm, plan.total_width, plan.total_height):
            report.add(ValidationIssue(
                severity="error", code="OUT_OF_BOUNDS",
                message=f"Xona uy chegarasidan chiqib ketgan: {rm.id}",
                room_ids=(rm.id,),
                floor_index=plan.floor_index
            ))

    # 4. SHNQ minimal o'lchovlar tekshiruvi
    for rm in plan.rooms:
        if rm.category == "transit":
            continue
            
        spec = get_room_spec(rm.room_type)
        if rm.w < spec.min_w or rm.h < spec.min_h:
            report.add(ValidationIssue(
                severity="warning", code="TOO_SMALL",
                message=f"Xona SHNQ me'yoridan kichik: {rm.id} ({rm.w:.2f}x{rm.h:.2f}m). "
                        f"Minimal: {spec.min_w}x{spec.min_h}m",
                room_ids=(rm.id,),
                floor_index=plan.floor_index
            ))

    # 5. Har bir xonada eshik borligini tekshirish
    for rm in plan.rooms:
        if rm.category == "transit":
            continue
        
        has_door = any(
            rm.id in (d.connects_rooms[0], d.connects_rooms[1]) or 
            (d.x >= rm.x and d.x <= rm.x+rm.w and d.y >= rm.y and d.y <= rm.y+rm.h)
            for d in plan.doors
        )
        # Soddalashtirilgan tekshiruv: agar xonaga tegishli eshik umuman yo'q bo'lsa
        if not has_door:
            report.add(ValidationIssue(
                severity="error", code="NO_DOOR",
                message=f"Xonaga eshik o'rnatilmagan: {rm.id}",
                room_ids=(rm.id,),
                floor_index=plan.floor_index
            ))

    return report
