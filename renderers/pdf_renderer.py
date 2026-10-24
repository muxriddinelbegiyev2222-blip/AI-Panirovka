# renderers/pdf_renderer.py
# -*- coding: utf-8 -*-
"""
PDF Renderer — Chizmalarni chop etish uchun PDF formatida saqlash.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from core.models import FloorPlan
from renderers.png_renderer import PNGRenderer


class PDFRenderer:
    def __init__(self):
        self.png_renderer = PNGRenderer()

    def render(self, plan: FloorPlan, output_path: str) -> str:
        """Chizmani PDF formatida saqlaydi."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Matplotlib vaqtinchalik fayl ochib, uni PDF sahifasiga aylantiramiz
        with PdfPages(output_path) as pdf:
            # PNG rendererning sozlamalarini qayta ishlatamiz, lekin saqlashni PDF ga yo'naltiramiz
            fig, ax = plt.subplots(figsize=(14, 10))
            fig.patch.set_facecolor("white")
            
            # Rendererni chaqiramiz (u o'zi fig yaratadi, lekin biz uni qayta ishlatishimiz kerak)
            # Soddalik uchun PNG rendererni ishlatib, keyin rasmni PDF ga joylaymiz
            temp_png = output_path.replace(".pdf", "_temp.png")
            self.png_renderer.render(plan, temp_png, dpi=150)
            
            img = plt.imread(temp_png)
            ax.imshow(img)
            ax.axis("off")
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
            
            if os.path.exists(temp_png):
                os.remove(temp_png)
                
        return output_path
