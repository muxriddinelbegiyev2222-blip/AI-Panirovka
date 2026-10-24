# core/models.py
# -*- coding: utf-8 -*-
"""
Barcha asosiy ma'lumot modellari (dataclass'lar).

Bu fayl HECH KIMGA bog'liq emas — faqat stdlib.
Boshqa barcha core/* modullari shu fayldan import qiladi.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any


# =============================================================================
# 1. XONA TURI SPETSIFIKATSIYASI (katalog elementi)
# =============================================================================
@dataclass(frozen=True)
class RoomTypeSpec:
    """Xona turining to'liq tavsifi (katalogdan)."""
    code: str
    name_uz: str
    category: str               # 'public', 'private', 'wet', 'service', 'transit', 'special', 'outdoor'
    default_w: float            # Standart eni (m)
    default_h: float            # Standart bo'yi (m)
    min_w: float                # SHNQ minimal eni
    min_h: float                # SHNQ minimal bo'yi
    needs_window: bool          # Tashqi devor/deraza shartmi
    priority_zone: str          # 'front', 'back', 'side', 'center', 'corner'
    door_width: float           # Standart eshik eni
    double_door: bool           # Ikki tabaqali eshikmi
    furniture_style: str        # Mebel chizish shabloni
    preferred_floor: str        # 'ground', 'upper', 'any'


# =============================================================================
# 2. FOYDALANUVCHI TALABI
# =============================================================================
@dataclass
class RoomRequest:
    """Foydalanuvchi kiritgan bitta xona talabi."""
    room_type: str
    width: float
    height: float
    custom_label: Optional[str] = None
    preferred_floor: Optional[int] = None    # 0=ground, 1=upper, None=AI tanlaydi

    def area(self) -> float:
        return self.width * self.height

    def __repr__(self) -> str:
        label = self.custom_label or self.room_type
        fl = f", floor={self.preferred_floor}" if self.preferred_floor is not None else ""
        return f"RoomRequest({label}, {self.width:.2f}x{self.height:.2f}m{fl})"


# =============================================================================
# 3. JOYLASHTIRILGAN XONA
# =============================================================================
@dataclass
class PlacedRoom:
    """Chizmada aniq koordinatali xona."""
    id: str                     # Unikal ID (room_1_oshxona)
    room_type: str
    label: str
    category: str
    x: float                    # Chap-pastki X (m)
    y: float                    # Chap-pastki Y (m)
    w: float                    # Haqiqiy eni (m)
    h: float                    # Haqiqiy bo'yi (m)
    orig_w: float               # Foydalanuvchi so'ragan eni (m)
    orig_h: float               # Foydalanuvchi so'ragan bo'yi (m)
    furniture_style: str
    needs_window: bool
    wing: str                   # 'left', 'right', 'top', 'center', 'corridor'
    floor_index: int = 0
    rotated: bool = False

    def area(self) -> float:
        return self.w * self.h

    def bbox(self) -> Tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def overlaps_with(self, other: "PlacedRoom", tol: float = 0.01) -> bool:
        ax1, ay1, ax2, ay2 = self.bbox()
        bx1, by1, bx2, by2 = other.bbox()
        return not (ax2 <= bx1 + tol or bx2 <= ax1 + tol or
                    ay2 <= by1 + tol or by2 <= ay1 + tol)


# =============================================================================
# 4. ESHIK
# =============================================================================
@dataclass
class DoorSpec:
    """Bitta eshik."""
    x: float
    y: float
    width: float
    orientation: str        # 'H' (gorizontal devorda) yoki 'V' (vertikal devorda)
    swing_dir: str          # '+y', '-y', '+x', '-x'
    hinge_side: str         # 'left' yoki 'right'
    is_double: bool = False
    is_exterior: bool = False
    connects_rooms: Tuple[str, str] = ("", "")   # (room_id_1, room_id_2)
    floor_index: int = 0


# =============================================================================
# 5. DERAZA
# =============================================================================
@dataclass
class WindowSpec:
    """Bitta deraza."""
    x: float
    y: float
    length: float
    orientation: str        # 'H' yoki 'V'
    wall_side: str          # 'bottom', 'top', 'left', 'right'
    room_id: str = ""
    floor_index: int = 0


# =============================================================================
# 6. ZINAPOYA (2 qavatli uylar uchun)
# =============================================================================
@dataclass
class StaircaseSpec:
    """Zinapoya — qavatlarni bog'laydi."""
    x: float
    y: float
    w: float
    h: float
    shape: str = "L"        # 'L', 'U', 'straight'
    direction: str = "up"   # 'up', 'down', 'up-down'
    flight_count: int = 2
    connects_floors: Tuple[int, int] = (0, 1)


