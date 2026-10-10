# -*- coding: utf-8 -*-
"""
main.py
Application Entrypoint for ProjectPM Addon Patcher & Randomizer.
Supports modern PyWebView (Edge WebView2) Pixel Art interface with automatic fallback to Tkinter.
Supports running directly via Python or bundled as a standalone PyInstaller .exe.
"""
import os
import sys

# Ensure root directory is in sys.path
if getattr(sys, "frozen", False):
    APP_ROOT = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

def launch_legacy():
    from ui.main_window import MainWindow
    app = MainWindow(root_dir=APP_ROOT)
    app.mainloop()

def launch_webview():
    import webview
    from ui.bridge import PatcherBridge

    bridge = PatcherBridge(root_dir=APP_ROOT)
    web_dir = os.path.join(APP_ROOT, "ui", "web")
    index_html = os.path.join(web_dir, "index.html")

    window = webview.create_window(
        title="ProjectPM - Mod Patcher & Randomizer",
        url=index_html,
        js_api=bridge,
        width=1180,
        height=840,
        min_size=(1040, 740),
        frameless=True,
        easy_drag=False,
        background_color="#0b101b"
    )
    bridge.set_window(window)
    webview.start(gui="edgechromium")

def main():
    try:
        from core.logger import init_logging
        init_logging()
    except Exception as e:
        print(f"[Logger Init Warning] {e}")

    if "--legacy" in sys.argv:
        launch_legacy()
        return

    try:
        launch_webview()
    except Exception as e:
        print(f"[Launcher] PyWebView initialization failed ({e}), falling back to Tkinter GUI...")
        launch_legacy()

if __name__ == "__main__":
    main()
