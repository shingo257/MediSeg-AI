"""
Colab setup: install MediSeg.AI and create directories.
Run from repo root after cloning: python colab_setup.py

Usage on Colab:
  !git clone https://github.com/YOUR_USERNAME/MediSeg-AI.git /content/MediSeg-AI
  %cd /content/MediSeg-AI
  !python colab_setup.py
"""

import os
import subprocess
import sys

REPO_DIR = os.environ.get("MEDISEG_REPO_DIR", os.getcwd())
os.chdir(REPO_DIR)

def main():
    print("Installing MediSeg.AI (editable + gui-web)...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-e", ".[gui-web]", "-q",
    ], cwd=REPO_DIR)
    print("Installing Colab extras (pyngrok for public URL)...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "pyngrok", "-q",
    ], cwd=REPO_DIR)
    print("Creating data/results/configs dirs...")
    for d in ("data", "results", "configs"):
        path = os.path.join(REPO_DIR, d)
        os.makedirs(path, exist_ok=True)
    print("Done. In notebook: sys.path.insert(0, REPO_DIR) then use colab_launcher or main.py")
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