# =============================================================================
# 7. BITTA QAVATNING REJASI
# =============================================================================
@dataclass
class FloorPlan:
    """Bitta qavatning to'liq planirovkasi."""
    variant_index: int
    strategy_name: str
    strategy_desc: str
    floor_index: int
    total_width: float
    total_height: float
    ext_wall_thick: float
    int_wall_thick: float
    rooms: List[PlacedRoom] = field(default_factory=list)
    doors: List[DoorSpec] = field(default_factory=list)
    windows: List[WindowSpec] = field(default_factory=list)
    staircases: List[StaircaseSpec] = field(default_factory=list)
    ai_score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def total_area(self) -> float:
        return self.total_width * self.total_height

    def usable_area(self) -> float:
        return sum(r.area() for r in self.rooms if r.category != "transit")

    def transit_area(self) -> float:
        return sum(r.area() for r in self.rooms if r.category == "transit")

    def get_room(self, room_id: str) -> Optional[PlacedRoom]:
        for r in self.rooms:
            if r.id == room_id:
                return r
        return None


# =============================================================================
# 8. QAVAT (FloorPlan uchun o'rovchi)
# =============================================================================
@dataclass
class StoryPlan:
    """Bitta qavat + unga tegishli metama'lumot."""
    story_index: int
    floorplan: FloorPlan
    staircase: Optional[StaircaseSpec] = None


# =============================================================================
# 9. BUTUN UY (1 yoki 2+ qavat)
# =============================================================================
@dataclass
class HousePlan:
    """Butun uyning to'liq planirovkasi (barcha qavatlar)."""
    house_id: str
    stories: List[StoryPlan] = field(default_factory=list)
    footprint_w: float = 0.0        # Eng katta qavat eni
    footprint_h: float = 0.0        # Eng katta qavat bo'yi
    total_area: float = 0.0         # Barcha qavatlar yig'indisi
    usable_area: float = 0.0        # Foydali maydon yig'indisi
    ai_score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)

    def story_count(self) -> int:
        return len(self.stories)


# =============================================================================
# 10. GENOM — GENETIK ALGORITM "XROMOSOMASI" (1 qavat)
# =============================================================================
@dataclass
class FloorGenome:
    """
    Bitta qavat uchun genetik kod.

    Bu genom mutatsiya/krossover orqali o'zgaradi va floor_planner tomonidan
    haqiqiy FloorPlan ga "dekodlanadi". Cheksiz kombinatsiyalar shu yerdan keladi.
    """
    floor_index: int
    wing_assignment: Dict[str, str] = field(default_factory=dict)
    # ^ room_id -> 'left' | 'right' | 'top' | 'unassigned'

    left_order: List[str] = field(default_factory=list)
    right_order: List[str] = field(default_factory=list)
    top_order: List[str] = field(default_factory=list)

    hall_w: float = 4.0             # Xoll eni (3.0 - 6.5)
    hall_h_ratio: float = 0.55      # Xoll balandligi nisbati (0.30 - 0.70)
    rotations: Dict[str, bool] = field(default_factory=dict)  # room_id -> rotated?

    def all_room_ids(self) -> List[str]:
        return list(self.wing_assignment.keys())

    def copy(self) -> "FloorGenome":
        return FloorGenome(
            floor_index=self.floor_index,
            wing_assignment=dict(self.wing_assignment),
            left_order=list(self.left_order),
            right_order=list(self.right_order),
            top_order=list(self.top_order),
            hall_w=self.hall_w,
            hall_h_ratio=self.hall_h_ratio,
            rotations=dict(self.rotations),
        )


# =============================================================================
# 11. BUTUN UY GENOMI
# =============================================================================
@dataclass
class HouseGenome:
    """Butun uy uchun genetik kod (barcha qavatlar)."""
    floor_genomes: List[FloorGenome] = field(default_factory=list)
    staircase_slot: str = "center"      # 'left' | 'center' | 'right'
    shared_footprint: bool = True       # Qavatlar bir xil tashqi o'lchamdami

    def copy(self) -> "HouseGenome":
        return HouseGenome(
            floor_genomes=[fg.copy() for fg in self.floor_genomes],
            staircase_slot=self.staircase_slot,
            shared_footprint=self.shared_footprint,
        )

    def story_count(self) -> int:
        return len(self.floor_genomes)


# =============================================================================
# 12. OPTIMALLASHTIRISH NATIJASI
# =============================================================================
@dataclass
class OptimizationResult:
    """Genetik algoritm natijasi."""
    best_genome: HouseGenome
    best_house: HousePlan
    best_score: float
    all_time_best_score: float
    history: List[float] = field(default_factory=list)   # Har avlod eng yaxshi ball
    mean_history: List[float] = field(default_factory=list)
    generations_run: int = 0
    stagnation_reached: bool = False
    elapsed_seconds: float = 0.0
    population_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# 13. VALIDATSIYA NATIJASI
# =============================================================================
@dataclass
class ValidationIssue:
    """Bitta validatsiya xatosi/ogohlantirishi."""
    severity: str       # 'error' | 'warning' | 'info'
    code: str           # 'OVERLAP', 'OUT_OF_BOUNDS', 'TOO_SMALL', ...
    message: str
    room_ids: Tuple[str, ...] = ()
    floor_index: int = 0


@dataclass
class ValidationReport:
    """To'liq validatsiya hisoboti."""
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)

    def add(self, issue: ValidationIssue) -> None:
        self.issues.append(issue)
        if issue.severity == "error":
            self.is_valid = False

    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
