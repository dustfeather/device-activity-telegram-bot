# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

Two standalone scripts wired to OS task schedulers (Windows `taskschd.msc`, cron):

- `src/send.py` — one-shot: on login/unlock, sends a notification, exits.
- `src/halt.py` — long-running: sends a startup notification, then `run_polling()`
  listens for `/halt [DEVICENAME]` and shuts down the host.

`halt.py` and `send.py` use different Telegram layers: `halt.py` uses the
`python-telegram-bot` `Application` for *inbound* commands; all *outbound*
notifications go through the raw httpx `send_message()` in `telegram_client.py`.

`src/config.py`: `settings` is a lazy `_SettingsProxy` — the pydantic `Settings`
object is constructed only on first attribute access. Under pytest it falls back
to a `MagicMock` if env validation fails, so tests must mock settings before use.

## Invariants — preserve when editing

- `bot_token` / `chat_id` are regex-validated in BOTH `config.py` and
  `telegram_client.py` (SSRF defense; token is interpolated into the API URL) —
  keep both in sync.
- `halt()` regex-checks `DEVICENAME` and shuts down only when it matches
  `platform.node()` (command-injection / wrong-host defense).

## Conventions

- Python 3.14+; `src/` layout — run scripts as modules (`python -m src.send`).
- Config from `.env`: `BOT_TOKEN`, `CHAT_ID`.
- mypy is strict (typed defs required); ruff line-length 100.
- Repo is rebase-merge only.
