# cli/batch_generator.py
# -*- coding: utf-8 -*-
"""
Ommaviy chizmalar generatori (Batch Generator).

Terminal orqali ishga tushiriladi va ko'rsatilgan miqdorda tasodifiy,
lekin eng mukammal uy chizmalarini yaratib, papkaga saqlaydi.
"""

import os
import time
import random
from typing import List
from core.models import RoomRequest
from core.genetic_optimizer import GeneticOptimizer
from core.multi_story_planner import build_house_plan
from core.scorer import score_house_plan
from renderers.png_renderer import PNGRenderer
from renderers.dxf_exporter import DXFExporter


def run_batch_generation(count: int, output_dir: str, floor_count: int = 1):
    """N ta eng yaxshi chizmalarni yaratish."""
    os.makedirs(output_dir, exist_ok=True)
    print(f"🚀 Ommaviy generatsiya boshlandi. {count} ta chizma yaratiladi...")
    print(f"📁 Saqlanadigan papka: {output_dir}\n")

    # Standart xonalar to'plami (namuna sifatida)
    requests = [
        RoomRequest("mehmonxona", 4.6, 6.0),
        RoomRequest("oshxona", 4.6, 4.0),
        RoomRequest("kattalar_yotoqxonasi", 4.0, 3.6),
        RoomRequest("bolalar_yotoqxonasi", 4.6, 3.0),
        RoomRequest("sanuzel", 2.0, 1.5),
    ]

    renderer = PNGRenderer()

    for i in range(1, count + 1):
        start_time = time.time()
        
        # Har bir chizma uchun mutlaqo yangi AI qidiruvi (yangi seed bilan)
        optimizer = GeneticOptimizer(
            population_size=60,   # Tezroq ishlashi uchun biroz kamaytirildi
            generations=80,
            seed=random.randint(1, 999999)
        )

        def evaluator(genome):
            house = build_house_plan(genome, requests, variant_index=i)
            score, breakdown = score_house_plan(house)
            house.ai_score = score
            return score, breakdown, house

        # AI ni ishga tushirish
        result = optimizer.optimize(requests, floor_count, evaluator)
        best_house = result.best_house

        # Fayllarni saqlash
        base_name = f"AI_House_{i:03d}_Score_{best_house.ai_score:.1f}"
        png_path = os.path.join(output_dir, f"{base_name}.png")
        dxf_path = os.path.join(output_dir, f"{base_name}.dxf")

        renderer.render(best_house.stories[0].floorplan, png_path, dpi=150)
        DXFExporter.export(best_house.stories[0].floorplan, dxf_path)

        elapsed = time.time() - start_time
        print(f"✅ [{i}/{count}] Yaratildi: {base_name} | Vaqt: {elapsed:.1f}s")

    print("\n🎉 Barcha chizmalar muvaffaqiyatli yaratildi!")
