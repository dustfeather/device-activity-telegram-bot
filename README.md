# Device Activity Telegram Bot

## Requirements
* a registered telegram bot - [@BotFather](https://t.me/BotFather)
* your personal telegram id - [@myidbot](https://t.me/myidbot)

## Usage

```sh
cp .env.example .env
virtualenv venv
venv/bin/pip install -r requirements.txt
venv/bin/python send.py
venv/bin/python halt.py
```
Or add manually to `taskschd.msc`:

![taskschd.msc screenshot](https://github.com/dustfeather/device-activity-telegram-bot/blob/main/taskschd.msc.png?raw=true)

* send.py - should be triggered on every login / screen unlock and sends a notification that someone logged into your device
* halt.py - should be triggered on every screen lock and listens for remote shutdown commands

## Telegram Usage
```sh
/halt # sends a shutdown command to every machine that has halt.py running
/halt DEVICENAME # sends a shutdown command to a specific machine
```

## Demo
[![preview](https://img.youtube.com/vi/vWEMChJ3yJY/0.jpg)](https://youtube.com/shorts/vWEMChJ3yJY)