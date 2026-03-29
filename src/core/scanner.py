"""
Conversation scanning, title resolution, workspace inference,
and trajectory entry building.
"""

import base64
import os
import re
import time
from urllib.parse import quote

from src.core.paths import get_system, get_brain_dir, get_conversations_dir
from src.core.protobuf import (
    encode_varint, decode_varint, skip_protobuf_field,
    strip_field_from_protobuf, encode_length_delimited, encode_string_field,
)


_SYSTEM = get_system()


# ─── Discovery ───────────────────────────────────────────────────────────────

def discover_conversations(conversations_dir):
    """
    Return conversation IDs sorted by file modification time (newest first).
    """
    conv_files = [f for f in os.listdir(conversations_dir) if f.endswith('.pb')]
    conv_files.sort(
        key=lambda f: os.path.getmtime(os.path.join(conversations_dir, f)),
        reverse=True
    )
    return [f[:-3] for f in conv_files]


# ─── Workspace Helpers ───────────────────────────────────────────────────────

def path_to_workspace_uri(folder_path):
    """
    Convert a local folder path to a file:/// URI matching Antigravity's format.
    Example: D:\\Repos\\My Project  →  file:///d%3A/Repos/My%20Project
    """
    p = folder_path.replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        drive = p[0].lower()
        rest = p[2:]
    else:
        drive = None
        rest = p

    segments = rest.split("/")
    encoded_segments = [quote(seg, safe="") for seg in segments]
    encoded_path = "/".join(encoded_segments)

    if drive:
        return f"file:///{drive}%3A{encoded_path}"
    else:
        return f"file:///{encoded_path.lstrip('/')}"


def build_workspace_field(folder_path):
    """
    Build protobuf field 9 (workspace sub-message) from a filesystem path.
    Sub-message: sub-field 1 = workspace URI, sub-field 2 = workspace URI.
    """
    uri = path_to_workspace_uri(folder_path)
    sub_msg = encode_string_field(1, uri) + encode_string_field(2, uri)
    return encode_length_delimited(9, sub_msg)


def extract_workspace_hint(inner_blob):
    """
    Try to extract a workspace URI from the protobuf inner blob.
    Returns the URI string if found, or None.
    """
    if not inner_blob:
        return None
    try:
        pos = 0
        while pos < len(inner_blob):
            tag, pos = decode_varint(inner_blob, pos)
            wire_type = tag & 7
            field_num = tag >> 3
            if wire_type == 2:
                l, pos = decode_varint(inner_blob, pos)
                content = inner_blob[pos:pos + l]
                pos += l
                if field_num > 1:
                    try:
                        text = content.decode("utf-8", errors="strict")
                        if "file:///" in text:
                            return text
                    except Exception:
                        pass
            elif wire_type == 0:
                _, pos = decode_varint(inner_blob, pos)
            elif wire_type == 1:
                pos += 8
            elif wire_type == 5:
                pos += 4
            else:
                break
    except Exception:
        pass
    return None


def infer_workspace_from_brain(conversation_id, brain_dir=None):
    """
    Scan brain .md files for file:/// paths and infer the workspace
    from the most common project folder prefix.
    Returns a filesystem path string or None.
    """
    if brain_dir is None:
        brain_dir = get_brain_dir()

    brain_path = os.path.join(brain_dir, conversation_id)
    if not os.path.isdir(brain_path):
        return None

    if _SYSTEM == "Windows":
        path_pattern = re.compile(r"file:///([A-Za-z](?:%3A|:)/[^\s\"'\]>]+)")
    else:
        path_pattern = re.compile(r"file:///([^\s\"'\]>]+)")

    path_counts = {}

    try:
        for name in os.listdir(brain_path):
            if not name.endswith(".md") or name.startswith("."):
                continue
            filepath = os.path.join(brain_path, name)
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(16384)
                for match in path_pattern.finditer(content):
                    raw = match.group(1)
                    raw = raw.replace("%3A", ":").replace("%3a", ":")
                    raw = raw.replace("%20", " ")
                    parts = raw.replace("\\", "/").split("/")
                    depth = 5 if _SYSTEM == "Windows" else 4
                    if len(parts) >= depth:
                        ws = "/".join(parts[:depth])
                        path_counts[ws] = path_counts.get(ws, 0) + 1
            except Exception:
                pass
    except Exception:
        return None

    if not path_counts:
        return None

    best = max(path_counts, key=path_counts.get)
    return best.replace("/", os.sep)


# ─── Timestamp Helpers ───────────────────────────────────────────────────────

def build_timestamp_fields(epoch_seconds):
    """
    Build protobuf timestamp fields 3, 7, and 10 from an epoch timestamp.
    Each is a sub-message with: sub-field 1 (varint) = seconds since epoch.
    """
    seconds = int(epoch_seconds)
    ts_inner = encode_varint((1 << 3) | 0) + encode_varint(seconds)
    return (
        encode_length_delimited(3, ts_inner)
        + encode_length_delimited(7, ts_inner)
        + encode_length_delimited(10, ts_inner)
    )


def has_timestamp_fields(inner_blob):
    """Check if the inner blob already contains timestamp fields (3, 7, or 10)."""
    if not inner_blob:
        return False
    try:
        pos = 0
        while pos < len(inner_blob):
            tag, pos = decode_varint(inner_blob, pos)
            fn = tag >> 3
            wt = tag & 7
            if fn in (3, 7, 10):
                return True
            pos = skip_protobuf_field(inner_blob, pos, wt)
    except Exception:
        pass
    return False


