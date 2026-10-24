from __future__ import annotations
import uuid
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
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8]) # <-- MANA SHU YANGI QATOR

    def area(self) -> float:
        return self.width * self.height

    def __repr__(self) -> str:
        label = self.custom_label or self.room_type
        fl = f", floor={self.preferred_floor}" if self.preferred_floor is not None else ""
        return f"RoomRequest({label}, {self.width:.2f}x{self.height:.2f}m{fl})"
