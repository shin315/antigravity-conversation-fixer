"""Rich-based Terminal UI for Antigravity Fixer."""

import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich import box

from src.core import fixer, process
from src.core.fixer import Callbacks
from src.i18n import t


console = Console()


def _source_icon(source):
    """Return colored source indicator."""
    icons = {"brain": "🟢", "preserved": "🔵", "fallback": "🟡"}
    return icons.get(source, "⚪")


def _source_label(source):
    """Return translated source label."""
    keys = {"brain": "source_brain", "preserved": "source_preserved", "fallback": "source_fallback"}
    return t(keys.get(source, source))


def _check_antigravity():
    """Check if Antigravity is running and offer to kill it."""
    if not process.is_antigravity_running():
        console.print(f"  {t('ag_not_running')}")
        return True

    console.print(f"  {t('ag_running')}")
    console.print(f"  {t('ag_running_detail')}")
    console.print()

    if Confirm.ask(f"  {t('ag_kill_confirm')}", default=True):
        if process.kill_antigravity():
            console.print(f"  {t('ag_kill_success')}")
            return True
        else:
            console.print(f"  {t('ag_kill_fail')}")
            return False
    else:
        return False


def _scan_conversations():
    """Scan conversations with a progress bar."""
    conversations = []

    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(t("scanning"), total=1.0)

        def on_progress(msg, pct):
            progress.update(task, completed=pct)

        def on_log(msg):
            pass  # Suppress during progress

        callbacks = Callbacks(on_progress=on_progress, on_log=on_log)

        try:
            conversations = fixer.scan(callbacks)
        except RuntimeError as e:
            console.print(f"\n  [red]{t('error_generic', msg=str(e))}[/red]")
            return []

        progress.update(task, completed=1.0)

    return conversations


def _display_conversation_table(conversations):
    """Display conversations in a Rich table."""
    table = Table(box=box.ROUNDED, show_lines=False, pad_edge=True)
    table.add_column(t("col_num"), style="dim", width=5, justify="right")
    table.add_column(t("col_title"), min_width=30)
    table.add_column(t("col_source"), width=12, justify="center")
    table.add_column(t("col_workspace"), width=5, justify="center")

    for i, conv in enumerate(conversations, 1):
        icon = _source_icon(conv.source)
        label = _source_label(conv.source)
        ws = "✓" if conv.has_workspace else ""
        table.add_row(
            str(i),
            conv.title[:50],
            f"{icon} {label}",
            ws,
        )

    console.print(table)
    console.print(f"  {t('tui_legend')}")


def _workspace_assignment(conversations):
    """Handle workspace assignment flow."""
    unmapped = [c for c in conversations if not c.has_workspace]
    if not unmapped:
        return {}

    console.print()
    console.print(f"  {t('ws_choose_desc', n=len(unmapped))}")
    console.print()
    console.print(f"  [1] {t('ws_option_auto')}")
    console.print(f"  [2] {t('ws_option_auto_manual')}")
    console.print()

    choice = Prompt.ask(f"  {t('tui_your_choice')}", choices=["1", "2"], default="1")

    # Auto-assign
    console.print()
    ws_assignments = {}

    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(t("ws_auto_assign"), total=1.0)

        def on_progress(msg, pct):
            progress.update(task, completed=pct)

        def on_log(msg):
            console.print(f"  {msg}")

        callbacks = Callbacks(on_progress=on_progress, on_log=on_log)
        ws_assignments = fixer.auto_assign_workspaces(conversations, callbacks)
        progress.update(task, completed=1.0)

    # Manual assignment for option 2
    if choice == "2":
        still_unmapped = [c for c in unmapped if c.id not in ws_assignments]
        if still_unmapped:
            console.print()
            console.print(f"  [bold]{t('ws_choose_title')}[/bold]")
            ws_assignments.update(_interactive_assign(still_unmapped))
        else:
            console.print(f"  {t('ws_all_assigned')}")

    console.print()
    return ws_assignments


def _interactive_assign(unmapped_convos):
    """Manually assign workspaces one by one."""
    assignments = {}
    batch_path = None

    for i, conv in enumerate(unmapped_convos, 1):
        if batch_path:
            assignments[conv.id] = batch_path
            console.print(f"  [{i:3d}] {conv.title[:45]} {t('ws_mapped', name=os.path.basename(batch_path))}")
            continue

        console.print(f"\n  [{i:3d}] {conv.title[:55]}")

        while True:
            raw = Prompt.ask(f"    {t('ws_prompt')}", default="")

            if raw == "":
                console.print(f"    {t('ws_skip')}")
                break
            if raw.lower() == "q":
                console.print(f"    {t('ws_stop')}")
                return assignments
            if raw.lower() == "all":
                batch_input = Prompt.ask(f"    {t('ws_batch_prompt')}", default="")
                if batch_input and os.path.isdir(batch_input.strip('"').strip("'")):
                    batch_path = batch_input.strip('"').strip("'").rstrip("\\/")
                    assignments[conv.id] = batch_path
                    break
                continue

            folder = raw.strip('"').strip("'").rstrip("\\/")
            if os.path.isdir(folder):
                assignments[conv.id] = folder
                console.print(f"    {t('ws_mapped', name=os.path.basename(folder))}")
                break
            else:
                console.print(f"    {t('ws_path_not_found', path=folder)}")

    return assignments


def _run_fix(conversations, ws_assignments):
    """Execute the fix with a progress bar."""
    result = None

    with Progress(
        TextColumn("[bold green]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(t("fixing"), total=1.0)

        def on_progress(msg, pct):
            progress.update(task, completed=pct)

        def on_log(msg):
            pass

        callbacks = Callbacks(on_progress=on_progress, on_log=on_log)
        result = fixer.fix(conversations, ws_assignments, callbacks)
        progress.update(task, completed=1.0)

    return result


def _display_result(result):
    """Display fix result summary."""
    stats = result.by_source
    lines = [
        f"  {t('fix_success', n=result.total)}",
        f"  {t('fix_stats', brain=stats.get('brain', 0), preserved=stats.get('preserved', 0), fallback=stats.get('fallback', 0))}",
        f"  {t('fix_ws_stats', ws=result.workspaces_mapped, ts=result.timestamps_injected)}",
    ]
    console.print()
    console.print(Panel(
        "\n".join(lines),
        border_style="green",
        padding=(1, 2),
    ))
    console.print(f"\n  {t('fix_reopen')}")


def run():
    """Main TUI entry point."""
    # Header
    console.print()
    console.print(Panel(
        f"  🔧 {t('app_title')}  {t('app_version')}",
        border_style="blue",
        padding=(0, 2),
    ))
    console.print()

    # Check Antigravity
    if not _check_antigravity():
        console.print()
        Prompt.ask(t("tui_press_enter"))
        return

    console.print()

    # Scan
    conversations = _scan_conversations()
    if not conversations:
        console.print(f"  {t('found_none')}")
        Prompt.ask(t("tui_press_enter"))
        return

    console.print(f"\n  📂 {t('found_n', n=len(conversations))}\n")

    # Display table
    _display_conversation_table(conversations)

    # Workspace assignment
    ws_assignments = _workspace_assignment(conversations)

    # Fix
    result = _run_fix(conversations, ws_assignments)

    # Result
    _display_result(result)

    # Offer to launch
    console.print()
    if Confirm.ask(f"  {t('btn_launch')}?", default=False):
        if process.launch_antigravity():
            console.print(f"  {t('ag_launch_success')}")
        else:
            console.print(f"  {t('ag_launch_fail')}")

    console.print()
