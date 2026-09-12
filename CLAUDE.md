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
