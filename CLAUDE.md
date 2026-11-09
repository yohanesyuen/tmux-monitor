# CLAUDE.md

Single-file MCP server (`server.py`) that shells out to the `tmux` CLI via `subprocess.run` — no tmux library dependency, no persistent state beyond log files.

## Structure

- Every `@mcp.tool()` function maps ~1:1 to a `tmux` subcommand; the pattern is: build argv, run, return `stdout` or `f"Error: {stderr}"` on non-zero exit.
- `_log_path()` derives a filesystem-safe log filename from a pane target for the capture tools (`start_capture`/`stop_capture`/`read_output`/`clear_output`), which drive `tmux pipe-pane`.
- `snapshot()` is stateless (`tmux capture-pane`) and doesn't touch the log files — prefer it over start/stop capture for one-off reads.

## Conventions

- Keep new tools consistent: one `tmux` subcommand per tool, same error-handling shape (`if result.returncode != 0: return f"Error: {result.stderr.strip()}"`).
- `target` strings follow tmux's own `session:window.pane` addressing — don't invent a different addressing scheme.
- No test suite currently exists.
