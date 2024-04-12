import random
import threading
import time
import mido
from mido import Message

# Dictionary mapping solfege syllables to corresponding MIDI notes in the C major scale.
solfege_to_midi = {
    'do': 60, 'ra': 61, 're': 62, 'me': 63, 'mi': 64,
    'fa': 65, 'fi': 66, 'sol': 67, 'le': 68, 'la': 69,
    'te': 70, 'ti': 71
}

# Dictionary mapping musical keys to their MIDI note adjustments.
key_to_adjustment = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 2, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': -6, 'G': -5, 'G#': -4,
    'Ab': -4, 'A': -3, 'A3': -2, 'Bb': -2, 'B': -1
}

# Preset difficulty settings for the ear training game.
settings_easy = {"number_of_notes": [2], "octave_range": [1], "key": ["C"]}
settings_medium = {"number_of_notes": [3], "octave_range": [1], "key": ["C"]}
settings_hard = {"number_of_notes": [5], "octave_range": [2], "key": ["C"]}
settings_impossible = {"number_of_notes": [16], "octave_range": [3], "key": ["C"]}

# Dictionary of MIDI note sequences for various musical modes based on the C major scale.
modes = {
    "Ionian": [60, 62, 64, 65, 67, 69, 71],  # C D E F G A B
    "Dorian": [60, 62, 63, 65, 67, 69, 70],  # C D Eb F G A Bb
    "Phrygian": [60, 61, 63, 65, 67, 68, 70],  # C Db Eb F G Ab Bb
    "Lydian": [60, 62, 64, 66, 67, 69, 71],  # C D E F# G A B
    "Mixolydian": [60, 62, 64, 65, 67, 69, 70],  # C D E F G A Bb
    "Aeolian": [60, 62, 63, 65, 67, 68, 70],  # C D Eb F G Ab Bb (Natural Minor)
    "Locrian": [60, 61, 63, 65, 66, 68, 70],  # C Db Eb F Gb Ab Bb
    # Additional modes with specific note sequences.
    "Melodic Minor": [60, 62, 63, 65, 67, 69, 71],
    "Dorian b2": [60, 61, 63, 65, 67, 69, 71],
    "Lydian Augmented": [60, 62, 64, 66, 68, 69, 71],
    "Lydian Dominant": [60, 62, 64, 66, 67, 69, 70],
    "Mixolydian b6": [60, 62, 64, 65, 67, 68, 70],
    "Locrian #2": [60, 62, 63, 65, 66, 68, 70],
    "Altered Scale": [60, 61, 63, 64, 66, 68, 70],
    "Chromatic": [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
}

def validate_user_input(pre_octave_key_list, user_input_list):
    """
    Compares user input MIDI notes against a pre-generated sequence to determine accuracy.
    
    Parameters:
    - pre_octave_key_list (list): The original sequence of MIDI notes before any octave or key adjustments.
    - user_input_list (list): The sequence of MIDI notes inputted by the user.
    
    Returns:
    - tuple (int, list): An integer (1 for exact match, 0 otherwise) and a list of individual matches (1 for match, 0 otherwise).
    """
    overall_match = 1 if pre_octave_key_list == user_input_list else 0
    detailed_match = [1 if pre_octave_key_list[i] == user_input_list[i] else 0 for i in range(len(pre_octave_key_list))]
    return overall_match, detailed_match

class EarTrainingGame:
    """
    Manages the state and logic of an ear training game.
    """
    def __init__(self):
        """
        Initializes a new instance of the ear training game.
        """
        self.user_guesses = []  # Stores the user's guesses as a list of solfege syllables.
        self.elapsed_time = 0.0  # Tracks the elapsed time since the game started.
        self.running = False  # Indicates whether the game is currently running.
        self.lock = threading.Lock()  # Thread lock for synchronizing operations.

    def start_game(self):
        """
        Starts the game clock in a new thread.
        """
        self.running = True
        self.thread = threading.Thread(target=self._game_clock)
        self.thread.start()

    def stop_game(self):
        """
        Stops the game clock and waits for the thread to finish.
        """
        self.running = False
        self.thread.join()

    def _game_clock(self):
        """
        Private method that runs in a separate thread to update the game clock.
        """
        try:
            while self.running:
                with self.lock:
                    self.elapsed_time += 1/60  # Increment the clock in seconds.
                time.sleep(1/60)
                self.notify_gui()
        except Exception as e:
            print(f"An error occurred: {e}")

    def notify_gui(self):
        """
        Outputs the current state of the game for the GUI.
        """
        print(f"Elapsed Time: {self.elapsed_time:.2f} seconds, Guesses: {self.user_guesses}")

    def add_user_guess(self, solfege):
        """
        Adds a user guess to the guesses list and updates the GUI.
        
        Parameters:
        - solfege (str): The solfege syllable to add to the guesses list.
        """
        with self.lock:
            self.user_guesses.append(solfege)
        self.notify_gui()

    def remove_user_guess(self):
        """
        Removes the last guess from the guesses list and updates the GUI.
        """
        with self.lock:
            if self.user_guesses:
                self.user_guesses.pop()
        self.notify_gui()

    def generate_test_sequence(self, number_of_notes, solfege_syllables, octave_range, key):
        """
        Generates a random sequence of MIDI notes based on specified musical parameters.
        
        Parameters:
        - number_of_notes (int): The number of notes to include in the sequence.
        - solfege_syllables (str): A space-separated string of solfege syllables to use for the sequence.
        - octave_range (int): The range of octaves over which notes can vary.
        - key (str): The musical key in which to generate the sequence.
        
        Returns:
        - tuple (str, list): A string representing the MIDI note sequence and a list of pre-octave adjustment MIDI notes.
        """
        solfege_list = solfege_syllables.split()  # Convert the string of solfege syllables into a list.
        selected_midi_notes = [solfege_to_midi[syllable] for syllable in solfege_list]  # Convert solfege to MIDI notes.
        midi_sequence = [random.choice(selected_midi_notes)]  # Start the sequence with a random note.
        
        # Generate the rest of the sequence, ensuring no immediate repetitions.
        while len(midi_sequence) < number_of_notes:
            next_note = random.choice([note for note in selected_midi_notes if note != midi_sequence[-1]])
            midi_sequence.append(next_note)

        pre_octave_key_list = midi_sequence.copy()  # Copy the sequence before applying any octave adjustments.
        
        # Apply random octave adjustments within the specified range.
        octave_adjustments = [random.randint(1, octave_range)]
        for _ in range(1, number_of_notes):
            if octave_adjustments[-1] == 1:
                next_octave = 1 if random.random() < 0.75 else random.choice([octave for octave in range(1, octave_range+1) if octave != octave_adjustments[-1]])
            else:
                next_octave = random.choice([octave for octave in range(1, octave_range+1) if octave != octave_adjustments[-1]])
            octave_adjustments.append(next_octave)

        notes_plus_octave = [(note + (octave - 1) * 12) for note, octave in zip(midi_sequence, octave_adjustments)]  # Apply the octave adjustments.
        key_adjustment = key_to_adjustment[key]  # Adjust the notes for the key.
        adjusted_notes = [note + key_adjustment for note in notes_plus_octave]  # Apply the key adjustment.

        midi_test_notes = "_".join(map(str, adjusted_notes))  # Convert the note list to a string for easy handling.
        return midi_test_notes, pre_octave_key_list

    def generate_reference_cadence(self, key):
        """
        Generates a reference cadence based on the specified key.
        
        Parameters:
        - key (str): The musical key for the cadence.
        
        Returns:
        - dict: A dictionary containing the dominant and tonic chords of the key.
        """
        key_note = solfege_to_midi['do'] + key_to_adjustment[key]  # Base note of the key.
        dominant = (key_note - 5, key_note - 1, key_note + 2)  # Dominant chord notes.
        tonic = (key_note, key_note + 4, key_note + 7)  # Tonic chord notes.
        return {'dominant': dominant, 'tonic': tonic}

def get_midi_output():
    """
    Retrieves and opens a MIDI output port for sending MIDI messages.
    
    Returns:
    - mido.ports.BaseOutput: The opened MIDI output port.
    
    Raises:
    - Exception: If no MIDI output devices are found.
    """
    outputs = mido.get_output_names()  # List available MIDI outputs.
    print("Available MIDI Outputs:", outputs)
    if outputs:
        return mido.open_output(outputs[0])  # Open the first available output.
    else:
        raise Exception("No MIDI output devices found. Please connect a device.")

def play_midi_notes(midi_output, notes, duration, chord=False):
    """
    Plays a series of MIDI notes either as individual notes or as a chord.
    
    Parameters:
    - midi_output (mido.ports.BaseOutput): The MIDI output port.
    - notes (list): A list of MIDI note values to play.
    - duration (float): The duration to hold the notes in seconds.
    - chord (bool): If True, play notes as a chord; otherwise, play sequentially.
    """
    if chord:
        for note in notes:
            midi_output.send(Message('note_on', note=note, velocity=64))  # Start all notes at once.
        time.sleep(duration)  # Hold notes for the duration.
        for note in notes:
            midi_output.send(Message('note_off', note=note, velocity=64))  # Turn off all notes.
    else:
        for note in notes:
            midi_output.send(Message('note_on', note=note, velocity=64))  # Start note.
            time.sleep(duration)  # Hold note for the duration.
            midi_output.send(Message('note_off', note=note, velocity=64))  # Turn off note.

def play_sequence(midi_output, reference_chord, test_sequence, chord_duration, space_between, test_note_speed):
    """
    Plays a reference chord followed by a sequence of test notes with specified timings.
    
    Parameters:
    - midi_output (mido.ports.BaseOutput): The MIDI output port.
    - reference_chord (list): The MIDI notes of the reference chord to play first.
    - test_sequence (list): The sequence of MIDI notes to play after the reference chord.
    - chord_duration (float): The duration to hold the reference chord.
    - space_between (float): The time to wait between the reference chord and the test sequence.
    - test_note_speed (float): The duration of each note in the test sequence.
    """
    play_midi_notes(midi_output, reference_chord, chord_duration, chord=True)  # Play the reference chord.
    time.sleep(space_between)  # Wait before starting the test sequence.
    play_midi_notes(midi_output, test_sequence, test_note_speed, chord=False)  # Play the test sequence sequentially.

def main():
    """
    Main function to run the ear training game.
    """
    game = EarTrainingGame()  # Instantiate the game.
    game.start_game()  # Start the game clock.

    number_of_notes = 4
    solfege_syllables = "do re mi fa sol la ti do"
    octave_range = 2
    key = "C"

    midi_output = get_midi_output()  # Set up MIDI output.

    # Generate and print the test MIDI sequence and reference cadence.
    midi_test_notes, pre_octave_key_list = game.generate_test_sequence(number_of_notes, solfege_syllables, octave_range, key)
    test_sequence_midi = [solfege_to_midi[note] for note in midi_test_notes.split('_')]
    print("Generated MIDI Test Notes:", midi_test_notes)
    print("Pre-Octave List:", pre_octave_key_list)

    reference_cadence = game.generate_reference_cadence(key)
    print("Reference Cadence (Dominant - Tonic):", reference_cadence)

    # Play the reference cadence and the test sequence.
    play_midi_notes(midi_output, reference_cadence['dominant'], 2, chord=True)
    time.sleep(1)  # Space between reference cadence and test sequence.
    play_midi_notes(midi_output, test_sequence_midi, 0.5, chord=False)

    # Simulate user input and validate it.
    user_input_list = ['do', 're', 'mi', 'fa']
    user_input_midi = [solfege_to_midi[syllable] for syllable in user_input_list]
    overall_match, detailed_match = validate_user_input(pre_octave_key_list, user_input_midi)
    print("Overall Match:", overall_match)
    print("Detailed Match:", detailed_match)

    # Keep the game running until the user decides to stop.
    try:
        while True:
            user_command = input("Type 'exit' to end the game or 'remove' to remove the last guess: ").strip().lower()
            if user_command == 'exit':
                break
            elif user_command == 'remove':
                game.remove_user_guess()
    finally:
        game.stop_game()  # Ensure the game clock is stopped.
        midi_output.close()  # Close the MIDI output.

if __name__ == "__main__":
    main()
