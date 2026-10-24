# core/room_catalog.py
# -*- coding: utf-8 -*-
"""
Xonalar katalogi.

Bu faylda barcha mumkin bo'lgan xona turlari, ularning standart o'lchamlari,
SHNQ bo'yicha minimal o'lchamlari va boshqa xususiyatlari saqlanadi.
"""

from typing import Dict, List
from core.models import RoomTypeSpec

# =============================================================================
# XONALAR KATALOGI (20+ xona turi)
# =============================================================================

ROOM_CATALOG: Dict[str, RoomTypeSpec] = {
    "mehmonxona": RoomTypeSpec(
        code="mehmonxona", name_uz="Mehmonxona", category="public",
        default_w=4.6, default_h=6.0, min_w=3.2, min_h=4.0,
        needs_window=True, priority_zone="front",
        door_width=1.2, double_door=True, furniture_style="banquet_hall",
        preferred_floor="ground"
    ),
    "oshxona": RoomTypeSpec(
        code="oshxona", name_uz="Oshxona", category="public",
        default_w=4.6, default_h=4.0, min_w=2.4, min_h=2.8,
        needs_window=True, priority_zone="front",
        door_width=0.9, double_door=False, furniture_style="kitchen_dining",
        preferred_floor="ground"
    ),
    "kattalar_yotoqxonasi": RoomTypeSpec(
        code="kattalar_yotoqxonasi", name_uz="Kattalar\nyotoqxonasi", category="private",
        default_w=4.0, default_h=3.8, min_w=2.8, min_h=3.0,
        needs_window=True, priority_zone="back",
        door_width=0.9, double_door=False, furniture_style="master_bedroom",
        preferred_floor="any"
    ),
    "ota_ona_yotoqxonasi": RoomTypeSpec(
        code="ota_ona_yotoqxonasi", name_uz="Ota-ona\nyotoqxonasi", category="private",
        default_w=4.6, default_h=4.0, min_w=3.0, min_h=3.2,
        needs_window=True, priority_zone="back",
        door_width=0.9, double_door=False, furniture_style="master_bedroom",
        preferred_floor="ground"
    ),
    "bolalar_yotoqxonasi": RoomTypeSpec(
        code="bolalar_yotoqxonasi", name_uz="Bolalar\nyotoqxonasi", category="private",
        default_w=4.6, default_h=3.0, min_w=2.4, min_h=2.8,
        needs_window=True, priority_zone="side",
        door_width=0.9, double_door=False, furniture_style="kids_bedroom",
        preferred_floor="upper"
    ),
    "namozxona": RoomTypeSpec(
        code="namozxona", name_uz="Namoz xona", category="special",
        default_w=3.2, default_h=3.6, min_w=2.0, min_h=2.5,
        needs_window=True, priority_zone="back",
        door_width=0.9, double_door=False, furniture_style="prayer_room",
        preferred_floor="any"
    ),
    "sanuzel": RoomTypeSpec(
        code="sanuzel", name_uz="S/U", category="wet",
        default_w=2.0, default_h=1.8, min_w=1.2, min_h=1.5,
        needs_window=True, priority_zone="side",
        door_width=0.75, double_door=False, furniture_style="bathroom_compact",
        preferred_floor="any"
    ),
    "xammom": RoomTypeSpec(
        code="xammom", name_uz="Xammom", category="wet",
        default_w=2.9, default_h=2.0, min_w=1.8, min_h=1.8,
        needs_window=True, priority_zone="back",
        door_width=0.75, double_door=False, furniture_style="bathroom_full",
        preferred_floor="ground"
    ),
    "dush": RoomTypeSpec(
        code="dush", name_uz="Dush", category="wet",
        default_w=1.8, default_h=2.0, min_w=1.2, min_h=1.4,
        needs_window=True, priority_zone="side",
        door_width=0.75, double_door=False, furniture_style="shower_room",
        preferred_floor="upper"
    ),
    "kabinet": RoomTypeSpec(
        code="kabinet", name_uz="Ish kabineti", category="special",
        default_w=3.6, default_h=3.4, min_w=2.4, min_h=2.6,
        needs_window=True, priority_zone="front",
        door_width=0.9, double_door=False, furniture_style="office_study",
        preferred_floor="ground"
    ),
    "garderob": RoomTypeSpec(
        code="garderob", name_uz="Garderob", category="service",
        default_w=2.4, default_h=2.0, min_w=1.5, min_h=1.5,
        needs_window=False, priority_zone="side",
        door_width=0.8, double_door=False, furniture_style="wardrobe_room",
        preferred_floor="any"
    ),
    "kotelnaya": RoomTypeSpec(
        code="kotelnaya", name_uz="Qozonxona\n(Kotel)", category="service",
        default_w=2.8, default_h=2.2, min_w=1.8, min_h=1.8,
        needs_window=True, priority_zone="back",
        door_width=0.8, double_door=False, furniture_style="boiler_room",
        preferred_floor="ground"
    ),
    "omborxona": RoomTypeSpec(
        code="omborxona", name_uz="Omborxona", category="service",
        default_w=2.2, default_h=2.0, min_w=1.5, min_h=1.5,
        needs_window=False, priority_zone="side",
        door_width=0.8, double_door=False, furniture_style="storage_room",
        preferred_floor="any"
    ),
    "kir_yuvish": RoomTypeSpec(
        code="kir_yuvish", name_uz="Kir yuvish\nxonasi", category="wet",
        default_w=2.2, default_h=2.0, min_w=1.6, min_h=1.6,
        needs_window=False, priority_zone="side",
        door_width=0.75, double_door=False, furniture_style="laundry_room",
        preferred_floor="any"
    ),
    "tambur": RoomTypeSpec(
        code="tambur", name_uz="Prixojaya", category="transit",
        default_w=3.0, default_h=2.2, min_w=2.0, min_h=1.8,
        needs_window=False, priority_zone="front",
        door_width=1.2, double_door=True, furniture_style="foyer",
        preferred_floor="ground"
    ),
    "xoll": RoomTypeSpec(
        code="xoll", name_uz="XOLL", category="transit",
        default_w=4.0, default_h=7.0, min_w=3.0, min_h=3.0,
        needs_window=False, priority_zone="center",
        door_width=1.4, double_door=True, furniture_style="central_hall",
        preferred_floor="ground"
    ),
    "garaj": RoomTypeSpec(
        code="garaj", name_uz="Garaj", category="special",
        default_w=4.0, default_h=6.0, min_w=3.0, min_h=5.0,
        needs_window=False, priority_zone="front",
        door_width=2.5, double_door=True, furniture_style="garage",
        preferred_floor="ground"
    ),
    "terrasa": RoomTypeSpec(
        code="terrasa", name_uz="Terrasa", category="outdoor",
        default_w=3.5, default_h=4.0, min_w=2.5, min_h=2.5,
        needs_window=False, priority_zone="front",
        door_width=1.2, double_door=True, furniture_style="terrace",
        preferred_floor="ground"
    ),
    "sport_zali": RoomTypeSpec(
        code="sport_zali", name_uz="Sport zali", category="special",
        default_w=4.0, default_h=5.0, min_w=3.0, min_h=3.5,
        needs_window=True, priority_zone="side",
        door_width=0.9, double_door=False, furniture_style="gym",
        preferred_floor="upper"
    ),
    "kutubxona": RoomTypeSpec(
        code="kutubxona", name_uz="Kutubxona", category="special",
        default_w=3.5, default_h=4.0, min_w=2.5, min_h=2.5,
        needs_window=True, priority_zone="back",
        door_width=0.9, double_door=False, furniture_style="library",
        preferred_floor="upper"
    )
}


# =============================================================================
# YORDAMCHI FUNKSIYALAR
# =============================================================================

def get_room_spec(room_type: str) -> RoomTypeSpec:
    """Xona turi bo'yicha spetsifikatsiyani qaytaradi. Topilmasa xato beradi."""
    if room_type not in ROOM_CATALOG:
        raise KeyError(f"Xona turi katalogda topilmadi: '{room_type}'. "
                       f"Mavjud turlar: {list(ROOM_CATALOG.keys())}")
    return ROOM_CATALOG[room_type]


def get_all_room_codes() -> List[str]:
    """Barcha mavjud xona turlari kodlarini ro'yxat shaklida qaytaradi."""
    return list(ROOM_CATALOG.keys())


def get_room_label(room_type: str) -> str:
    """Xonaning o'zbekcha nomini qaytaradi (yangi qatorsiz)."""
    spec = get_room_spec(room_type)
    return spec.name_uz.replace("\n", " ")
