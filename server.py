#!/usr/bin/env python3
import subprocess
import time
from pathlib import Path
from mcp.server.fastmcp import FastMCP

LOG_DIR = Path.home() / ".tmux-mcp-logs"
LOG_DIR.mkdir(exist_ok=True)

mcp = FastMCP("tmux-monitor")


def _log_path(target: str) -> Path:
    safe = target.replace(":", "_").replace(".", "_")
    return LOG_DIR / f"{safe}.log"


@mcp.tool()
def list_panes() -> str:
    """List all tmux sessions, windows, and panes with their IDs."""
    result = subprocess.run(
        [
            "tmux", "list-panes", "-a", "-F",
            "#{session_name}:#{window_index}.#{pane_index}  "
            "cmd=#{pane_current_command}  "
            "path=#{pane_current_path}  "
            "size=#{pane_width}x#{pane_height}",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout.strip() or "No tmux sessions found."


@mcp.tool()
def start_capture(target: str) -> str:
    """Start streaming a pane's output to a log file via pipe-pane.

    Args:
        target: tmux pane target e.g. "mysession:1.0" or "0:0.0"
    """
    path = _log_path(target)
    path.touch()
    result = subprocess.run(
        ["tmux", "pipe-pane", "-t", target, "-o", f"cat >> {path}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Streaming pane {target} → {path}"


@mcp.tool()
def stop_capture(target: str) -> str:
    """Stop streaming a pane's output.

    Args:
        target: tmux pane target e.g. "mysession:1.0"
    """
    result = subprocess.run(
        ["tmux", "pipe-pane", "-t", target],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Stopped capture for {target}"


@mcp.tool()
def read_output(target: str, lines: int = 100) -> str:
    """Read recent streamed output from a pane's log.

    Args:
        target: tmux pane target e.g. "mysession:1.0"
        lines: how many tail lines to return (default 100)
    """
    path = _log_path(target)
    if not path.exists():
        return f"No log for {target} — run start_capture first."
    result = subprocess.run(
        ["tail", "-n", str(lines), str(path)],
        capture_output=True, text=True,
    )
    return result.stdout or "(empty)"


@mcp.tool()
def clear_output(target: str) -> str:
    """Clear the log file for a pane without stopping capture.

    Args:
        target: tmux pane target e.g. "mysession:1.0"
    """
    path = _log_path(target)
    if not path.exists():
        return f"No log found for {target}."
    path.write_text("")
    return f"Cleared log for {target}"


@mcp.tool()
def snapshot(target: str, scrollback: int = 500) -> str:
    """On-demand snapshot of a pane's current visible content + scrollback.

    Args:
        target: tmux pane target e.g. "mysession:1.0"
        scrollback: lines of history to include (default 500)
    """
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", target, "-p", "-S", f"-{scrollback}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return result.stdout or "(empty pane)"


@mcp.tool()
def split_pane(target: str, vertical: bool = True, start_dir: str = "") -> str:
    """Split a pane horizontally or vertically.

    Args:
        target: tmux pane target e.g. "0:1.1"
        vertical: True for vertical split (new pane below), False for horizontal (new pane right)
        start_dir: starting directory for the new pane (defaults to pane's current path)
    """
    cmd = ["tmux", "split-window", "-t", target]
    if vertical:
        cmd.append("-v")
    else:
        cmd.append("-h")
    if start_dir:
        cmd += ["-c", start_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Split pane {target} ({'vertical' if vertical else 'horizontal'})"


@mcp.tool()
def send_keys(target: str, keys: str, enter: bool = True) -> str:
    """Send keystrokes or a command to a pane.

    Args:
        target: tmux pane target e.g. "0:1.2"
        keys: the text or key sequence to send
        enter: whether to press Enter after sending (default True)
    """
    cmd = ["tmux", "send-keys", "-t", target, keys]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    if enter:
        time.sleep(0.1)
        subprocess.run(["tmux", "send-keys", "-t", target, "Enter"])
    return f"Sent keys to {target}"


@mcp.tool()
def kill_pane(target: str) -> str:
    """Kill a pane.

    Args:
        target: tmux pane target e.g. "0:1.2"
    """
    result = subprocess.run(
        ["tmux", "kill-pane", "-t", target],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Killed pane {target}"


@mcp.tool()
def new_window(session: str, name: str = "", start_dir: str = "") -> str:
    """Create a new window in a session.

    Args:
        session: session name or index e.g. "0" or "main"
        name: optional window name
        start_dir: starting directory (defaults to session's working dir)
    """
    cmd = ["tmux", "new-window", "-t", session]
    if name:
        cmd += ["-n", name]
    if start_dir:
        cmd += ["-c", start_dir]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"New window created in session {session}" + (f" named '{name}'" if name else "")


@mcp.tool()
def rename_window(target: str, new_name: str) -> str:
    """Rename a window.

    Args:
        target: tmux window target e.g. "0:1" or "main:2"
        new_name: the new name for the window
    """
    result = subprocess.run(
        ["tmux", "rename-window", "-t", target, new_name],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Renamed window {target} to '{new_name}'"


@mcp.tool()
def select_pane(target: str) -> str:
    """Focus a specific pane.

    Args:
        target: tmux pane target e.g. "0:1.2"
    """
    result = subprocess.run(
        ["tmux", "select-pane", "-t", target],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.strip()}"
    return f"Selected pane {target}"


def main():
    mcp.run()


if __name__ == "__main__":
    main()
