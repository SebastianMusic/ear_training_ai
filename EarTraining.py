import random
import threading
import time

# Mapping solfege syllables to corresponding MIDI notes in C major scale
solfege_to_midi = {
    'do': 60, 'ra': 61, 're': 62, 'me': 63, 'mi': 64,
    'fa': 65, 'fi': 66, 'sol': 67, 'le': 68, 'la': 69,
    'te': 70, 'ti': 71
}

# Mapping musical keys to their MIDI note adjustments
key_to_adjustment = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 2, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': -6, 'G': -5, 'G#': -4,
    'Ab': -4, 'A': -3, 'A#': -2, 'Bb': -2, 'B': -1
}

# Difficulty settings for various levels
settings_easy = {
    "number_of_notes": [2],
    "octave_range": [1],
    "key": ["C"]
}

settings_medium = {
    "number_of_notes": [3],
    "octave_range": [1],
    "key": ["C"]
}

settings_hard = {
    "number_of_notes": [5],
    "octave_range": [2],
    "key": ["C"]
}

settings_impossible = {
    "number_of_notes": [16],
    "octave_range": [3],
    "key": ["C"]
}

# MIDI note sequences for various musical modes based on the C major scale
modes = {
    "Ionian": [60, 62, 64, 65, 67, 69, 71],  # C D E F G A B
    "Dorian": [60, 62, 63, 65, 67, 69, 70],  # C D Eb F G A Bb
    "Phrygian": [60, 61, 63, 65, 67, 68, 70],  # C Db Eb F G Ab Bb
    "Lydian": [60, 62, 64, 66, 67, 69, 71],  # C D E F# G A B
    "Mixolydian": [60, 62, 64, 65, 67, 69, 70],  # C D E F G A Bb
    "Aeolian": [60, 62, 63, 65, 67, 68, 70],  # C D Eb F G Ab Bb (Natural Minor)
    "Locrian": [60, 61, 63, 65, 66, 68, 70],  # C Db Eb F Gb Ab Bb
    # More modes defined similarly...
    "Melodic Minor": [60, 62, 63, 65, 67, 69, 71],
    "Dorian b2": [60, 61, 63, 65, 67, 69, 71],
    "Lydian Augmented": [60, 62, 64, 66, 68, 69, 71],
    "Lydian Dominant": [60, 62, 64, 66, 67, 69, 70],
    "Mixolydian b6": [60, 62, 64, 65, 67, 68, 70],
    "Locrian #2": [60, 62, 63, 65, 66, 68, 70],
    "Altered Scale": [60, 61, 63, 64, 66, 68, 70],
    "Chromatic": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
}

# Function to validate user input against a pre-generated MIDI sequence
def validate_user_input(pre_octave_key_list, user_input_list):
    # Check if the entire user input list matches the pre-generated list
    overall_match = 1 if pre_octave_key_list == user_input_list else 0
    
    # Check for individual note matches
    detailed_match = [1 if pre_octave_key_list[i] == user_input_list[i] else 0 for i in range(len(pre_octave_key_list))]
    
    return overall_match, detailed_match

