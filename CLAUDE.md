# CLAUDE.md

## Architecture

Two scripts wired to OS schedulers (Windows `taskschd.msc`, cron):
- `src/send.py` — one-shot: login/unlock notification, exits.
- `src/halt.py` — long-running: startup notification, then `run_polling()` for `/halt [DEVICENAME]` → shut down host.

Different Telegram layers: `halt.py` uses `python-telegram-bot` `Application` for inbound; ALL outbound goes through raw httpx `send_message()` in `telegram_client.py`.

`src/config.py`: `settings` is lazy `_SettingsProxy` — pydantic `Settings` built on first attr access. Under pytest falls back to `MagicMock` if env validation fails → tests MUST mock settings before use.

## Invariants — preserve

- `bot_token`/`chat_id` regex-validated in BOTH `config.py` AND `telegram_client.py` (SSRF defense; token interpolated into API URL). Keep both in sync.
- `halt()` regex-checks `DEVICENAME`, shuts down only when matches `platform.node()` (command-injection / wrong-host defense).
- `halt()` rejects senders not in `settings.authorized_user_ids` BEFORE parsing args, and the handler is registered behind `filters.User` (unauthenticated-remote-shutdown defense). Both are needed: `error_handler` re-invokes `halt()` directly, bypassing handler filters. `CHAT_ID` is an outbound destination, never an inbound authorization.

## Conventions

- Python 3.14+; `src/` layout — run as modules (`python -m src.send`).
- Config from `.env`: `BOT_TOKEN`, `CHAT_ID`, optional `ALLOWED_USER_IDS` (comma-separated; defaults to `CHAT_ID`, required when `CHAT_ID` is negative).
- mypy strict; ruff line-length 100.
- Rebase-merge only.

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
| ------ | ---------- |
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
