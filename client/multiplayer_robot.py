import json
import os
import tkinter as tk
from tkinter import ttk


GRID_SIZE = 10


class MultiplayerReplayPlayer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.meta = {}
        self.frames = []
        self.names = {"player1": "P1", "player2": "P2"}
        self.result = None
        self.frame_index = 0
        self.timer = None

        self.load_log()

        width = self.meta.get("width", 400)
        height = self.meta.get("height", 400)
        self.timer_interval = self.meta.get("timer_interval", 200)

        self.window = tk.Tk()
        self.window.title("Snake Game - Multiplayer Replay")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = tk.Canvas(self.window, width=width, height=height, bg="black")
        self.canvas.pack()

        self.info_label = tk.Label(
            self.window,
            text=f"P1: {self.names['player1']}    P2: {self.names['player2']}",
            font=("Helvetica", 12),
        )
        self.info_label.pack()

        self.timer_label = tk.Label(self.window, text="Time: 0 s", font=("Helvetica", 14))
        self.timer_label.pack()

        self.score_label = tk.Label(self.window, text="P1 Score: 0    P2 Score: 0", font=("Helvetica", 14))
        self.score_label.pack()

        self.status_label = tk.Label(self.window, text=os.path.basename(log_file), font=("Helvetica", 12))
        self.status_label.pack()

    def load_log(self):
        with open(self.log_file, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("MULTI_META "):
                    self.meta = json.loads(line[len("MULTI_META ") :])
                elif line.startswith("MULTI_FRAME "):
                    self.frames.append(json.loads(line[len("MULTI_FRAME ") :]))
                elif line.startswith("MULTI_NAMES "):
                    self.names = json.loads(line[len("MULTI_NAMES ") :])
                elif line.startswith("MULTI_RESULT "):
                    self.result = json.loads(line[len("MULTI_RESULT ") :])

        if not self.frames:
            raise ValueError("Replay file does not contain multiplayer frame data.")

    def render_frame(self, frame):
        self.canvas.delete("all")

        for segment in frame["player1"]["snake"]:
            self.canvas.create_rectangle(
                segment[0],
                segment[1],
                segment[0] + GRID_SIZE,
                segment[1] + GRID_SIZE,
                fill="green",
                outline="",
            )

        for segment in frame["player2"]["snake"]:
            self.canvas.create_rectangle(
                segment[0],
                segment[1],
                segment[0] + GRID_SIZE,
                segment[1] + GRID_SIZE,
                fill="cyan",
                outline="",
            )

        for food_x, food_y in frame["food_positions"]:
            self.canvas.create_oval(
                food_x,
                food_y,
                food_x + GRID_SIZE,
                food_y + GRID_SIZE,
                fill="red",
                outline="",
            )

        self.timer_label.config(text=f"Time: {frame['elapsed_time']} s")
        self.score_label.config(
            text=(
                f"{self.names['player1']} Score: {frame['player1']['score']}    "
                f"{self.names['player2']} Score: {frame['player2']['score']}"
            )
        )

        if self.frame_index == len(self.frames) - 1 and self.result is not None:
            self.canvas.create_text(
                self.meta.get("width", 400) / 2,
                self.meta.get("height", 400) / 2,
                text=self.result["result"],
                font=("Helvetica", 24),
                fill="white",
            )
            self.status_label.config(text=f"Replay Finished - {self.result['result']}")

    def on_timer(self):
        if self.frame_index >= len(self.frames):
            return

        current_frame = self.frames[self.frame_index]
        self.render_frame(current_frame)
        self.frame_index += 1

        if self.frame_index < len(self.frames):
            self.timer = self.window.after(self.timer_interval, self.on_timer)

    def start(self):
        self.on_timer()
        self.window.mainloop()

    def on_close(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
        self.window.quit()
        self.window.destroy()


class MultiplayerReplayBrowser:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Snake Game - Multiplayer Replay Browser")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.path_map = {}

        self.search_label = tk.Label(
            self.window,
            text="Search replays by player name (leave empty to list all):",
            font=("Helvetica", 12),
        )
        self.search_label.pack()

        self.search_entry = tk.Entry(self.window, width=32)
        self.search_entry.pack()

        self.search_button = tk.Button(self.window, text="Search", command=self.refresh_files)
        self.search_button.pack(pady=(5, 10))

        self.file_picker = ttk.Combobox(self.window, state="readonly", width=50)
        self.file_picker.bind("<<ComboboxSelected>>", self.open_selected_replay)
        self.file_picker.pack()

        self.status_label = tk.Label(self.window, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=(10, 0))

        self.refresh_files()

    def list_replays(self):
        if not os.path.isdir("records"):
            return []

        keyword = self.search_entry.get().strip().lower()
        file_paths = []
        for filename in os.listdir("records"):
            if not filename.startswith("multi_") or not filename.endswith(".log"):
                continue
            if keyword and keyword not in filename.lower():
                continue
            file_paths.append(os.path.join("records", filename))

        file_paths.sort(reverse=True)
        return file_paths

    def describe_replay(self, file_path):
        player_one_name = "P1"
        player_two_name = "P2"
        result_text = ""

        with open(file_path, "r", encoding="utf-8") as file:
            for raw_line in file:
                line = raw_line.strip()
                if line.startswith("MULTI_NAMES "):
                    names = json.loads(line[len("MULTI_NAMES ") :])
                    player_one_name = names.get("player1", player_one_name)
                    player_two_name = names.get("player2", player_two_name)
                elif line.startswith("MULTI_RESULT "):
                    result = json.loads(line[len("MULTI_RESULT ") :])
                    result_text = result.get("result", "")

        base_name = os.path.basename(file_path)
        if result_text:
            return f"{player_one_name} vs {player_two_name} | {result_text} | {base_name}"
        return f"{player_one_name} vs {player_two_name} | {base_name}"

    def refresh_files(self):
        self.path_map = {}
        file_paths = self.list_replays()
        descriptions = []

        for file_path in file_paths:
            description = self.describe_replay(file_path)
            descriptions.append(description)
            self.path_map[description] = file_path

        self.file_picker["values"] = descriptions
        if descriptions:
            self.file_picker.current(0)
            self.status_label.config(text=f"Found {len(descriptions)} replay(s). Select one to play.")
        else:
            self.status_label.config(text="No matching multiplayer replays found.")

    def open_selected_replay(self, event=None):
        description = self.file_picker.get()
        file_path = self.path_map.get(description)
        if not file_path:
            return

        self.window.withdraw()
        player = MultiplayerReplayPlayer(file_path)
        player.start()
        self.window.deiconify()

    def start(self):
        self.window.mainloop()

    def on_close(self):
        self.window.quit()
        self.window.destroy()


if __name__ == "__main__":
    MultiplayerReplayBrowser().start()
