# -*- coding: utf-8 -*-
"""
main.py
Application Entrypoint for ProjectPM Addon Patcher.
Supports running directly via Python or bundled as a standalone PyInstaller .exe.
"""
import os
import sys

# Ensure root directory is in sys.path
if getattr(sys, "frozen", False):
    # PyInstaller bundle directory
    APP_ROOT = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from ui.main_window import MainWindow

def main():
    app = MainWindow(root_dir=APP_ROOT)
    app.mainloop()

if __name__ == "__main__":
    main()
