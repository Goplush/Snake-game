import tkinter as tk
from tkinter import messagebox

from multiplayer import LocalMultiplayerSnakeGame
from snake import SnakeGame


DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 400
MIN_SIZE = 200


class MainMenu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.title_label = tk.Label(self.window, text="Snake Game", font=("Helvetica", 18))
        self.title_label.pack(pady=(10, 5))

        self.width_label = tk.Label(self.window, text="Width:")
        self.width_label.pack()
        self.width_entry = tk.Entry(self.window)
        self.width_entry.insert(0, str(DEFAULT_WIDTH))
        self.width_entry.pack()

        self.height_label = tk.Label(self.window, text="Height:")
        self.height_label.pack()
        self.height_entry = tk.Entry(self.window)
        self.height_entry.insert(0, str(DEFAULT_HEIGHT))
        self.height_entry.pack()

        self.single_player_button = tk.Button(
            self.window,
            text="Single Player",
            command=self.start_single_player_game,
            width=18,
        )
        self.single_player_button.pack(pady=(10, 5))

        self.multiplayer_button = tk.Button(
            self.window,
            text="Local Multiplayer",
            command=self.start_multiplayer_game,
            width=18,
        )
        self.multiplayer_button.pack(pady=(0, 10))

    def parse_size(self):
        width = self.width_entry.get().strip()
        height = self.height_entry.get().strip()
        try:
            width_value = int(width)
            height_value = int(height)
        except ValueError:
            return None

        if width_value < MIN_SIZE or height_value < MIN_SIZE:
            return None
        return width_value, height_value

    def launch_game(self, game_factory):
        size = self.parse_size()
        if size is None:
            messagebox.showwarning(
                "Invalid Size",
                f"Width and height must both be integers >= {MIN_SIZE}.",
            )
            return

        self.window.withdraw()
        game = game_factory(*size)
        game.start()
        self.window.deiconify()

    def start_single_player_game(self):
        self.launch_game(SnakeGame)

    def start_multiplayer_game(self):
        self.launch_game(LocalMultiplayerSnakeGame)

    def start(self):
        self.window.mainloop()

    def on_close(self):
        self.window.quit()
        self.window.destroy()


if __name__ == "__main__":
    MainMenu().start()
