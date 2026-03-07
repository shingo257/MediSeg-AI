"""
Colab entrypoint for MediSeg.AI Web GUI.
Use after cloning the repo and running: python colab_setup.py
"""

import os
import sys
import threading
import time
from typing import Optional

# Ensure repo root is on path (Colab clones to /content/MediSeg-AI)
REPO_DIR = os.environ.get("MEDISEG_REPO_DIR", "/content/MediSeg-AI")
if REPO_DIR not in sys.path:
    sys.path.insert(0, REPO_DIR)
os.chdir(REPO_DIR)


def launch_web_gui(
    ngrok_token: Optional[str] = None,
    port: int = 8080,
    host: str = "0.0.0.0",
) -> None:
    """
    Start the Web GUI for Colab. Optionally expose with ngrok.

    Args:
        ngrok_token: If set, install/start ngrok and print the public URL.
        port: Port for the Flask app (default 8080).
        host: Bind address (default 0.0.0.0 for Colab).
    """
    from backend.gui.web.config import WebGUIConfig
    from backend.gui.web.launcher import WebGUILauncher

    config = WebGUIConfig.from_env()
    config.host = host
    config.port = port
    config.auto_open_browser = False  # Colab: no local browser

    def start_ngrok_after_delay():
        time.sleep(4)
        try:
            from pyngrok import ngrok
            public_url = ngrok.connect(port, bind_tls=True)
            print("=" * 60)
            print("Web GUI (public):", public_url.public_url)
            print("=" * 60)
        except Exception as e:
            print("ngrok failed:", e)

    if ngrok_token:
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyngrok"])
        except Exception:
            pass
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(ngrok_token)
            t = threading.Thread(target=start_ngrok_after_delay, daemon=True)
            t.start()
        except Exception as e:
            print("ngrok setup failed:", e)

    launcher = WebGUILauncher(config=config)
    launcher.launch()
