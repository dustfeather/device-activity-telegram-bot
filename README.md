# Device Activity Telegram Bot

## Requirements

* Python 3.14 or higher
* A registered telegram bot - [@BotFather](https://t.me/BotFather)
* Your personal telegram id - [@myidbot](https://t.me/myidbot)

## Python Version Management

This project requires Python 3.14. If you need to manage multiple Python versions:

### Windows (using pyenv-win)

1. **Install pyenv-win**:
   ```powershell
   Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
   ```

2. **Reload environment in editor terminal** (if needed):
   ```powershell
   $env:Path += ";$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims"
   ```

3. **Install and set Python 3.14**:
   ```powershell
   pyenv install 3.14.0
   pyenv local 3.14.0  # For this project
   # or
   pyenv global 3.14.0  # System-wide default
   ```

### Linux/macOS (using pyenv)

1. **Install pyenv**:
   ```bash
   # macOS
   brew install pyenv
   
   # Linux
   curl https://pyenv.run | bash
   ```

2. **Install and set Python 3.14**:
   ```bash
   pyenv install 3.14.0
   pyenv local 3.14.0  # For this project
   # or
   pyenv global 3.14.0  # System-wide default
   ```

## Installation

1. **Clone the repository**:
   ```sh
   git clone <repository-url>
   cd device-activity-telegram-bot
   ```

2. **Create a virtual environment**:
   ```sh
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Configure environment variables**:
   ```sh
   cp .env.example .env
   # Edit .env with your BOT_TOKEN and CHAT_ID
   ```

## Usage

```sh
# Run send.py (triggers on login/screen unlock)
python -m src.send

# Run halt.py (triggers on screen lock, listens for shutdown commands)
python -m src.halt
```

Or add manually to `taskschd.msc`:

![taskschd.msc screenshot](https://github.com/dustfeather/device-activity-telegram-bot/blob/main/taskschd.msc.png?raw=true)

* `src/send.py` - Sends notification when device is logged into
* `src/halt.py` - Listens for remote shutdown commands via `/halt`

## Telegram Commands

```sh
/halt              # Shutdown all machines running halt.py
/halt DEVICENAME   # Shutdown a specific machine
```

## Development

### Code Quality

```sh
ruff check src/ tests/      # Lint
ruff format src/ tests/     # Format
mypy src/                   # Type check
pytest -v                   # Test
```

See `TESTING.md` for detailed test instructions.

## Demo

[![preview](https://img.youtube.com/vi/vWEMChJ3yJY/0.jpg)](https://youtube.com/shorts/vWEMChJ3yJY)
