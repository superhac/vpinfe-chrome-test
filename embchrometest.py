import os
import sys
import subprocess
import platform
from screeninfo import get_monitors
import tempfile
import time
import signal

URL = "https://google.com"


def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller --onefile."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def get_chromium_path():
    system = platform.system()

    if system == "Windows":
        return resource_path("chromium/windows/chrome-win/chrome.exe")
    elif system == "Darwin":
        return resource_path("chromium/mac/Chromium.app/Contents/MacOS/Chromium")
    elif system == "Linux":
        return resource_path("chromium/linux/chrome")
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


def launch_for_monitor(chrome_path, monitor, index):
    """Launch one Chromium instance for a given monitor using a temporary profile."""
    user_data_dir = tempfile.mkdtemp(prefix=f"chromium_profile_{index}_")

    args = [
        chrome_path,
        f"--app={URL}",
        "--start-fullscreen",
        f"--window-position={monitor.x},{monitor.y}",
        f"--window-size={monitor.width},{monitor.height}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-restore-session-state",
    ]

    #if platform.system() == "Linux":
        #args.append("--no-sandbox")

    # Launch process
    return subprocess.Popen(args)


def main():
    chrome_path = get_chromium_path()

    if not os.path.exists(chrome_path):
        print("Chromium binary not found:", chrome_path)
        sys.exit(1)

    monitors = get_monitors()
    processes = []

    # Launch Chromium on each monitor
    for i, monitor in enumerate(monitors):
        proc = launch_for_monitor(chrome_path, monitor, i)
        processes.append(proc)

    print(f"Browsers launched on {len(monitors)} monitors. Waiting 10 seconds...")
    time.sleep(10)

    # Close all browser instances
    print("Closing browsers...")
    for proc in processes:
        if platform.system() == "Windows":
            proc.terminate()
        else:
            proc.send_signal(signal.SIGTERM)

    # Optional: wait for all processes to exit
    for proc in processes:
        proc.wait()

    print("All browsers closed.")


if __name__ == "__main__":
    main()
