from typing import Dict, List, Tuple
import random
import config

def calculate_note_at_fret(open_note: str, fret_number: int) -> str:
    """Calculate the note at a specific fret given the open note."""
    start_index = config.NOTES.index(open_note)
    return config.NOTES[(start_index + fret_number) % len(config.NOTES)]

def create_fretboard(max_fret: int) -> Dict[int, List[str]]:
    """Create a complete fretboard mapping of all notes."""
    fretboard = {}
    for string_num, open_note in config.STRINGS.items():
        string_notes = []
        for fret in range(max_fret + 1):  # +1 to include open string (fret 0)
            note = calculate_note_at_fret(open_note, fret)
            string_notes.append(note)
        fretboard[string_num] = string_notes
    return fretboard

def visualize_string_horizontal(string_num: int, notes: List[str], target_fret: int = None) -> str:
    """Visualize a single string horizontally with optional target fret marked with '?'."""
    # Use lowercase 'e' for the first string
    string_name = 'e' if string_num == 1 else config.STRINGS[string_num]
    # Start with string name and open string note, marked with circle symbol
    result = f"{string_name} | ◯ |"
    
    for fret in range(1, len(notes)):
        if fret == target_fret:
            # Add emphasis around the question mark
            result += f" {config.QUESTION_MARK} |"
        else:
            # For hidden notes (shown as "---"), don't add extra space
            if notes[fret] == "---":
                result += f" {notes[fret]} |"
            else:
                # Align other notes, adding extra space for non-sharp notes
                note = notes[fret] + " " if len(notes[fret]) == 1 else notes[fret]
                result += f" {note} |"
    return result

def create_vertical_fretboard(fretboard: Dict[int, List[str]], max_fret: int, target_string: int = None, target_fret: int = None, mode: str = 'show') -> List[str]:
    """Create a vertical representation of the fretboard."""
    # Create header with string names - each cell is exactly 5 chars wide
    header = "    |"  # 4 spaces for fret numbers
    for string_num in range(6, 0, -1):  # Reverse order for strings
        string_name = 'e' if string_num == 1 else config.STRINGS[string_num]
        # Single character notes get 2 spaces on each side
        header += f"  {string_name}  |"  # 2 spaces + note + 2 spaces = 5 chars
    
    # Create separator line matching header exactly
    separator = "--+" + "---+" * 6  # 4 dashes + 5 dashes per column
    
    # Create fret rows
    rows = []
    for fret in range(max_fret + 1):
        # Add padding for single-digit fret numbers to maintain 4 char width
        fret_padding = " " if fret < 10 else ""
        row = f"{fret}{fret_padding} |"
        
        for string_num in range(6, 0, -1):  # Reverse order for strings
            note = fretboard[string_num][fret]
            
            # Handle target note - maintain 5 char width
            if fret == target_fret and string_num == target_string:
                row += f"  {config.QUESTION_MARK}  |"
            # Handle open strings - maintain 5 char width
            elif fret == 0:
                row += f"  0  |"
            # Handle hidden notes - maintain 5 char width
            elif mode == 'hide' and (fret != target_fret or string_num != target_string):
                row += f" --- |"
            # Handle regular notes - maintain 5 char width
            else:
                # Adjust padding based on note length (1 or 2 characters)
                if len(note) == 1:
                    row += f"  {note}  |"  # 2 spaces on each side for single char
                else:
                    row += f" {note} |"   # 1 space before, 2 after for sharp notes
        rows.append(row)
    
    # Combine all parts
    return [header, separator] + rows

def create_question(max_fret: int, orientation: str = 'vertical', mode: str = 'show') -> Tuple[str, int, int, str]:
    """Create a random question for note guessing.
    
    Returns:
        Tuple containing (fretboard_visual, string_number, fret_number, correct_note)
    """
    # Generate complete fretboard
    fretboard = create_fretboard(max_fret)
    
    # Select random string and fret
    string_num = random.randint(1, 6)
    fret_num = random.randint(0, max_fret)
    
    # Get correct answer
    correct_note = fretboard[string_num][fret_num]
    
    if orientation == 'vertical':
        # Use vertical visualization
        visual = create_vertical_fretboard(
            fretboard,
            max_fret,
            target_string=string_num,
            target_fret=fret_num,
            mode=mode
        )
        return ("\n".join(visual), string_num, fret_num, correct_note)
    else:
        # Create horizontal visualization
        visual = []
        for string in range(1, 7):
            string_notes = fretboard[string].copy()
            target = fret_num if string == string_num else None
            
            if mode == 'hide':
                for i in range(len(string_notes)):
                    if target is None or i != target:
                        string_notes[i] = "---"
                        
            visual.append(visualize_string_horizontal(string, string_notes, target))
        
        # Add fret numbers at the top
        fret_numbers = "        "  # Space for string name and open string
        for fret in range(max_fret + 1):
            fret_numbers += f"{fret}     "  # Adjust spacing for alignment with vertical bars
        
        visual.insert(0, fret_numbers)
        return ("\n".join(visual), string_num, fret_num, correct_note)

def format_note_name(note: str) -> str:
    """Format note name to handle both user inputs and internal representation."""
    note = note.upper().strip()
    # Handle alternative representations
    replacements = {
        'BB': 'A#',
        'DB': 'C#',
        'EB': 'D#',
        'GB': 'F#',
        'AB': 'G#',
        'B#': 'C',
        'E#': 'F'
    }
    return replacements.get(note, note) 