# Class that manages the ear training game
class EarTrainingGame:
    def __init__(self):
        self.user_guesses = []  # List to store user guesses
        self.elapsed_time = 0.0  # Track elapsed time since the game started
        self.running = False  # Game state indicator
        self.lock = threading.Lock()  # Lock for thread-safe operations

    def start_game(self, mode, difficulty):
        """Start the game clock in a separate thread."""
        self.running = True
        self.thread = threading.Thread(target=self._game_clock)  # Removed daemon=True
        self.thread.start()


    def stop_game(self):
        """Stop the game clock."""
        self.running = False
        self.thread.join()  # Wait for the game clock thread to finish

    def _game_clock(self):
        """Private method to update the game clock."""
        try:
            while self.running:
                with self.lock:
                    self.elapsed_time += 1/60  # Increment time in seconds
                time.sleep(1/60)  # Update at a rate of 60 times per second
                self.notify_gui()  # Call GUI update method
        except Exception as e:
            print(f"An error occurred: {e}")

    def notify_gui(self):
        """Notify GUI with the current game state."""
        print(f"Elapsed Time: {self.elapsed_time:.2f} seconds, Guesses: {self.user_guesses}")


    def add_user_guess(self, solfege):
        """Add a solfege syllable to the user guesses list."""
        with self.lock:
            self.user_guesses.append(solfege)
        self.notify_gui()  # Update GUI after adding a guess

    def remove_user_guess(self):
        """Remove the last solfege syllable from the user guesses list."""
        with self.lock:
            if self.user_guesses:
                self.user_guesses.pop()
        self.notify_gui()  # Update GUI after removing a guess

    def notify_gui(self):
        """Notify GUI with the current game state."""
        print(f"Elapsed Time: {self.elapsed_time:.2f} seconds, Guesses: {self.user_guesses}")

    def generate_test_sequence(self, number_of_notes, solfege_syllables, octave_range, key):
        """Generate a sequence of MIDI notes based on given parameters."""
        solfege_list = solfege_syllables.split()  # Split solfege syllables into a list
        selected_midi_notes = [solfege_to_midi[syllable] for syllable in solfege_list]  # Convert solfege to MIDI notes
        midi_sequence = [random.choice(selected_midi_notes)]  # Start sequence with a random note

        # Generate remaining notes ensuring no immediate repetitions
        while len(midi_sequence) < number_of_notes:
            next_note = random.choice([note for note in selected_midi_notes if note != midi_sequence[-1]])
            midi_sequence.append(next_note)

        pre_octave_key_list = midi_sequence.copy()  # Copy sequence before applying octave adjustments

        # Apply random octave adjustments
        octave_adjustments = [random.randint(1, octave_range)]
        for _ in range(1, number_of_notes):
            if octave_adjustments[-1] == 1:
                next_octave = 1 if random.random() < 0.75 else random.choice([octave for octave in range(1, octave_range+1) if octave != octave_adjustments[-1]])
            else:
                next_octave = random.choice([octave for octave in range(1, octave_range+1) if octave != octave_adjustments[-1]])
            octave_adjustments.append(next_octave)

        notes_plus_octave = [(note + (octave - 1) * 12) for note, octave in zip(midi_sequence, octave_adjustments)]  # Apply octave adjustments
        key_adjustment = key_to_adjustment[key]  # Get key adjustment
        adjusted_notes = [note + key_adjustment for note in notes_plus_octave]  # Apply key adjustment

        midi_test_notes = "_".join(map(str, adjusted_notes))  # Convert note list to a string
        return midi_test_notes, pre_octave_key_list

    def generate_reference_cadence(self, key):
        """Generate a reference cadence based on a given key."""
        key_note = solfege_to_midi['do'] + key_to_adjustment[key]  # Calculate the base note of the key
        dominant = (key_note - 5, key_note - 1, key_note + 2)  # Calculate dominant chord notes
        tonic = (key_note, key_note + 4, key_note + 7)  # Calculate tonic chord notes
        return {'dominant': dominant, 'tonic': tonic}  # Return both chords as a dictionary


def main():
    game = EarTrainingGame()  # Create an instance of the game
    game.start_game()  # Start the game clock
    number_of_notes = 4
    solfege_syllables = "do re mi fa sol la ti do"
    octave_range = 2
    key = "C"

    # Generate and print test MIDI sequence
    midi_test_notes, pre_octave_key_list = game.generate_test_sequence(number_of_notes, solfege_syllables, octave_range, key)
    print("Generated MIDI Test Notes:", midi_test_notes)
    print("Pre-Octave List:", pre_octave_key_list)

    # Generate and print reference cadence
    reference_cadence = game.generate_reference_cadence(key)
    print("Reference Cadence (Dominant - Tonic):", reference_cadence)
    
    # Simulate user input and validate
    user_input_list = ['do', 're', 'mi', 'fa']
    user_input_midi = [solfege_to_midi[syllable] for syllable in user_input_list]
    overall_match, detailed_match = validate_user_input(pre_octave_key_list, user_input_midi)
    print("Overall Match:", overall_match)
    print("Detailed Match:", detailed_match)

    # Keep the game running until the user decides to stop
    try:
        while True:  # Infinite loop to keep checking for user input
            user_command = input("Type 'exit' to end the game or 'remove' to remove the last guess: ").strip().lower()
            if user_command == 'exit':
                break
            elif user_command == 'remove':
                game.remove_user_guess()
    finally:
        game.stop_game()  # Stop the game clock

if __name__ == "__main__":
    main()