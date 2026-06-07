"""
launcher.py — Windows system tray app for LeadBot
Right-click the system tray icon to:
  - Open Dashboard (browser)
  - Run Pipeline Now
  - Send Test Notification
  - View data folder
  - Quit

Double-click the icon = open dashboard.
This makes LeadBot feel like a real Windows app.
"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

# Ensure we're in the right directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def make_icon_image():
    """Create a simple spider icon programmatically (no external file needed)."""
    try:
        from PIL import Image, ImageDraw
        # 64x64 RGBA image
        img = Image.new("RGBA", (64, 64), (15, 17, 21, 255))
        d = ImageDraw.Draw(img)
        # Spider body (purple)
        d.ellipse([24, 20, 40, 36], fill=(155, 89, 182, 255))
        # Spider head
        d.ellipse([20, 14, 30, 24], fill=(155, 89, 182, 255))
        # 8 legs (lines radiating from body)
        for angle_offset in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            d.line([(32, 28), (32 + angle_offset[0] * 20, 28 + angle_offset[1] * 20)], fill=(155, 89, 182, 255), width=2)
        # Eyes (white)
        d.ellipse([22, 16, 25, 19], fill=(255, 255, 255, 255))
        d.ellipse([27, 16, 30, 19], fill=(255, 255, 255, 255))
        return img
    except ImportError:
        return None


def start_dashboard_server(port: int = 7860):
    """Start the FastAPI dashboard server in background."""
    import uvicorn
    from dashboard import app
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    # Wait for server to be ready
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def open_dashboard(port: int = 7860):
    """Open the dashboard in default browser."""
    webbrowser.open(f"http://127.0.0.1:{port}")


def run_pipeline_now():
    """Run the main.py pipeline in background."""
    subprocess.Popen(
        [sys.executable, "-B", "main.py"],
        cwd=PROJECT_ROOT,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )


def open_data_folder():
    """Open the data folder in file explorer."""
    from config import DATA_DIR
    if sys.platform == "win32":
        os.startfile(DATA_DIR)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", DATA_DIR])
    else:
        subprocess.Popen(["xdg-open", DATA_DIR])


def send_test_notification():
    """Send a test notification via the dashboard API."""
    import urllib.request
    import json
    try:
        req = urllib.request.Request("http://127.0.0.1:7860/api/notify?min_score=0", method="POST")
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Test notification failed: {e}")


def main():
    """Start the system tray app."""
    try:
        import pystray
    except ImportError:
        print("pystray not installed. Run: pip install pystray")
        print("Or use the web dashboard: python dashboard.py")
        return

    icon_image = make_icon_image()
    if icon_image is None:
        # Use default icon
        icon_image = pystray.Icon.DEFAULT_ICON if hasattr(pystray, "Icon") else None

    def on_open_dashboard(icon, item):
        open_dashboard()

    def on_run_pipeline(icon, item):
        run_pipeline_now()
        icon.notify("LeadBot: Pipeline started!", title="LeadBot")

    def on_open_data(icon, item):
        open_data_folder()

    def on_test_notify(icon, item):
        send_test_notification()
        icon.notify("Test notification sent!", title="LeadBot")

    def on_quit(icon, item):
        icon.stop()

    def on_double_click(icon, item):
        open_dashboard()

    menu = pystray.Menu(
        pystray.MenuItem("🌐 Open Dashboard", on_open_dashboard, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("▶ Run Pipeline Now", on_run_pipeline),
        pystray.MenuItem("🔔 Test Notification", on_test_notify),
        pystray.MenuItem("📂 Open Data Folder", on_open_data),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Quit", on_quit),
    )

    icon = pystray.Icon("LeadBot", icon_image, "LeadBot - AI Lead Generator", menu)
    icon.on_double_click = on_double_click if hasattr(icon, "on_double_click") else None

    # Start the dashboard server in background
    print("Starting dashboard server...")
    if not start_dashboard_server():
        print("Warning: Dashboard server failed to start. Open browser manually at http://127.0.0.1:7860")

    # Show notification
    def notify_and_open():
        time.sleep(2)
        try:
            icon.notify("🕷️ LeadBot is running! Right-click for menu.", title="LeadBot")
        except Exception:
            pass

    threading.Thread(target=notify_and_open, daemon=True).start()

    # Run the icon (blocks)
    icon.run()


if __name__ == "__main__":
    main()
