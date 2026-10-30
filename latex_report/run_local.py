"""Launch Streamlit and automatically open the local app in a browser."""
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

URL = "http://localhost:8501"
cmd = [sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve().parent / "app.py"), "--server.headless=true", "--server.port=8501", "--browser.gatherUsageStats=false"]
process = subprocess.Popen(cmd)
try:
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError("Streamlit exited before starting. Check the terminal error above.")
        try:
            with urllib.request.urlopen(URL + "/_stcore/health", timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(URL)
                    print(f"Opened {URL} in your default browser.", flush=True)
                    break
        except Exception:
            time.sleep(0.5)
    else:
        print(f"Still waiting for Streamlit. Open {URL} manually if needed.", flush=True)
    process.wait()
except KeyboardInterrupt:
    process.terminate()
    process.wait()
