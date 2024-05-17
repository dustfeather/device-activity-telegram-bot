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
# check dist/ for executable file
```
