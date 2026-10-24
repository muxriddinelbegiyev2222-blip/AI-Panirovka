# gui/app.py
# -*- coding: utf-8 -*-
"""
Asosiy oyna (Main Application).
"""

import os
import random
import threading
import tkinter as tk
from tkinter import messagebox
from typing import List

from core.models import RoomRequest, HousePlan
from core.genome import create_random_house_genome
from core.genetic_optimizer import GeneticOptimizer
from core.multi_story_planner import build_house_plan
from core.scorer import score_house_plan
from core.floor_planner import build_floor_plan
from renderers.png_renderer import PNGRenderer
from gui.room_editor import RoomEditorPanel
from gui.preview_panel import PreviewPanel
from config.settings import DEFAULT_OUTPUT_DIR

class AIArchitectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI ARXITEKTOR PRO v4.0 — Sun'iy Ong Planlovchisi")
        self.root.geometry("1440x900")
        self.root.configure(bg="#F4F6F9")

        # Papka yaratish
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

        # UI qismlari
        left_frame = tk.Frame(root, bg="#FFFFFF", bd=1, relief="solid", width=380)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(root, bg="#FFFFFF", bd=1, relief="solid")
        right_frame.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)

        self.preview_panel = PreviewPanel(right_frame)
        self.preview_panel.pack(fill="both", expand=True)

        self.room_editor = RoomEditorPanel(left_frame, on_generate=self.start_ai_generation)
        self.room_editor.pack(fill="both", expand=True)

    def start_ai_generation(self, requests: List[RoomRequest], floor_count: int):
        self.room_editor.set_loading(True)
        self.preview_panel.status_label.config(text="AI ishlamoqda... Iltimos kuting.")
        
        # Thread (Oqim) yaratish (Dastur qotib qolmasligi uchun)
        thread = threading.Thread(target=self._run_ai_background, args=(requests, floor_count))
        thread.daemon = True
        thread.start()

    def _run_ai_background(self, requests: List[RoomRequest], floor_count: int):
        try:
            variants = []
            image_paths = {}
            renderer = PNGRenderer()

            # 5 ta mustaqil AI qidiruvi (har biri 10 000+ variantni ko'radi)
            for i in range(5):
                optimizer = GeneticOptimizer(seed=random.randint(1, 999999))
                
                # Baholovchi funksiya (Evaluator)
                def evaluator(genome):
                    house = build_house_plan(genome, requests, variant_index=i+1)
                    score, breakdown = score_house_plan(house)
                    house.ai_score = score
                    house.score_breakdown = breakdown
                    return score, breakdown, house

                result = optimizer.optimize(requests, floor_count, evaluator)
                best_house = result.best_house
                variants.append(best_house)

                # 1-qavatni PNG ga chizish
                png_path = os.path.join(DEFAULT_OUTPUT_DIR, f"Variant_{i+1}.png")
                renderer.render(best_house.stories[0].floorplan, png_path, dpi=150)
                image_paths[i] = png_path

            # UI ni yangilash (Main thread da bajariladi)
            self.root.after(0, self._on_generation_complete, variants, image_paths)

        except Exception as e:
            self.root.after(0, self._on_generation_error, str(e))

    def _on_generation_complete(self, variants: List[HousePlan], image_paths: dict):
        self.room_editor.set_loading(False)
        self.preview_panel.set_data(variants, image_paths)

    def _on_generation_error(self, err_msg: str):
        self.room_editor.set_loading(False)
        messagebox.showerror("AI Xatosi", f"Kutilmagan xatolik yuz berdi:\n{err_msg}")
