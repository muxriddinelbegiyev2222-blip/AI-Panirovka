# core/multi_story_planner.py
# -*- coding: utf-8 -*-
"""
Ko'p qavatli uylar planirovkasi.

Bu modul 2 yoki undan ortiq qavatli uylarni loyihalashda qavatlarni
bir-biriga bog'laydi va zinapoyalarni (lestnitsa) to'g'ri joylashtiradi.
"""

import random
from typing import List
from core.models import (
    RoomRequest, HouseGenome, HousePlan, StoryPlan, StaircaseSpec, PlacedRoom
)
from core.floor_planner import build_floor_plan
from config.settings import STAIR_TOTAL_WIDTH, STAIR_TOTAL_DEPTH


def build_house_plan(
    genome: HouseGenome, 
    requests: List[RoomRequest], 
    variant_index: int = 1,
    rng: random.Random = None
) -> HousePlan:
    """Butun uyni (barcha qavatlarni) quradi va zinapoyalarni bog'laydi."""
    if rng is None:
        rng = random.Random()

    house = HousePlan(house_id=f"house_{variant_index}")
    
    max_width = 0.0
    max_height = 0.0
    total_area = 0.0
    usable_area = 0.0

    # 1. Har bir qavatni alohida qurish
    for f_idx, f_genome in enumerate(genome.floor_genomes):
        floor_plan = build_floor_plan(
            f_genome, requests, variant_index, 
            f"Qavat {f_idx + 1} (AI)", rng
        )
        
        # Zinapoyani joylashtirish (agar 1 dan ortiq qavat bo'lsa)
        stair = None
        if genome.story_count() > 1:
            # Zinapoyani Xollning o'rtasiga yoki chetiga qo'yish (genomga qarab)
            hall = next((r for r in floor_plan.rooms if r.room_type == "xoll"), None)
            if hall:
                # Zinapoya o'lchami
                st_w = min(STAIR_TOTAL_WIDTH, hall.w * 0.6)
                st_h = min(STAIR_TOTAL_DEPTH, hall.h * 0.5)
                
                # Joylashuv (markazda)
                st_x = hall.x + (hall.w - st_w) / 2.0
                st_y = hall.y + (hall.h - st_h) / 2.0
                
                stair = StaircaseSpec(
                    x=st_x, y=st_y, w=st_w, h=st_h,
                    shape="U", direction="up-down", flight_count=2,
                    connects_floors=(f_idx - 1 if f_idx > 0 else 0, f_idx + 1 if f_idx < genome.story_count()-1 else f_idx)
                )
                floor_plan.staircases.append(stair)

        story = StoryPlan(story_index=f_idx, floorplan=floor_plan, staircase=stair)
        house.stories.append(story)

        # Umumiy o'lchamlarni yangilash
        max_width = max(max_width, floor_plan.total_width)
        max_height = max(max_height, floor_plan.total_height)
        total_area += floor_plan.total_area()
        usable_area += floor_plan.usable_area()

    house.footprint_w = round(max_width, 2)
    house.footprint_h = round(max_height, 2)
    house.total_area = round(total_area, 2)
    house.usable_area = round(usable_area, 2)

    return house
