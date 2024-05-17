# Device Activity Telegram Bot

## Usage:

```sh
cp .env.example .env
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python send.py
# compile for windows
venv/bin/pyinstaller --name send.exe --onefile --add-data ".env;." send.py
venv/bin/pyinstaller --name halt.exe --onefile --add-data ".env;." halt.py
venv/bin/pyinstaller --name windows_service.exe --onefile --add-data ".env;." windows_service.py
# check dist/ for executable file
.\windows_service.exe --startup auto install
net start DeviceActivityTelegramBot
```
