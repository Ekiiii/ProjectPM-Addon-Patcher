"""
Application entrypoint for ProjectPM Addon Patcher & Randomizer.
"""
import ctypes
import os
import sys

if getattr(sys, "frozen", False):
    APP_ROOT = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))

if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)


def _close_native_splash():
    try:
        import pyi_splash
        if pyi_splash.is_alive():
            pyi_splash.close()
    except Exception:
        pass


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
    window.events.loaded += _close_native_splash
    webview.start(gui="edgechromium")


def main():
    try:
        from core.logger import init_logging
        init_logging()
    except Exception as e:
        print(f"[Logger Init Warning] {e}")

    try:
        launch_webview()
    except Exception as e:
        _close_native_splash()
        err_msg = f"Failed to initialize Edge WebView2 interface:\n{e}"
        print(f"[Launcher] {err_msg}")
        try:
            ctypes.windll.user32.MessageBoxW(0, err_msg, "ProjectPM Addon Patcher - Error", 0x10)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()


