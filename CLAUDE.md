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

## Conventions

- Python 3.14+; `src/` layout — run as modules (`python -m src.send`).
- Config from `.env`: `BOT_TOKEN`, `CHAT_ID`.
- mypy strict; ruff line-length 100.
- Rebase-merge only.
