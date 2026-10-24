# renderers/png_renderer.py
# -*- coding: utf-8 -*-
"""
PNG Renderer — Chizmalarni yuqori aniqlikda rasmga aylantirish.

Matplotlib yordamida chizma elementlarini (devor, eshik, deraza, mebel,
o'lcham chiziqlari) professional arxitektura uslubida chizadi.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List

from core.models import FloorPlan, PlacedRoom
from config.settings import (
    COLOR_BG, COLOR_WALL, COLOR_FURNITURE, COLOR_FURNITURE_FILL,
    COLOR_DOOR, COLOR_DOOR_EXTERIOR, COLOR_WINDOW_GLASS, COLOR_DIM,
    COLOR_TEXT, COLOR_STAIR, COLOR_CORRIDOR_FILL, COLOR_GARDEN
)


class PNGRenderer:
    def __init__(self):
        self.font_family = "sans-serif"

    def render(self, plan: FloorPlan, output_path: str, dpi: int = 200, show_banner: bool = True) -> str:
        """Bitta qavat chizmasini PNG faylga saqlaydi."""
        W = plan.total_width
        H = plan.total_height
        ew = plan.ext_wall_thick
        iw = plan.int_wall_thick

        margin_l, margin_r, margin_b, margin_t = 2.5, 2.0, 2.5, 2.5
        fig_w = (W + margin_l + margin_r) * 0.7
        fig_h = (H + margin_b + margin_t) * 0.7
        
        fig, ax = plt.subplots(figsize=(max(10, fig_w), max(10, fig_h)), dpi=dpi)
        fig.patch.set_facecolor(COLOR_BG)
        ax.set_facecolor(COLOR_BG)

        # 1. Xonalar va mebellar
        for rm in plan.rooms:
            if rm.category == "transit":
                if rm.room_type == "xoll":
                    self._draw_hall(ax, rm)
                elif rm.wing == "corridor":
                    self._draw_corridor(ax, rm)
            else:
                self._draw_room_furniture(ax, rm)
                self._draw_room_label_and_dims(ax, rm)

        # 2. Devorlar
        self._draw_walls(ax, plan)

        # 3. Derazalar
        self._draw_windows(ax, plan)

        # 4. Eshiklar
        self._draw_doors(ax, plan)

        # 5. Zinapoyalar (agar bo'lsa)
        for stair in plan.staircases:
            self._draw_staircase(ax, stair)

        # 6. Tashqi gabarit o'lchamlari
        self._draw_external_dimensions(ax, W, H, ew)

        # 7. Sarlavha (Banner)
        if show_banner:
            self._draw_banner(ax, plan, W, H, margin_t)

        ax.set_xlim(-margin_l, W + margin_r)
        ax.set_ylim(-margin_b, H + margin_t)
        ax.set_aspect("equal")
        ax.axis("off")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        plt.tight_layout(pad=0.2)
        fig.savefig(output_path, dpi=dpi, facecolor=COLOR_BG, bbox_inches="tight")
        plt.close(fig)
        return output_path

    def _draw_walls(self, ax, plan: FloorPlan):
        W, H, ew, iw = plan.total_width, plan.total_height, plan.ext_wall_thick, plan.int_wall_thick
        
        # Tashqi devorlar
        ax.add_patch(patches.Rectangle((-ew, -ew), W + 2*ew, ew, facecolor=COLOR_WALL, zorder=10))
        ax.add_patch(patches.Rectangle((-ew, H), W + 2*ew, ew, facecolor=COLOR_WALL, zorder=10))
        ax.add_patch(patches.Rectangle((-ew, -ew), ew, H + 2*ew, facecolor=COLOR_WALL, zorder=10))
        ax.add_patch(patches.Rectangle((W, -ew), ew, H + 2*ew, facecolor=COLOR_WALL, zorder=10))

        # Ichki devorlar (xonalar orasidagi)
        rooms = plan.rooms
        for i, r1 in enumerate(rooms):
            for r2 in rooms[i+1:]:
                if r1.category == "transit" and r2.category == "transit": continue
                
                shared = self._get_shared_segment(r1, r2)
                if shared:
                    orient, coord, s, e = shared
                    t = 0.26 if (r1.room_type == "xoll" or r2.room_type == "xoll") else iw
                    if orient == "V":
                        ax.add_patch(patches.Rectangle((coord - t/2, s - t/2), t, (e-s)+t, facecolor=COLOR_WALL, zorder=10))
                    else:
                        ax.add_patch(patches.Rectangle((s - t/2, coord - t/2), (e-s)+t, t, facecolor=COLOR_WALL, zorder=10))

    def _get_shared_segment(self, r1: PlacedRoom, r2: PlacedRoom, tol=0.04):
        if abs((r1.x + r1.w) - r2.x) < tol:
            s, e = max(r1.y, r2.y), min(r1.y + r1.h, r2.y + r2.h)
            if e - s > 0.05: return ("V", r2.x, s, e)
        if abs(r1.x - (r2.x + r2.w)) < tol:
            s, e = max(r1.y, r2.y), min(r1.y + r1.h, r2.y + r2.h)
            if e - s > 0.05: return ("V", r1.x, s, e)
        if abs((r1.y + r1.h) - r2.y) < tol:
            s, e = max(r1.x, r2.x), min(r1.x + r1.w, r2.x + r2.w)
            if e - s > 0.05: return ("H", r2.y, s, e)
        if abs(r1.y - (r2.y + r2.h)) < tol:
            s, e = max(r1.x, r2.x), min(r1.x + r1.w, r2.x + r2.w)
            if e - s > 0.05: return ("H", r1.y, s, e)
        return None

    def _draw_windows(self, ax, plan: FloorPlan):
        W, H, ew = plan.total_width, plan.total_height, plan.ext_wall_thick
        for win in plan.windows:
            half = win.length / 2.0
            if win.orientation == "H":
                wy = -ew if win.wall_side == "bottom" else H
                ax.add_patch(patches.Rectangle((win.x - half, wy), win.length, ew, facecolor=COLOR_BG, edgecolor=COLOR_WALL, lw=1.0, zorder=15))
                for frac in [0.28, 0.5, 0.72]:
                    ax.plot([win.x - half, win.x + half], [wy + ew*frac, wy + ew*frac], color=COLOR_WINDOW_GLASS, lw=1.2 if frac==0.5 else 0.8, zorder=16)
            else:
                wx = -ew if win.wall_side == "left" else W
                ax.add_patch(patches.Rectangle((wx, win.y - half), ew, win.length, facecolor=COLOR_BG, edgecolor=COLOR_WALL, lw=1.0, zorder=15))
                for frac in [0.28, 0.5, 0.72]:
                    ax.plot([wx + ew*frac, wx + ew*frac], [win.y - half, win.y + half], color=COLOR_WINDOW_GLASS, lw=1.2 if frac==0.5 else 0.8, zorder=16)

    def _draw_doors(self, ax, plan: FloorPlan):
        ew = plan.ext_wall_thick
        for d in plan.doors:
            t = ew + 0.04 if d.is_exterior else 0.30
            half = d.width / 2.0
            color = COLOR_DOOR_EXTERIOR if d.is_exterior else COLOR_DOOR
            
            if d.orientation == "H":
                wy = -ew/2 if (d.is_exterior and d.y < 0.1) else (plan.total_height + ew/2 if d.is_exterior else d.y)
                ax.add_patch(patches.Rectangle((d.x - half, wy - t/2), d.width, t, facecolor=COLOR_BG, edgecolor="none", zorder=18))
                sgn = 1.0 if d.swing_dir == "+y" else -1.0
                
                if d.is_double:
                    leaf = d.width / 2.0
                    hx1 = d.x - half
                    hx2 = d.x + half
                    ax.plot([hx1, hx1 + leaf*0.7], [d.y, d.y + sgn*leaf*0.7], color=color, lw=1.5, zorder=20)
                    ax.plot([hx2, hx2 - leaf*0.7], [d.y, d.y + sgn*leaf*0.7], color=color, lw=1.5, zorder=20)
                else:
                    hx = d.x - half if d.hinge_side == "left" else d.x + half
                    dir_x = 1.0 if d.hinge_side == "left" else -1.0
                    ax.plot([hx, hx + dir_x*d.width*0.72], [d.y, d.y + sgn*d.width*0.72], color=color, lw=1.6, zorder=20)
            else:
                ax.add_patch(patches.Rectangle((d.x - t/2, d.y - half), t, d.width, facecolor=COLOR_BG, edgecolor="none", zorder=18))
                sgn = 1.0 if d.swing_dir == "+x" else -1.0
                hy = d.y - half if d.hinge_side == "left" else d.y + half
                dir_y = 1.0 if d.hinge_side == "left" else -1.0
                ax.plot([d.x, d.x + sgn*d.width*0.72], [hy, hy + dir_y*d.width*0.72], color=color, lw=1.6, zorder=20)

    def _draw_staircase(self, ax, stair):
        ax.add_patch(patches.Rectangle((stair.x, stair.y), stair.w, stair.h, facecolor="#F5F5F5", edgecolor=COLOR_STAIR, lw=1.2, zorder=6))
        n_steps = 10
        for i in range(1, n_steps):
            ax.plot([stair.x, stair.x + stair.w], [stair.y + i*(stair.h/n_steps), stair.y + i*(stair.h/n_steps)], color=COLOR_STAIR, lw=0.8, zorder=7)

    def _draw_room_furniture(self, ax, rm: PlacedRoom):
        # (Oldingi koddagi mebel chizish mantiqlari soddalashtirilgan holda saqlanadi)
        pad = 0.22
        if rm.w - 2*pad <= 0.6 or rm.h - 2*pad <= 0.6: return
        c, fc = COLOR_FURNITURE, COLOR_FURNITURE_FILL
        
        if rm.furniture_style == "master_bedroom":
            bw, bl = 1.75, 2.05
            bx = rm.x + (rm.w - bw)/2
            by = rm.y + rm.h - bl - 0.2
            ax.add_patch(patches.Rectangle((bx, by), bw, bl, facecolor=fc, edgecolor=c, lw=1.2, zorder=5))
            ax.add_patch(patches.Rectangle((bx + 0.1, by + bl - 0.4), 0.6, 0.3, facecolor="white", edgecolor=c, lw=0.8, zorder=6))
            ax.add_patch(patches.Rectangle((bx + bw - 0.7, by + bl - 0.4), 0.6, 0.3, facecolor="white", edgecolor=c, lw=0.8, zorder=6))
            
        elif rm.furniture_style == "kitchen_dining":
            ax.add_patch(patches.Rectangle((rm.x + 0.2, rm.y + 0.2), 0.6, rm.h - 0.4, facecolor=fc, edgecolor=c, lw=1.2, zorder=5))
            ax.add_patch(patches.Rectangle((rm.x + rm.w - 1.2, rm.y + rm.h/2 - 0.75), 0.9, 1.5, facecolor=fc, edgecolor=c, lw=1.2, zorder=5))

    def _draw_room_label_and_dims(self, ax, rm: PlacedRoom):
        w_mm, h_mm = int(round(rm.w * 1000)), int(round(rm.h * 1000))
        ax.text(rm.x + rm.w/2, rm.y + rm.h/2, rm.label, ha="center", va="center", fontsize=9, fontweight="bold", color=COLOR_TEXT, bbox=dict(boxstyle="round,pad=0.1", facecolor="white", edgecolor="none", alpha=0.8), zorder=25)
        
        # Oddiy o'lcham chiziqlari
        ax.plot([rm.x + 0.15, rm.x + rm.w - 0.15], [rm.y + 0.3, rm.y + 0.3], color=COLOR_DIM, lw=0.6, zorder=22)
        ax.text(rm.x + rm.w/2, rm.y + 0.35, f"{w_mm}", ha="center", va="bottom", fontsize=7, color=COLOR_DIM, zorder=24)

    def _draw_hall(self, ax, rm: PlacedRoom):
        ax.text(rm.x + rm.w/2, rm.y + rm.h/2, "XOLL", ha="center", va="center", fontsize=11, fontweight="bold", zorder=25)
        ax.plot([rm.x + 0.2, rm.x + rm.w - 0.2], [rm.y + rm.h/2 - 0.5, rm.y + rm.h/2 - 0.5], color=COLOR_DIM, lw=0.6)

    def _draw_corridor(self, ax, rm: PlacedRoom):
        ax.add_patch(patches.Rectangle((rm.x, rm.y), rm.w, rm.h, facecolor=COLOR_CORRIDOR_FILL, edgecolor="none", zorder=2))

    def _draw_external_dimensions(self, ax, W, H, ew):
        # Chap tomondagi balandlik
        ax.plot([-ew - 0.8, -ew - 0.8], [0, H], color=COLOR_DIM, lw=0.8)
        ax.text(-ew - 0.9, H/2, f"{int(H*1000)}", rotation=90, ha="right", va="center", fontsize=9, fontweight="bold")
        # Tepa tomondagi en
        ax.plot([0, W], [H + ew + 0.8, H + ew + 0.8], color=COLOR_DIM, lw=0.8)
        ax.text(W/2, H + ew + 0.9, f"{int(W*1000)}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    def _draw_banner(self, ax, plan, W, H, margin_t):
        title = f"AI VARIANT | Ball: {plan.ai_score}/100 | Gabarit: {int(plan.total_width*1000)}x{int(plan.total_height*1000)} mm"
        ax.text(W/2, H + margin_t - 0.2, title, ha="center", va="top", fontsize=11, fontweight="bold", color="#102A43", bbox=dict(boxstyle="round,pad=0.4", facecolor="#F4F9FC", edgecolor=COLOR_FURNITURE, lw=1.5))