# ─── Metadata Extraction ─────────────────────────────────────────────────────

def extract_existing_metadata(db_path):
    """
    Read metadata from the database's trajectory data.
    Returns two dicts:
      - titles:      {conversation_id: title}  (non-fallback titles only)
      - inner_blobs: {conversation_id: raw_inner_protobuf_bytes}
    """
    from src.core.database import read_trajectory_data

    titles = {}
    inner_blobs = {}

    raw_b64 = read_trajectory_data(db_path)
    if not raw_b64:
        return titles, inner_blobs

    try:
        decoded = base64.b64decode(raw_b64)
        pos = 0

        while pos < len(decoded):
            tag, pos = decode_varint(decoded, pos)
            wire_type = tag & 7

            if wire_type != 2:
                break

            length, pos = decode_varint(decoded, pos)
            entry = decoded[pos:pos + length]
            pos += length

            ep, uid, info_b64 = 0, None, None
            while ep < len(entry):
                t, ep = decode_varint(entry, ep)
                fn, wt = t >> 3, t & 7
                if wt == 2:
                    l, ep = decode_varint(entry, ep)
                    content = entry[ep:ep + l]
                    ep += l
                    if fn == 1:
                        uid = content.decode('utf-8', errors='replace')
                    elif fn == 2:
                        sp = 0
                        _, sp = decode_varint(content, sp)
                        sl, sp = decode_varint(content, sp)
                        info_b64 = content[sp:sp + sl].decode('utf-8', errors='replace')
                elif wt == 0:
                    _, ep = decode_varint(entry, ep)
                else:
                    break

            if uid and info_b64:
                try:
                    raw_inner = base64.b64decode(info_b64)
                    inner_blobs[uid] = raw_inner

                    ip = 0
                    _, ip = decode_varint(raw_inner, ip)
                    il, ip = decode_varint(raw_inner, ip)
                    title = raw_inner[ip:ip + il].decode('utf-8', errors='replace')
                    if not title.startswith("Conversation (") and not title.startswith("Conversation "):
                        titles[uid] = title
                except Exception:
                    pass
    except Exception:
        pass

    return titles, inner_blobs


# ─── Title Resolution ────────────────────────────────────────────────────────

def get_title_from_brain(conversation_id, brain_dir=None):
    """
    Try to extract a title from brain artifact .md files.
    Returns the first markdown heading found, or None.
    """
    if brain_dir is None:
        brain_dir = get_brain_dir()

    brain_path = os.path.join(brain_dir, conversation_id)
    if not os.path.isdir(brain_path):
        return None

    for item in sorted(os.listdir(brain_path)):
        if item.startswith('.') or not item.endswith('.md'):
            continue
        try:
            filepath = os.path.join(brain_path, item)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                first_line = f.readline().strip()
            if first_line.startswith('#'):
                return first_line.lstrip('# ').strip()[:80]
        except Exception:
            pass

    return None


def resolve_title(conversation_id, existing_titles, brain_dir=None, conversations_dir=None):
    """
    Determine the best title for a conversation. Priority:
      1. Brain artifact .md heading
      2. Existing title from database (preserved)
      3. Fallback: date + short UUID
    Returns (title, source) where source is 'brain', 'preserved', or 'fallback'.
    """
    if brain_dir is None:
        brain_dir = get_brain_dir()
    if conversations_dir is None:
        conversations_dir = get_conversations_dir()

    brain_title = get_title_from_brain(conversation_id, brain_dir)
    if brain_title:
        return brain_title, "brain"

    if conversation_id in existing_titles:
        return existing_titles[conversation_id], "preserved"

    conv_file = os.path.join(conversations_dir, f"{conversation_id}.pb")
    if os.path.exists(conv_file):
        mod_time = time.strftime("%b %d", time.localtime(os.path.getmtime(conv_file)))
        return f"Conversation ({mod_time}) {conversation_id[:8]}", "fallback"

    return f"Conversation {conversation_id[:8]}", "fallback"


# ─── Trajectory Entry Builder ────────────────────────────────────────────────

def build_trajectory_entry(conversation_id, title, existing_inner_data=None,
                           workspace_path=None, pb_mtime=None):
    """
    Build a single trajectory summary protobuf entry.

    - If existing_inner_data is provided, title (field 1) is replaced but
      ALL other fields (workspace, timestamps, tool state) are preserved.
    - If workspace_path is provided and there is no existing workspace,
      a workspace field (field 9) is injected.
    - If pb_mtime is provided and timestamps are missing,
      timestamp fields (3, 7, 10) are injected for proper sorting.
    """
    if existing_inner_data:
        preserved_fields = strip_field_from_protobuf(existing_inner_data, 1)
        inner_info = encode_string_field(1, title) + preserved_fields
        if workspace_path:
            inner_info = strip_field_from_protobuf(inner_info, 9)
            inner_info += build_workspace_field(workspace_path)
        if pb_mtime and not has_timestamp_fields(existing_inner_data):
            inner_info += build_timestamp_fields(pb_mtime)
    else:
        inner_info = encode_string_field(1, title)
        if workspace_path:
            inner_info += build_workspace_field(workspace_path)
        if pb_mtime:
            inner_info += build_timestamp_fields(pb_mtime)

    info_b64 = base64.b64encode(inner_info).decode('utf-8')
    sub_message = encode_string_field(1, info_b64)

    entry = encode_string_field(1, conversation_id)
    entry += encode_length_delimited(2, sub_message)
    return entry
