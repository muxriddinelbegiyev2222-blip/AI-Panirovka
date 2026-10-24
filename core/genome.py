# core/genome.py
# -*- coding: utf-8 -*-
"""
Genom (Xromosoma) moduli — Genetik algoritmning DNKsi.

Bu fayl xonalarni qanday qilib "gen" ko'rinishida saqlashni, ularni
mutatsiyaga uchrashini (o'zgarishini) va krossover (chatishtirish) qilishni biladi.
Har bir genom — bu bitta potentsial uy loyihasi.
"""

import random
from typing import List, Dict, Tuple
from core.models import RoomRequest, FloorGenome, HouseGenome
from core.room_catalog import get_room_spec
from config.settings import (
    MIN_HALL_WIDTH, MAX_HALL_WIDTH, 
    MIN_HALL_HEIGHT_RATIO, MAX_HALL_HEIGHT_RATIO
)

# =============================================================================
# 1. YANGI TASODIFIY GENOM YARATISH (INITIALIZATION)
# =============================================================================

def create_random_floor_genome(
    requests: List[RoomRequest], 
    floor_index: int, 
    rng: random.Random
) -> FloorGenome:
    """Bitta qavat uchun mutlaqo tasodifiy, lekin mantiqiy boshlang'ich genom yaratadi."""
    genome = FloorGenome(floor_index=floor_index)
    
    # Xonalarni tasodifiy qanotlarga taqsimlash
    for req in requests:
        spec = get_room_spec(req.room_type)
        
        # Ba'zi mantiqiy qoidalar (Xoll har doim markazda bo'lishi kerak)
        if req.room_type == "xoll":
            genome.wing_assignment[req.room_type] = "center"
            continue
            
        # Tasodifiy tanlov, lekin xona turiga qarab ehtimollikni oshirish
        choices = ["left", "right", "top"]
        weights = [0.4, 0.4, 0.2] # 40% chap, 40% o'ng, 20% tepa
        
        # Katta xonalar (mehmonxona, oshxona) ko'proq old/pastga (chap/o'ng) tushadi
        if spec.category in ("public", "wet"):
            weights = [0.45, 0.45, 0.1]
        elif spec.category == "private":
            weights = [0.35, 0.35, 0.3]
            
        wing = rng.choices(choices, weights=weights, k=1)[0]
        genome.wing_assignment[req.room_type] = wing
        
        # Aylantirish (rotatsiya) ehtimoli 50%
        genome.rotations[req.room_type] = rng.choice([True, False])

    # Xonalarni tartibga solish (shuffle)
    ids = list(genome.wing_assignment.keys())
    for room_id in ids:
        wing = genome.wing_assignment[room_id]
        if wing == "left":
            genome.left_order.append(room_id)
        elif wing == "right":
            genome.right_order.append(room_id)
        elif wing == "top":
            genome.top_order.append(room_id)
            
    rng.shuffle(genome.left_order)
    rng.shuffle(genome.right_order)
    rng.shuffle(genome.top_order)
    
    # Xoll o'lchamlari (mutatsiya uchun ochiq)
    genome.hall_w = rng.uniform(MIN_HALL_WIDTH, MAX_HALL_WIDTH)
    genome.hall_h_ratio = rng.uniform(MIN_HALL_HEIGHT_RATIO, MAX_HALL_HEIGHT_RATIO)
    
    return genome


def create_random_house_genome(
    requests: List[RoomRequest], 
    floor_count: int, 
    rng: random.Random
) -> HouseGenome:
    """Butun uy (1 yoki 2+ qavat) uchun boshlang'ich genom yaratadi."""
    house_genome = HouseGenome()
    
    # Xonalarni qavatlarga taqsimlash (agar 2 qavat bo'lsa)
    # (Hozircha oddiy mantiq: yotoqxonalar 2-qavatga, oshxona 1-qavatga)
    floor_requests: Dict[int, List[RoomRequest]] = {i: [] for i in range(floor_count)}
    
    if floor_count == 1:
        floor_requests[0] = requests
    else:
        for req in requests:
            spec = get_room_spec(req.room_type)
            if spec.preferred_floor == "upper" and floor_count > 1:
                floor_requests[1].append(req)
            elif spec.preferred_floor == "ground":
                floor_requests[0].append(req)
            else:
                # 'any' bo'lsa tasodifiy
                floor_requests[rng.randint(0, floor_count - 1)].append(req)

    for f_idx in range(floor_count):
        f_genome = create_random_floor_genome(floor_requests[f_idx], f_idx, rng)
        house_genome.floor_genomes.append(f_genome)
        
    house_genome.staircase_slot = rng.choice(["left", "center", "right"])
    return house_genome


# =============================================================================
# 2. MUTATSIYA (NASLNING O'ZGARISHI)
# =============================================================================

