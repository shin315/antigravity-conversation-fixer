"""Check and kill Antigravity processes."""

import subprocess
import platform
import time
import os


_SYSTEM = platform.system()


def is_antigravity_running():
    """Check if any Antigravity process is currently running."""
    if _SYSTEM == "Windows":
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq antigravity.exe'],
                capture_output=True, text=True, creationflags=0x08000000
            )
            return 'antigravity.exe' in result.stdout.lower()
        except Exception:
            return False
    else:
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'antigravity'],
                capture_output=True, text=True
            )
            return bool(result.stdout.strip())
        except Exception:
            return False


def kill_antigravity():
    """
    Kill all Antigravity processes.
    Returns True if all processes were terminated successfully.
    """
    try:
        if _SYSTEM == "Windows":
            subprocess.run(
                ['taskkill', '/F', '/IM', 'antigravity.exe'],
                capture_output=True, creationflags=0x08000000
            )
        else:
            subprocess.run(
                ['pkill', '-f', 'antigravity'],
                capture_output=True
            )
        time.sleep(1)
        return not is_antigravity_running()
    except Exception:
        return False


def launch_antigravity():
    """
    Attempt to launch Antigravity.
    Returns True if the process was started.
    """
    try:
        if _SYSTEM == "Windows":
            candidates = [
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Programs\antigravity\antigravity.exe"
                ),
                os.path.expandvars(
                    r"%LOCALAPPDATA%\antigravity\antigravity.exe"
                ),
            ]
            for path in candidates:
                if os.path.exists(path):
                    subprocess.Popen(
                        [path],
                        creationflags=0x00000008  # DETACHED_PROCESS
                    )
                    return True
        elif _SYSTEM == "Darwin":
            subprocess.Popen(['open', '-a', 'Antigravity'])
            return True
        else:
            subprocess.Popen(['antigravity'], start_new_session=True)
            return True
    except Exception:
        pass
    return False
