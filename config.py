import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Guitar Configuration
STRINGS = {
    1: "E",  # highest string
    2: "B",
    3: "G",
    4: "D",
    5: "A",
    6: "E"   # lowest string
}

NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
FRET_OPTIONS = [3, 5, 7, 9, 12]

# Visual Configuration
FRET_SYMBOL = "|"
QUESTION_MARK = "❓"  # Using emoji for better visibility
OPEN_STRING = " ◯ "    # Circle symbol for open string
NOTE_SPACING = 2     # Number of spaces for note alignment 