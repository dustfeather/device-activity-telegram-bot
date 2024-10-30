# Device Activity Telegram Bot

## Requirement

```sh
cp .env.example .env
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python send.py
```

## Compile for Windows

```sh
venv/bin/pyinstaller --name send.exe --onefile --add-data ".env;." send.py
venv/bin/pyinstaller --name halt.exe --onefile --add-data ".env;." halt.py
venv/bin/pyinstaller --name windows_service.exe --onefile --add-data ".env;." windows_service.py
```

## Usage

```sh
## check dist/ for executable file
.\windows_service.exe --startup auto install
net start DeviceActivityTelegramBot
```

Or add manually to `taskschd.msc`:

![taskschd.msc screenshot](https://github.com/dustfeather/device-activity-telegram-bot/blob/main/taskschd.msc.png?raw=true)