def mutate_floor_genome(
    genome: FloorGenome, 
    requests: List[RoomRequest], 
    rng: random.Random, 
    mutation_rate: float
) -> FloorGenome:
    """Genomga tasodifiy mutatsiyalar kiritadi (evolyutsiya uchun)."""
    new_genome = genome.copy()
    
    if rng.random() > mutation_rate:
        return new_genome

    # Mutatsiya turlari
    mutation_type = rng.choice([
        "swap_order",      # 2 ta xonani o'rnini almashtirish
        "change_wing",     # Xonani boshqa qanotga ko'chirish
        "toggle_rotation", # Xonani 90 gradusga aylantirish
        "change_hall"      # Xoll o'lchamini o'zgartirish
    ])

    if mutation_type == "swap_order":
        # Tanlangan qanotdagi xonalar tartibini almashtirish
        lists = [new_genome.left_order, new_genome.right_order, new_genome.top_order]
        target_list = rng.choice([l for l in lists if len(l) > 1])
        if target_list:
            i, j = rng.sample(range(len(target_list)), 2)
            target_list[i], target_list[j] = target_list[j], target_list[i]

    elif mutation_type == "change_wing":
        # Bitta xonani bir qanotdan boshqasiga ko'chirish
        all_rooms = new_genome.all_room_ids()
        if all_rooms:
            room_id = rng.choice(all_rooms)
            if room_id == "xoll": return new_genome # Xollni ko'chirib bo'lmaydi
            
            old_wing = new_genome.wing_assignment[room_id]
            new_wing = rng.choice(["left", "right", "top"])
            
            if old_wing != new_wing:
                # Eski ro'yxatdan o'chirish
                if old_wing == "left": new_genome.left_order.remove(room_id)
                elif old_wing == "right": new_genome.right_order.remove(room_id)
                elif old_wing == "top": new_genome.top_order.remove(room_id)
                
                # Yangi ro'yxatga qo'shish (tasodifiy joyga)
                new_genome.wing_assignment[room_id] = new_wing
                if new_wing == "left": new_genome.left_order.insert(rng.randint(0, len(new_genome.left_order)), room_id)
                elif new_wing == "right": new_genome.right_order.insert(rng.randint(0, len(new_genome.right_order)), room_id)
                elif new_wing == "top": new_genome.top_order.insert(rng.randint(0, len(new_genome.top_order)), room_id)

    elif mutation_type == "toggle_rotation":
        # Xonaning eni va bo'yini almashtirish
        all_rooms = new_genome.all_room_ids()
        if all_rooms:
            room_id = rng.choice(all_rooms)
            new_genome.rotations[room_id] = not new_genome.rotations.get(room_id, False)

    elif mutation_type == "change_hall":
        # Xollning parametrlarini siljitish
        if rng.random() < 0.5:
            new_genome.hall_w = max(MIN_HALL_WIDTH, min(MAX_HALL_WIDTH, new_genome.hall_w + rng.uniform(-0.5, 0.5)))
        else:
            new_genome.hall_h_ratio = max(MIN_HALL_HEIGHT_RATIO, min(MAX_HALL_HEIGHT_RATIO, new_genome.hall_h_ratio + rng.uniform(-0.05, 0.05)))

    return new_genome


# =============================================================================
# 3. KROSSOVER (OTA-ONA GENLARINI BIRLASHTIRISH)
# =============================================================================

def crossover_house_genomes(
    parent1: HouseGenome, 
    parent2: HouseGenome, 
    rng: random.Random
) -> Tuple[HouseGenome, HouseGenome]:
    """Ikki ota-onadan ikkita yangi nasl yaratadi (genlarni aralashtirib)."""
    child1 = HouseGenome()
    child2 = HouseGenome()
    
    # Har bir qavat uchun alohida krossover
    for f_idx in range(min(parent1.story_count(), parent2.story_count())):
        p1_floor = parent1.floor_genomes[f_idx]
        p2_floor = parent2.floor_genomes[f_idx]
        
        c1_floor = p1_floor.copy()
        c2_floor = p2_floor.copy()
        
        # Xoll o'lchamlarini o'rtacha qilib olish (yoki tasodifiy birini olish)
        if rng.random() < 0.5:
            c1_floor.hall_w = p2_floor.hall_w
            c2_floor.hall_w = p1_floor.hall_w
            
        # Chap qanot tartibini almashtirish
        if rng.random() < 0.7:
            c1_floor.left_order = list(p2_floor.left_order)
            c2_floor.left_order = list(p1_floor.left_order)
            # Wing assignment ni yangilash
            for rid in c1_floor.left_order: c1_floor.wing_assignment[rid] = "left"
            for rid in c2_floor.left_order: c2_floor.wing_assignment[rid] = "left"

        child1.floor_genomes.append(c1_floor)
        child2.floor_genomes.append(c2_floor)
        
    child1.staircase_slot = rng.choice([parent1.staircase_slot, parent2.staircase_slot])
    child2.staircase_slot = rng.choice([parent1.staircase_slot, parent2.staircase_slot])
    
    return child1, child2
