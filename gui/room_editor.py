# gui/room_editor.py
# -*- coding: utf-8 -*-
"""
Xonalarni tahrirlash paneli.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable

from core.models import RoomRequest
from core.room_catalog import ROOM_CATALOG, get_all_room_codes


class RoomEditorPanel(tk.Frame):
    def __init__(self, master, on_generate: Callable[[List[RoomRequest], int], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_generate = on_generate
        self.room_requests: List[RoomRequest] = []
        
        # Standart namuna xonalarni yuklash
        self._load_demo_rooms()
        self._build_ui()

    def _load_demo_rooms(self):
        self.room_requests = [
            RoomRequest("mehmonxona", 4.6, 6.0),
            RoomRequest("oshxona", 4.6, 4.0),
            RoomRequest("kattalar_yotoqxonasi", 4.0, 3.6),
            RoomRequest("kattalar_yotoqxonasi", 4.6, 4.0),
            RoomRequest("bolalar_yotoqxonasi", 4.6, 3.0),
            RoomRequest("namozxona", 3.2, 3.6),
            RoomRequest("sanuzel", 2.0, 1.2),
            RoomRequest("sanuzel", 2.9, 2.0),
            RoomRequest("sanuzel", 1.5, 2.0),
        ]

    def _build_ui(self):
        # Sarlavha
        tk.Label(self, text="AI ARXITEKTOR KONSTRUKTORI", font=("Segoe UI", 12, "bold"), bg="#FFFFFF", fg="#102A43").pack(pady=(10, 2))
        tk.Label(self, text="Xonalarni kiriting. AI o'zi eng zo'r joylashuvni topadi.", font=("Segoe UI", 8), bg="#FFFFFF", fg="#486581").pack(pady=(0, 10))

        # Qavatlar soni
        floor_frame = tk.Frame(self, bg="#FFFFFF")
        floor_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(floor_frame, text="Qavatlar soni:", bg="#FFFFFF", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.combo_floors = ttk.Combobox(floor_frame, values=["1 qavat", "2 qavat"], state="readonly", width=10)
        self.combo_floors.current(0)
        self.combo_floors.pack(side="right")

        # Kiritish formasi
        form_frame = tk.Frame(self, bg="#FFFFFF")
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Xona turi:", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
        
        catalog_codes = get_all_room_codes()
        catalog_names = [f"{ROOM_CATALOG[c].name_uz.replace(chr(10), ' ')}" for c in catalog_codes]
        
        self.combo_room = ttk.Combobox(form_frame, values=catalog_names, state="readonly", width=25)
        self.combo_room.current(0)
        self.combo_room.grid(row=0, column=1, columnspan=3, pady=3, padx=5, sticky="we")

        tk.Label(form_frame, text="Eni (m):", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w")
        self.ent_w = ttk.Entry(form_frame, width=8)
        self.ent_w.insert(0, "4.0")
        self.ent_w.grid(row=1, column=1, pady=3, padx=5, sticky="w")

        tk.Label(form_frame, text="Bo'yi (m):", bg="#FFFFFF", font=("Segoe UI", 9)).grid(row=1, column=2, sticky="w")
        self.ent_h = ttk.Entry(form_frame, width=8)
        self.ent_h.insert(0, "4.0")
        self.ent_h.grid(row=1, column=3, pady=3, padx=5, sticky="w")

        # Tugmalar
        btn_frame = tk.Frame(self, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(btn_frame, text="+ Qo'shish", command=self._add_room, bg="#0E7C90", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=2)
        tk.Button(btn_frame, text="- O'chirish", command=self._remove_room, bg="#D64545", fg="white", font=("Segoe UI", 9)).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Tozalash", command=self._clear_rooms, bg="#627D98", fg="white", font=("Segoe UI", 9)).pack(side="right", padx=2)

        # Jadval (Treeview)
        self.tree = ttk.Treeview(self, columns=("tur", "olcham"), show="headings", height=12)
        self.tree.heading("tur", text="Xona Nomi")
        self.tree.heading("olcham", text="Eni × Bo'yi (m)")
        self.tree.column("tur", width=180)
        self.tree.column("olcham", width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_table()

        # Generatsiya tugmasi
        self.btn_generate = tk.Button(
            self, text="⚡ AI BILAN GENERATSIYA QILISH", command=self._trigger_generate,
            bg="#102A43", fg="white", font=("Segoe UI", 11, "bold"), pady=8
        )
        self.btn_generate.pack(fill="x", padx=10, pady=10)

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self.room_requests:
            name = ROOM_CATALOG[r.room_type].name_uz.replace("\n", " ")
            self.tree.insert("", "end", values=(name, f"{r.width:.1f} × {r.height:.1f}"))

    def _add_room(self):
        try:
            idx = self.combo_room.current()
            rcode = get_all_room_codes()[idx]
            w = float(self.ent_w.get())
            h = float(self.ent_h.get())
            if w < 1.0 or h < 1.0: raise ValueError
            self.room_requests.append(RoomRequest(rcode, w, h))
            self._refresh_table()
        except ValueError:
            messagebox.showerror("Xatolik", "Iltimos, xona eni va bo'yini to'g'ri raqamda kiriting (masalan: 4.0)")

    def _remove_room(self):
        sel = self.tree.selection()
        if sel:
            idx = self.tree.index(sel[0])
            self.room_requests.pop(idx)
            self._refresh_table()

    def _clear_rooms(self):
        self.room_requests.clear()
        self._refresh_table()

    def _trigger_generate(self):
        if not self.room_requests:
            messagebox.showwarning("Diqqat", "Kamida 2 ta xona kiriting!")
            return
        floor_count = 2 if self.combo_floors.current() == 1 else 1
        self.on_generate(self.room_requests, floor_count)

    def set_loading(self, is_loading: bool):
        """AI ishlayotganda tugmalarni bloklash."""
        state = "disabled" if is_loading else "normal"
        self.btn_generate.config(state=state, text="⏳ AI HISOBLAMOQDA..." if is_loading else "⚡ AI BILAN GENERATSIYA QILISH")
