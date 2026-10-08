# device-activity-telegram-bot

## Goal

A Telegram device-activity notifier. It watches OS login/screen-unlock events on a machine and pushes a Telegram message when the device is accessed, plus a companion long-running monitor that lets you remotely shut machines down via a `/halt` command.

- `src/send.py` — fires on login/unlock, sends "Your device 'name' has been logged into."
- `src/halt.py` — sends a startup notification, then long-polls Telegram for `/halt [DEVICENAME]` and shuts down the host when the device name matches.

## Stack

- Python 3.14+ (confirmed: `requires-python = ">=3.14"`, `.python-version` = 3.14, `target-version = py314`).
- `python-telegram-bot` >= 21.6 — inbound command handling (`Application` + `run_polling`).
- `httpx` — raw outbound calls to the Telegram Bot API (`sendMessage`).
- `pydantic-settings` — config from `.env` (`BOT_TOKEN`, `CHAT_ID`).
- Windows extras: `pywin32`, `pywin32-ctypes`.
- Dev: pytest + pytest-asyncio, ruff (line-length 100), mypy strict.

## Repo

- `dustfeather/device-activity-telegram-bot` (confirmed: `git@github.com:dustfeather/device-activity-telegram-bot.git`).
- Layout: `src/` package run as modules — `config.py` (lazy pydantic settings proxy), `telegram_client.py` (outbound `send_message`), `send.py`, `halt.py`. Tests in `tests/`. `.github/workflows/` for CI (Claude review, PR checks, Dependabot auto-merge).

## Deploy

Runs locally on each monitored device, wired to that OS's scheduler — Windows Task Scheduler (`taskschd.msc`, screenshot in repo) and cron on Linux/macOS. `send.py` is a one-shot triggered on login/unlock; `halt.py` is a long-running monitor. No container, systemd unit, or in-cluster manifest in the repo, so it is not hosted on the homelab cluster — it runs on the personal machines being monitored.

## Status

active — v1.0.0. Initial release 2024-05-17; full pytest suite added 2025-11-19; recent work is CI/tooling (shared workflows @v2, ARC runner pinning, ruff pin).

## Tasks

Open GitHub issues:

- [ ] [device-activity-telegram-bot#34](https://github.com/dustfeather/device-activity-telegram-bot/issues/34) — rewrite as a native cross-platform service (.NET), replacing the pywin32 + Task Scheduler / systemd-script setup *(epic)*

## Notes

- Detection method: relies on the OS scheduler to fire on the activity event — Windows Task Scheduler login/unlock triggers, cron on Linux/macOS. The app itself does not hook events; `send.py` just runs and reports `platform.node()`.
- Schedule: `send.py` is event-triggered (one-shot per login/unlock); `halt.py` runs continuously via `run_polling()`.
- Security invariants: `bot_token`/`chat_id` are regex-validated in both `config.py` and `telegram_client.py` (SSRF defense — token is interpolated into the API URL); `halt()` regex-checks `DEVICENAME` and only shuts down when it matches `platform.node()` (command-injection / wrong-host defense).
- Area: Software Engineering

## Log

- **2026-05-31** — Note created from repo scan.
- **2026-05-31** — Moved task tracking from Jira (DAT-1) back to GitHub issue #34.
