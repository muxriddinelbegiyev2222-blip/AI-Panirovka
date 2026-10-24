# main.py
# -*- coding: utf-8 -*-
"""
AI ARXITEKTOR PRO v4.0 — Asosiy kirish nuqtasi.

Ishlatish:
  python main.py                # GUI (Oyna) rejimida ishga tushish
  python main.py --cli --count 10 --out output_folder  # Terminal (Batch) rejimi
"""

import sys
import argparse
import logging
from config.settings import LOG_LEVEL, LOG_FORMAT

# Loggingni sozlash
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("main")

def main():
    parser = argparse.ArgumentParser(description="AI Arxitektor Pro v4.0")
    parser.add_argument("--cli", action="store_true", help="Terminal (CLI) rejimida ishga tushirish")
    parser.add_argument("--count", type=int, default=5, help="CLI rejimida nechta chizma yaratilsin")
    parser.add_argument("--out", type=str, default="batch_output", help="Chizmalar saqlanadigan papka")
    parser.add_argument("--floors", type=int, default=1, choices=[1, 2], help="Qavatlar soni (1 yoki 2)")
    
    args = parser.parse_args()

    if args.cli:
        # --- CLI REJIMI ---
        logger.info("CLI rejimi tanlandi.")
        from cli.batch_generator import run_batch_generation
        run_batch_generation(args.count, args.out, args.floors)
    else:
        # --- GUI REJIMI ---
        logger.info("GUI (Oyna) rejimi ishga tushirilmoqda...")
        try:
            import tkinter as tk
            from gui.app import AIArchitectApp
            
            root = tk.Tk()
            app = AIArchitectApp(root)
            root.mainloop()
        except ImportError as e:
            logger.error(f"GUI ishga tushmadi. Kutubxonalar yetishmayapti: {e}")
            print("Iltimos, 'pip install -r requirements.txt' buyrug'ini bajarib, Pillow o'rnatilganini tekshiring.")
        except tk.TclError:
            logger.error("Ekran (Display) topilmadi. Agar serverda ishlayotgan bo'lsangiz, faqat --cli rejimidan foydalaning.")

if __name__ == "__main__":
    main()
