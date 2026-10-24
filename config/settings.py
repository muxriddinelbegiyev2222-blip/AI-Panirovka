# config/settings.py
# -*- coding: utf-8 -*-
"""
AI ARXITEKTOR PRO v4.0 — Global konfiguratsiya va konstantalar.

Barcha sehrli sonlar (magic numbers) shu faylda. Kodning boshqa joyida
hech qanday "o'sha yerda yozib qo'yilgan raqam" bo'lmasligi kerak.
"""

from __future__ import annotations
import os

# =============================================================================
# 1. DEVOR QALINLIKLARI (metr)
# =============================================================================
DEFAULT_EXT_WALL = 0.40         # Tashqi devor qalinligi
DEFAULT_INT_WALL = 0.16         # Ichki devor qalinligi
HALL_WALL_EXTRA = 0.10          # Xoll atrofidagi devor qo'shimchasi

# =============================================================================
# 2. XONA VA KORIDOR MINIMALLARI (SHNQ bo'yicha, metr)
# =============================================================================
MIN_ROOM_WIDTH = 1.50           # Hech qanday xona 1.5m dan tor bo'lmaydi
MIN_ROOM_HEIGHT = 1.20
MIN_CORRIDOR_WIDTH = 1.10       # O'tish yo'lagi minimum
MAX_CORRIDOR_WIDTH = 1.60
MIN_HALL_WIDTH = 3.00
MAX_HALL_WIDTH = 6.50
MIN_HALL_HEIGHT_RATIO = 0.30    # Xoll balandligi uy balandligining % da
MAX_HALL_HEIGHT_RATIO = 0.70

# =============================================================================
# 3. ZINAPOYA (2 qavatli uylar uchun)
# =============================================================================
STAIR_MIN_WIDTH = 1.10          # Bir marsh minimal eni
STAIR_MIN_DEPTH = 2.60          # To'liq marsh uzunligi
STAIR_TOTAL_WIDTH = 2.40        # Ikki marsh + bo'shliq
STAIR_TOTAL_DEPTH = 2.80
STAIR_RAIL_WIDTH = 0.06

# =============================================================================
# 4. ESHIK VA DERAZA
# =============================================================================
DOOR_MIN_WIDTH = 0.70
DOOR_DEFAULT_WIDTH = 0.90
DOOR_DOUBLE_WIDTH = 1.40
DOOR_HEIGHT = 2.10
WINDOW_MIN_WIDTH = 0.60
WINDOW_HEIGHT = 1.50
WINDOW_BOTTOM = 0.90            # Deraza pol sathidan balandligi

# =============================================================================
# 5. PLANIROVKA CHEGARALARI
# =============================================================================
MIN_TOTAL_WIDTH = 6.0           # Uyning minimal tashqi eni
MIN_TOTAL_HEIGHT = 6.0
MAX_TOTAL_WIDTH = 30.0          # Haddan ziyod katta uylarning oldini olish
MAX_TOTAL_HEIGHT = 30.0
PLAN_TOLERANCE = 0.05           # Geometrik taqqoslash uchun epsilon (5 sm)

# =============================================================================
# 6. GENETIK ALGORITM PARAMETRLARI
# =============================================================================
GA_POPULATION_SIZE = 80         # Populyatsiya hajmi
GA_GENERATIONS = 120            # Avlodlar soni
GA_ELITE_COUNT = 8              # Har avlodda saqlanadigan eng yaxshilar
GA_TOURNAMENT_SIZE = 3          # Tanlov turniri hajmi
GA_MUTATION_RATE = 0.28         # Mutatsiya ehtimoli
GA_CROSSOVER_RATE = 0.75        # Krossover ehtimoli
GA_RANDOM_IMMIGRANTS = 8        # Har avlodga qo'shiladigan tasodifiy yangi genomlar
GA_STAGNATION_LIMIT = 25        # Necha avloddan keyin to'xtatish (o'zgarmasa)
GA_DEFAULT_SEED = None          # None = har safar yangi natija

# Annealing (mahalliy qidiruv)
SA_INITIAL_TEMP = 1.0
SA_COOLING_RATE = 0.97
SA_ITERATIONS = 200

# =============================================================================
# 7. BAHOLASH VAZNLARI (jami 1.0 bo'lishi shart emas — normallashtiriladi)
# =============================================================================
SCORE_WEIGHTS = {
    "efficiency":     0.20,     # Foydali maydon ulushi
    "daylight":       0.20,     # Tabiiy yorug'lik (tashqi devorda xona)
    "dimension":      0.18,     # Foydalanuvchi o'lchamiga yaqinlik
    "ergonomics":     0.15,     # SHNQ minimallariga rioya
    "circulation":    0.15,     # Koridor/xoll ulushi maqbulligi
    "symmetry":       0.07,     # Konstruktiv simmetriya
    "staircase":      0.05,     # Zinapoya joylashuvi (2-qavat uchun)
}
SCORE_MIN = 0.0
SCORE_MAX = 100.0

# =============================================================================
# 8. RENDER RANGLARI (oldingi koddan meros)
# =============================================================================
COLOR_BG = "#FFFFFF"
COLOR_WALL = "#0D0D0D"
COLOR_FURNITURE = "#0E7C90"
COLOR_FURNITURE_FILL = "#F2FAFC"
COLOR_DOOR = "#B56B27"
COLOR_DOOR_EXTERIOR = "#4A89B8"
COLOR_WINDOW_GLASS = "#4A89B8"
COLOR_DIM = "#222222"
COLOR_TEXT = "#181818"
COLOR_STAIR = "#8B5A2B"
COLOR_CORRIDOR_FILL = "#FAFCFE"
COLOR_GARDEN = "#2EAE34"

# =============================================================================
# 9. CHIZMA VA EKSPORT
# =============================================================================
DEFAULT_DPI = 200
PREVIEW_DPI = 120
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "ai_arxitektor_output")
EXPORT_FORMATS = ("png", "pdf", "dxf", "json")

# =============================================================================
# 10. 2 QAVATLI UYLAR UCHUN XONA TAVSIYALARI
# =============================================================================
# Qaysi xona turi qaysi qavatga mos keladi (genom boshlang'ich qiymati uchun)
GROUND_FLOOR_PREFERRED = {
    "mehmonxona", "oshxona", "tambur", "xoll", "ota_ona_yotoqxonasi",
    "kabinet", "sanuzel", "kotelnaya", "omborxona", "garaj", "terrasa",
}
UPPER_FLOOR_PREFERRED = {
    "kattalar_yotoqxonasi", "bolalar_yotoqxonasi", "namozxona",
    "xammom", "dush", "garderob", "kir_yuvish", "sport_zali", "kutubxona",
}

# =============================================================================
# 11. VALIDATSIYA
# =============================================================================
VALIDATE_STRICT = True          # False qilinsa, xatolar warning bo'ladi
MAX_ROOM_COUNT = 30             # Bitta qavatda maksimal xona
MAX_STORY_COUNT = 3             # Maksimal qavat soni

# =============================================================================
# 12. LOGING
# =============================================================================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
