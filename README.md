# Guitar Fretboard Learning Bot

A Telegram bot designed to help users learn and memorize notes on the guitar fretboard.

## Features
- Practice note recognition on standard tuning (E-A-D-G-B-E)
- Configurable fret range (3, 5, 7, 9, or 12 frets)
- Visual fretboard representation
- Interactive learning with immediate feedback

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your Telegram Bot Token:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

4. Run the bot:
```bash
python bot.py
```

## Usage
1. Start the bot with `/start`
2. Select the number of frets you want to practice
3. Answer the questions about notes on different frets
4. Get immediate feedback on your answers

## Commands
- `/start` - Start the bot and show welcome message
- `/setfret` - Change maximum fret number
- `/help` - Show instructions 