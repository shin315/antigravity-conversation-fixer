"""SQLite operations for Antigravity state.vscdb."""

import sqlite3
import os


_KEY = "antigravityUnifiedStateSync.trajectorySummaries"


def read_trajectory_data(db_path):
    """
    Read raw base64 trajectory data from state.vscdb.
    Returns the base64 string or None if key not found.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT value FROM ItemTable WHERE key=?", (_KEY,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else None


def write_trajectory_data(db_path, encoded_b64):
    """
    Write rebuilt trajectory data to state.vscdb.
    Creates the key if it doesn't exist, updates if it does.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM ItemTable WHERE key=?", (_KEY,))
    if cur.fetchone():
        cur.execute(
            "UPDATE ItemTable SET value=? WHERE key=?",
            (encoded_b64, _KEY)
        )
    else:
        cur.execute(
            "INSERT INTO ItemTable (key, value) VALUES (?, ?)",
            (_KEY, encoded_b64)
        )
    conn.commit()
    conn.close()


def backup_current_data(db_path, backup_path):
    """
    Backup current trajectory data to a text file.
    Returns True if backup was created, False if no data to backup.
    """
    data = read_trajectory_data(db_path)
    if data:
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(data)
        return True
    return False
