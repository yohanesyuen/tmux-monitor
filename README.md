# tmux-mcp

An MCP server exposing local `tmux` control (panes, windows, capture) as tools, backed by the `tmux` CLI via `subprocess`.

## Setup

```bash
uv sync   # or: pip install -e .
```

Requires `tmux` installed and on `PATH`. No credentials or config needed — it drives whatever local tmux server is running.

## Usage

```bash
tmux-mcp
# or
python server.py
```

Runs over stdio (`mcp.run()` default transport).

### Tools

- `list_panes()` — list all sessions/windows/panes with cmd, path, size
- `snapshot(target, scrollback=500)` — one-shot capture of a pane's visible content + scrollback
- `start_capture(target)` / `stop_capture(target)` — stream a pane's live output to a log file via `tmux pipe-pane`
- `read_output(target, lines=100)` / `clear_output(target)` — read or clear the streamed log for a pane
- `split_pane(target, vertical=True, start_dir="")` — split a pane
- `send_keys(target, keys, enter=True)` — send keystrokes/commands to a pane
- `kill_pane(target)` — kill a pane
- `new_window(session, name="", start_dir="")` — create a window in a session
- `rename_window(target, new_name)` — rename a window
- `select_pane(target)` — focus a pane

`target` follows tmux's own addressing, e.g. `"mysession:1.0"` (session:window.pane) or `"0:1"` (window only).

## Data

Streamed pane logs are written to `~/.tmux-mcp-logs/<session>_<window>_<pane>.log` (colons and dots in the target are replaced with underscores). No database.
