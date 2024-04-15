import tkinter as tk
import EarTraining as EarTrainingGame
from EarTraining import EarTrainingGame


def start_game(mode, difficulty, app):
    print(f"Starting game with mode: {mode}, difficulty: {difficulty}")
    # Assuming backend's start_game method expects mode and difficulty as parameters
    backend_response = app.backend.start_game(mode, difficulty)
    app.show_game_interface()

def verify_answers(user_inputs, correct_answers):
    # Returns a list of boolean where True indicates the answer is correct
    return [user_input == correct_answer for user_input, correct_answer in zip(user_inputs, correct_answers)]


class EarTrainerApp(tk.Tk):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend  # Store the backend instance
        self.title("EarTrainer")
        self.geometry("1000x600")
        self.configure(bg='#2b2b2b')
        self.create_widgets()
        
    def create_widgets(self):
        self.main_frame = tk.Frame(self, bg='#2b2b2b')
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.show_main_menu()

    def create_button(self, master, text, command, width=20, height=2, pady=10):
        return tk.Button(master, text=text, command=command, width=width, height=height, fg='black', bg='#3c3f41', activebackground='#4b4b4b', activeforeground='black', font=('Arial', 10, 'bold'), pady=pady)

    def show_main_menu(self):
        self.clear_frame(self.main_frame)
        self.create_button(self.main_frame, "Play", self.show_tonality_screen).pack(pady=20)
        self.create_button(self.main_frame, "Stats", lambda: None).pack(pady=20)
        self.create_button(self.main_frame, "Sandbox", lambda: None).pack(pady=20)

    def show_tonality_screen(self):
        self.clear_frame(self.main_frame)
        tonalities = ["Major", "Minor", "Chromatic", "Modes"]
        for tonality in tonalities:
            self.create_button(self.main_frame, tonality, lambda t=tonality: self.show_modes_screen() if t == "Modes" else self.show_difficulty_screen(t, from_modes=False)).pack(pady=10)
        self.create_button(self.main_frame, "Back", self.show_main_menu).pack(pady=20)

    def show_modes_screen(self):
        self.clear_frame(self.main_frame)
        self.create_button(self.main_frame, "Major Scale Modes", self.show_major_modes_screen).pack(pady=10)
        self.create_button(self.main_frame, "Melodic Minor Scale Modes", self.show_melodic_minor_modes_screen).pack(pady=10)
        self.create_button(self.main_frame, "Back", self.show_tonality_screen).pack(pady=20)

    def show_major_modes_screen(self):
        self.clear_frame(self.main_frame)
        major_modes = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]
        for mode in major_modes:
            self.create_button(self.main_frame, mode, lambda m=mode: self.show_difficulty_screen(m, from_modes=True)).pack(pady=5)
        self.create_button(self.main_frame, "Back", self.show_modes_screen).pack(pady=20)

    def show_melodic_minor_modes_screen(self):
        self.clear_frame(self.main_frame)
        melodic_minor_modes = ["Melodic Minor", "Dorian b2", "Lydian Augmented", "Lydian Dominant", "Mixolydian b6", "Locrian #2", "Altered"]
        for mode in melodic_minor_modes:
            self.create_button(self.main_frame, mode, lambda m=mode: self.show_difficulty_screen(m, from_modes=True)).pack(pady=5)
        self.create_button(self.main_frame, "Back", self.show_modes_screen).pack(pady=20)

    def show_difficulty_screen(self, mode, from_modes):
        self.clear_frame(self.main_frame)
        difficulties = ["Easy", "Medium", "Hard", "Impossible"]
        for difficulty in difficulties:
            self.create_button(self.main_frame, difficulty, lambda d=difficulty: start_game(mode, d, self)).pack(pady=10)
        back_action = self.show_modes_screen if from_modes else self.show_tonality_screen
        self.create_button(self.main_frame, "Back", back_action).pack(pady=20)

    def show_game_interface(self):
        self.clear_frame(self.main_frame)
        self.setup_input_answer_area()
        self.setup_keyboard_layout()

    def setup_input_answer_area(self):
        input_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, pady=(10, 5))

        self.answer_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.answer_frame.pack(fill=tk.X, pady=(5, 20))

        self.inputs = []
        self.answers = []
        answer_labels = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Ti", "Do#", "Re#", "Fa#", "Sol#", "La#"]
        for i in range(12):
            entry = tk.Entry(input_frame, width=5, font=('Arial', 12), justify='center', state='readonly')
            entry.pack(side=tk.LEFT, padx=5)
            self.inputs.append(entry)
            answer = tk.Entry(self.answer_frame, width=5, font=('Arial', 12), justify='center', state='readonly')
            answer.pack(side=tk.LEFT, padx=5)
            self.answers.append(answer)  # Initially empty

        backspace_button = tk.Button(input_frame, text="←", width=10, font=('Arial', 12), command=self.backspace_input)
        backspace_button.pack(side=tk.LEFT, padx=10)

        check_button = tk.Button(input_frame, text="Check", width=10, font=('Arial', 12), command=self.check_answers)
        check_button.pack(side=tk.LEFT, padx=0)
        
    def backspace_input(self):
        for entry in reversed(self.inputs):
            if entry.get():
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.config(state='readonly')
                break

    def check_answers(self):
        user_input_values = [entry.get() for entry in self.inputs]
        user_input_midi = solfege_to_midi(user_input_values)
        # You will need to dynamically determine the correct answers MIDI based on the game's current settings
        correct_answers_midi = backend.generate_test_sequence
        results = verify_answers(user_input_midi, correct_answers_midi)
        for entry, result in zip(self.inputs, results):
            entry.config(bg='light green' if result else 'light coral')

    def setup_keyboard_layout(self):
        keyboard_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        keyboard_frame.pack(side=tk.BOTTOM, fill=tk.X)  # Move to bottom

        # Upper row for sharp notes
        upper_row = tk.Frame(keyboard_frame, bg='#2b2b2b')
        upper_row.pack(fill=tk.X)
        upper_notes = [("Ra", 1), ("Me", 3), ("Fi", 6), ("Le", 8), ("Te", 10)]
        for note, pos in upper_notes:
            tk.Button(upper_row, text=note, width=4, height=2, command=lambda n=note: self.update_input(n)).pack(side=tk.LEFT, padx=(55 if pos == 1 else 45, 5))

        # Lower row for natural notes
        lower_row = tk.Frame(keyboard_frame, bg='#2b2b2b')
        lower_row.pack(fill=tk.X)
        lower_notes = ["Do", "Re", "Mi", "Fa", "Sol", "La", "Ti"]
        for note in lower_notes:
            tk.Button(lower_row, text=note, width=6, height=2, command=lambda n=note: self.update_input(n)).pack(side=tk.LEFT, padx=5)

    def update_input(self, note):
        solfege = {'Do': 'do', 'Ra': 'ra', 'Re': 're', 'Me': 'me', 'Mi': 'mi', 'Fa': 'fa', 'Fi': 'fi', 'Sol': 'sol', 'Le': 'le', 'La': 'la', 'Te': 'te', 'Ti': 'ti'}
        if note in solfege:
            self.backend.add_user_guess(solfege[note])
        # Find the first empty input and fill it with the note
        for entry in self.inputs:
            if not entry.get():
                entry.config(state='normal')
                entry.insert(0, note)
                entry.config(state='readonly')
                break

    def update_input(self, note):
        # Find the first empty input and fill it with the note
        for entry in self.inputs:
            if not entry.get():
                entry.config(state='normal')
                entry.insert(0, note)
                entry.config(state='readonly')
                break

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()
            
def solfege_to_midi(solfege):
    solfege_map = {
        'Do': 60, 'Ra': 61, 'Re': 62, 'Me': 63, 'Mi': 64,
        'Fa': 65, 'Fi': 66, 'Sol': 67, 'Le': 68, 'La': 69,
        'Te': 70, 'Ti': 71
    }
    return [solfege_map[note] for note in solfege if note in solfege_map]

if __name__ == "__main__":
    backend = EarTrainingGame()  # Create an instance of the EarTrainingGame class
    app = EarTrainerApp(backend)  # Pass the backend instance to the frontend class
    app.mainloop()