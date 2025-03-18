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

def visualize_string(string_num: int, notes: List[str], target_fret: int = None) -> str:
    """Visualize a single string with optional target fret marked with '?'."""
    # Use lowercase 'e' for the first string
    string_name = 'e' if string_num == 1 else config.STRINGS[string_num]
    # Start with string name and open string note, marked with circle symbol
    result = f"{string_name} | ◯ "
    
    for fret in range(1, len(notes)):
        if fret == target_fret:
            # Add emphasis around the question mark
            result += f"- {config.QUESTION_MARK} "
        else:
            # For hidden notes (shown as "---"), don't add extra space
            if notes[fret] == "---":
                result += f"- {notes[fret]} "
            else:
                # Align other notes, adding extra space for non-sharp notes
                note = notes[fret] + " " if len(notes[fret]) == 1 else notes[fret]
                result += f"- {note} "
    return result

def create_question(max_fret: int, orientation: str = 'vertical', mode: str = 'show') -> Tuple[str, int, int, str]:
    """Create a random question for note guessing.
    Returns: (fretboard_visual, string_number, fret_number, correct_note)
    """
    # Generate complete fretboard
    fretboard = create_fretboard(max_fret)
    
    # Select random string and fret
    string_num = random.randint(1, 6)
    fret_num = random.randint(0, max_fret)
    
    # Get correct answer
    correct_note = fretboard[string_num][fret_num]
    
    # Create visual representation
    visual = []
    for string in range(1, 7):
        string_notes = fretboard[string].copy()  # Make a copy to avoid modifying the original
        target = fret_num if string == string_num else None
        
        # Handle hide mode - replace notes with dashes except for the target
        if mode == 'hide':
            for i in range(len(string_notes)):
                if target is None or i != target:
                    string_notes[i] = "---"
                    
        visual.append(visualize_string(string, string_notes, target))
    
    # Add fret numbers at the top
    fret_numbers = "       "  # Space for string name and open string
    for fret in range(max_fret + 1):
        fret_numbers += f"{fret}   "  # Adjust spacing for alignment
    
    if orientation == 'vertical':
        visual.insert(0, fret_numbers)  # Insert at the top
    else:
        # For horizontal orientation, transpose the fretboard
        visual = transpose_fretboard(visual, fret_numbers)
    
    return ("\n".join(visual), string_num, fret_num, correct_note)

def transpose_fretboard(visual: List[str], fret_numbers: str) -> List[str]:
    """Transpose the fretboard for horizontal orientation."""
    transposed = [fret_numbers]
    for i in range(len(visual[0])):
        transposed.append(''.join([line[i] for line in visual]))
    return transposed

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