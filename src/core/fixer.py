"""
Main orchestrator — scan() and fix() with callback support.

Usage:
    from src.core.fixer import scan, fix, Callbacks

    # Step 1: Scan (read-only, no DB writes)
    conversations = scan()

    # Step 2: Fix (rebuild index, write to DB)
    result = fix(conversations, workspace_assignments={...})
"""

import base64
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from src.core import paths, scanner, database, protobuf


@dataclass
class ConversationInfo:
    """Information about a single conversation."""
    id: str
    title: str
    source: str                          # "brain" | "preserved" | "fallback"
    has_workspace: bool
    workspace_uri: Optional[str] = None
    inner_data: Optional[bytes] = None   # preserved protobuf blob (internal)


@dataclass
class FixResult:
    """Result summary after fixing."""
    total: int
    by_source: dict                      # {"brain": N, "preserved": N, "fallback": N}
    workspaces_mapped: int
    timestamps_injected: int
    conversations: list                  # list[ConversationInfo]
    backup_path: Optional[str] = None


@dataclass
class Callbacks:
    """Callbacks for progress reporting."""
    on_progress: Optional[Callable] = None   # (message: str, percent: float)
    on_log: Optional[Callable] = None        # (message: str)
    on_error: Optional[Callable] = None      # (message: str)


def _emit(callback, *args):
    """Safely call a callback if it exists."""
    if callback:
        callback(*args)


def scan(callbacks=None):
    """
    Step 1: Scan all conversations on disk.
    This is READ-ONLY — no database writes happen here.

    Returns a list of ConversationInfo objects for preview/review
    before the user decides to fix.

    Raises RuntimeError if required paths don't exist.
    """
    if callbacks is None:
        callbacks = Callbacks()

    db_path = paths.get_db_path()
    conv_dir = paths.get_conversations_dir()
    brain_dir = paths.get_brain_dir()

    # Validate required paths
    errors = paths.validate_paths()
    if errors:
        for e in errors:
            _emit(callbacks.on_error, e)
        raise RuntimeError(errors[0])

    # Discover conversation files
    _emit(callbacks.on_log, f"Scanning: {conv_dir}")
    conv_ids = scanner.discover_conversations(conv_dir)

    if not conv_ids:
        _emit(callbacks.on_log, "No conversations found on disk.")
        return []

    _emit(callbacks.on_log, f"Found {len(conv_ids)} conversations")

    # Read existing metadata from database
    existing_titles, existing_blobs = scanner.extract_existing_metadata(db_path)
    _emit(callbacks.on_log, f"Existing titles: {len(existing_titles)}, blobs: {len(existing_blobs)}")

    # Resolve each conversation
    results = []
    total = len(conv_ids)

    for i, cid in enumerate(conv_ids):
        title, source = scanner.resolve_title(cid, existing_titles, brain_dir, conv_dir)
        inner = existing_blobs.get(cid)
        has_ws = bool(inner and scanner.extract_workspace_hint(inner))
        ws_uri = scanner.extract_workspace_hint(inner) if inner else None

        results.append(ConversationInfo(
            id=cid,
            title=title,
            source=source,
            has_workspace=has_ws,
            workspace_uri=ws_uri,
            inner_data=inner,
        ))
        _emit(callbacks.on_progress, title, (i + 1) / total)

    return results


def auto_assign_workspaces(conversations, callbacks=None):
    """
    Attempt to auto-assign workspaces for conversations without one.
    Returns dict: {conversation_id: folder_path} for successfully inferred ones.
    """
    if callbacks is None:
        callbacks = Callbacks()

    brain_dir = paths.get_brain_dir()
    if not os.path.isdir(brain_dir):
        return {}

    assignments = {}
    unmapped = [c for c in conversations if not c.has_workspace]

    for i, conv in enumerate(unmapped):
        inferred = scanner.infer_workspace_from_brain(conv.id, brain_dir)
        if inferred and os.path.isdir(inferred):
            assignments[conv.id] = inferred
            _emit(callbacks.on_log, f"  [{i+1}] {conv.title[:40]} -> {os.path.basename(inferred)}")
        _emit(callbacks.on_progress, conv.title, (i + 1) / max(len(unmapped), 1))

    _emit(callbacks.on_log, f"Auto-assigned {len(assignments)} workspace(s)")
    return assignments


def fix(conversations, workspace_assignments=None, callbacks=None):
    """
    Step 2: Rebuild the conversation index and write to the database.
    Automatically creates a backup before writing.

    Args:
        conversations: List of ConversationInfo from scan()
        workspace_assignments: Optional dict {conversation_id: folder_path}
        callbacks: Optional Callbacks for progress reporting

    Returns FixResult with summary statistics.
    """
    if callbacks is None:
        callbacks = Callbacks()
    if workspace_assignments is None:
        workspace_assignments = {}

    db_path = paths.get_db_path()
    conv_dir = paths.get_conversations_dir()

    # Backup current data
    backup_dir = os.path.dirname(os.path.abspath(db_path))
    backup_path = os.path.join(backup_dir, "trajectorySummaries_backup.txt")
    backed_up = database.backup_current_data(db_path, backup_path)
    if backed_up:
        _emit(callbacks.on_log, f"Backup saved: {backup_path}")

    # Build new index
    result_bytes = b""
    stats = {"brain": 0, "preserved": 0, "fallback": 0}
    ws_total = 0
    ts_injected = 0
    total = len(conversations)

    for i, conv in enumerate(conversations):
        ws_path = workspace_assignments.get(conv.id)
        pb_path = os.path.join(conv_dir, f"{conv.id}.pb")
        pb_mtime = os.path.getmtime(pb_path) if os.path.exists(pb_path) else None

        entry = scanner.build_trajectory_entry(
            conv.id, conv.title, conv.inner_data, ws_path, pb_mtime
        )
        result_bytes += protobuf.encode_length_delimited(1, entry)

        stats[conv.source] += 1
        if conv.has_workspace or ws_path:
            ws_total += 1
        if pb_mtime and (not conv.inner_data or not scanner.has_timestamp_fields(conv.inner_data)):
            ts_injected += 1

        _emit(callbacks.on_progress, conv.title, (i + 1) / total)

    # Write to database
    encoded = base64.b64encode(result_bytes).decode('utf-8')
    database.write_trajectory_data(db_path, encoded)
    _emit(callbacks.on_log, f"Index rebuilt: {total} conversations")

    return FixResult(
        total=total,
        by_source=stats,
        workspaces_mapped=ws_total,
        timestamps_injected=ts_injected,
        conversations=conversations,
        backup_path=backup_path if backed_up else None,
    )
