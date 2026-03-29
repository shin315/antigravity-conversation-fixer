"""OS detection and Antigravity path constants."""

import os
import platform


_SYSTEM = platform.system()


def get_system() -> str:
    """Return the current OS name: 'Windows', 'Darwin', or 'Linux'."""
    return _SYSTEM


def get_db_path() -> str:
    """Return the path to Antigravity's state.vscdb database."""
    if _SYSTEM == "Windows":
        return os.path.expandvars(
            r"%APPDATA%\antigravity\User\globalStorage\state.vscdb"
        )
    elif _SYSTEM == "Darwin":
        return os.path.join(
            os.path.expanduser("~"), "Library", "Application Support",
            "antigravity", "User", "globalStorage", "state.vscdb"
        )
    else:
        return os.path.join(
            os.path.expanduser("~"), ".config", "Antigravity",
            "User", "globalStorage", "state.vscdb"
        )


def get_conversations_dir() -> str:
    """Return the path to the conversations directory (*.pb files)."""
    if _SYSTEM == "Windows":
        return os.path.expandvars(
            r"%USERPROFILE%\.gemini\antigravity\conversations"
        )
    else:
        return os.path.join(
            os.path.expanduser("~"), ".gemini", "antigravity", "conversations"
        )


def get_brain_dir() -> str:
    """Return the path to the brain artifacts directory."""
    if _SYSTEM == "Windows":
        return os.path.expandvars(
            r"%USERPROFILE%\.gemini\antigravity\brain"
        )
    else:
        return os.path.join(
            os.path.expanduser("~"), ".gemini", "antigravity", "brain"
        )


def validate_paths() -> list:
    """
    Validate that required paths exist.
    Returns list of error messages. Empty list = all OK.
    """
    errors = []
    if not os.path.exists(get_db_path()):
        errors.append(f"Database not found: {get_db_path()}")
    if not os.path.isdir(get_conversations_dir()):
        errors.append(f"Conversations directory not found: {get_conversations_dir()}")
    return errors
