# Device Activity Telegram Bot

## Usage:

```sh
cp .env.example .env
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python send.py
# compile for windows
cp .spec.template send.spec
pyinstaller send.spec
dist/send.exe
```
