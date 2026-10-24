# gui/preview_panel.py
# -*- coding: utf-8 -*-
"""
Chizmalarni ko'rish va yuklab olish paneli.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from typing import List, Dict
from core.models import HousePlan
from renderers.pdf_renderer import PDFRenderer
from renderers.dxf_exporter import DXFExporter

class PreviewPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.variants: List[HousePlan] = []
        self.image_paths: Dict[int, str] = {}
        self.current_idx = 0
        self._build_ui()

    def _build_ui(self):
        # Tepa panel (Variantlar)
        top_bar = tk.Frame(self, bg="#F0F4F8", height=45)
        top_bar.pack(fill="x", side="top")
        
        self.variant_buttons = []
        for i in range(5):
            btn = tk.Button(
                top_bar, text=f"Variant #{i+1}", command=lambda idx=i: self.show_variant(idx),
                bg="#0E7C90", fg="white", font=("Segoe UI", 9, "bold"), padx=12, pady=5
            )
            btn.pack(side="left", padx=5, pady=8)
            self.variant_buttons.append(btn)

        # Pastki panel (Yuklab olish)
        bottom_bar = tk.Frame(self, bg="#F0F4F8", height=45)
        bottom_bar.pack(fill="x", side="bottom")
        
        tk.Button(bottom_bar, text="PNG saqlash", command=self._save_png, bg="#2E9B3C", fg="white", font=("Segoe UI", 9, "bold"), padx=10).pack(side="left", padx=10, pady=8)
        tk.Button(bottom_bar, text="PDF saqlash", command=self._save_pdf, bg="#2E9B3C", fg="white", font=("Segoe UI", 9, "bold"), padx=10).pack(side="left", padx=5, pady=8)
        tk.Button(bottom_bar, text="DXF (AutoCAD) saqlash", command=self._save_dxf, bg="#2E9B3C", fg="white", font=("Segoe UI", 9, "bold"), padx=10).pack(side="left", padx=5, pady=8)

        self.status_label = tk.Label(bottom_bar, text="Tayyor", bg="#F0F4F8", font=("Segoe UI", 9, "italic"))
        self.status_label.pack(side="right", padx=10)

        # Rasm ko'rsatish joyi
        self.canvas = tk.Label(self, bg="#FFFFFF", text="AI natijalari shu yerda paydo bo'ladi...", font=("Segoe UI", 12, "italic"), fg="#999999")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)

    def set_data(self, variants: List[HousePlan], image_paths: Dict[int, str]):
        self.variants = variants
        self.image_paths = image_paths
        self.current_idx = 0
        self.show_variant(0)

    def show_variant(self, idx: int):
        if idx not in self.image_paths:
            return
        self.current_idx = idx
        
        # Tugmalar rangini yangilash
        for i, btn in enumerate(self.variant_buttons):
            btn.config(bg="#0E7C90" if i == idx else "#627D98")

        # Rasmni yuklash
        path = self.image_paths[idx]
        if not os.path.exists(path):
            return
            
        img = Image.open(path)
        img.thumbnail((900, 700), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)
        self.canvas.configure(image=tk_img, text="")
        self.canvas.image = tk_img
        
        # Statusni yangilash
        plan = self.variants[idx]
        self.status_label.config(text=f"Variant #{idx+1} | Qavatlar: {len(plan.stories)} | Ball: {plan.ai_score}/100")

    def _save_png(self):
        if not self.variants: return
        self._copy_file(self.image_paths[self.current_idx], "PNG")

    def _save_pdf(self):
        if not self.variants: return
        self.status_label.config(text="PDF yaratilmoqda...")
        self.update()
        try:
            # Hozircha bitta qavatni (birinchisini) saqlaymiz
            plan = self.variants[self.current_idx].stories[0].floorplan
            out_path = f"Variant_{self.current_idx+1}.pdf"
            PDFRenderer().render(plan, out_path)
            messagebox.showinfo("Muvaffaqiyat", f"PDF saqlandi: {out_path}")
            self.status_label.config(text="PDF tayyor")
        except Exception as e:
            messagebox.showerror("Xatolik", str(e))
            self.status_label.config(text="Xatolik")

    def _save_dxf(self):
        if not self.variants: return
        try:
            plan = self.variants[self.current_idx].stories[0].floorplan
            out_path = f"Variant_{self.current_idx+1}.dxf"
            DXFExporter.export(plan, out_path)
            messagebox.showinfo("Muvaffaqiyat", f"DXF saqlandi: {out_path}")
            self.status_label.config(text="DXF tayyor")
        except Exception as e:
            messagebox.showerror("Xatolik", str(e))

    def _copy_file(self, src, fmt):
        import shutil
        dst = f"Variant_{self.current_idx+1}.{fmt.lower()}"
        shutil.copy(src, dst)
        messagebox.showinfo("Muvaffaqiyat", f"{fmt} saqlandi: {dst}")
