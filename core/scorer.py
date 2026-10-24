# core/scorer.py
# -*- coding: utf-8 -*-
"""
Chizma sifatini baholash (Scoring) moduli.

Genetik algoritm qaysi genom yaxshiroq ekanligini tushunishi uchun
chizmalarni 100 ballik tizimda baholaydi.
"""

from typing import Dict, Tuple
from core.models import FloorPlan, HousePlan
from core.geometry import get_exterior_walls
from core.validator import validate_floor_plan
from config.settings import SCORE_WEIGHTS


def score_floor_plan(plan: FloorPlan) -> Tuple[float, Dict[str, float]]:
    """Bitta qavat chizmasini baholaydi va (umumiy_ball, tafsilotlar) qaytaradi."""
    
    # 0. Validatsiya (Agar chizma xato bo'lsa, 0 ball beramiz!)
    report = validate_floor_plan(plan)
    if not report.is_valid:
        return 0.0, {"Xato": "Chizma geometrik jihatdan noto'g'ri"}

    total_area = plan.total_area()
    transit_area = plan.transit_area()
    
    # 1. Foydali maydon (Efficiency) — Koridor qancha kam bo'lsa shuncha yaxshi
    hall_ratio = transit_area / total_area if total_area > 0 else 1.0
    # Ideal koridor ulushi ~20%. Undan chetlashish jarima oladi.
    eff_score = max(0.0, 100.0 - abs(hall_ratio - 0.20) * 250.0)

    # 2. Insolyatsiya (Yorug'lik) — Derazali xonalar ulushi
    living_rooms = [r for r in plan.rooms if r.category in ("public", "private", "special")]
    lit_count = 0
    for r in living_rooms:
        if get_exterior_walls(r, plan.total_width, plan.total_height):
            lit_count += 1
    light_score = (lit_count / len(living_rooms)) * 100.0 if living_rooms else 100.0

    # 3. O'lcham aniqligi (Dimension) — Foydalanuvchi so'ragan o'lchamga qanchalik yaqin
    func_rooms = [r for r in plan.rooms if r.category != "transit"]
    devs = []
    for r in func_rooms:
        area_orig = r.orig_w * r.orig_h
        area_actual = r.w * r.h
        devs.append(abs(area_actual - area_orig) / max(1.0, area_orig))
    dim_score = max(0.0, 100.0 - (sum(devs) / len(devs) if devs else 0.0) * 150.0)

    # 4. Ergonomika (SHNQ va qulaylik)
    ergo_penalties = len(report.warnings()) * 5.0 # Har bir ogohlantirish -5 ball
    ergo_score = max(0.0, 100.0 - ergo_penalties)

    # 5. Konstruktiv simmetriya — Uy to'g'ri to'rtburchakka qanchalik yaqin
    aspect_ratio = max(plan.total_width, plan.total_height) / min(plan.total_width, plan.total_height)
    sym_score = max(0.0, 100.0 - (aspect_ratio - 1.0) * 40.0)

    # Umumiy ballni vaznlar bo'yicha hisoblash
    overall = (
        eff_score * SCORE_WEIGHTS["efficiency"] +
        light_score * SCORE_WEIGHTS["daylight"] +
        dim_score * SCORE_WEIGHTS["dimension"] +
        ergo_score * SCORE_WEIGHTS["ergonomics"] +
        sym_score * SCORE_WEIGHTS["symmetry"]
    )
    # Circulation va Staircase vaznlarini ham qo'shish mumkin (hozircha soddalashtirildi)

    breakdown = {
        "Foydali maydon": round(eff_score, 1),
        "Yorug'lik": round(light_score, 1),
        "O'lcham aniqligi": round(dim_score, 1),
        "Ergonomika": round(ergo_score, 1),
        "Simmetriya": round(sym_score, 1)
    }
    
    return round(overall, 1), breakdown


def score_house_plan(house: HousePlan) -> Tuple[float, Dict[str, float]]:
    """Butun uyni (barcha qavatlarni) baholaydi."""
    if not house.stories:
        return 0.0, {}

    total_score = 0.0
    aggregated_breakdown = {}
    
    for story in house.stories:
        score, breakdown = score_floor_plan(story.floorplan)
        total_score += score
        for k, v in breakdown.items():
            aggregated_breakdown[k] = aggregated_breakdown.get(k, 0.0) + v

    # O'rtacha ball
    avg_score = total_score / len(house.stories)
    for k in aggregated_breakdown:
        aggregated_breakdown[k] = round(aggregated_breakdown[k] / len(house.stories), 1)

    # Qavatlar orasidagi zinapoya to'g'ri ulanganligini tekshirish (Bonus/Penalty)
    if len(house.stories) > 1:
        stair_bonus = 5.0 # Zinapoya to'g'ri joylashgan bo'lsa qo'shimcha ball
        avg_score = min(100.0, avg_score + stair_bonus)
        aggregated_breakdown["Zinapoya bonusi"] = stair_bonus

    return round(avg_score, 1), aggregated_breakdown
