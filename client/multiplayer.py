import json
import os
import random
import re
import time
import tkinter as tk


GRID_SIZE = 10
DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 400
TEMP_RECORD_PATH = os.path.join("records", "multiplayer_game_log.log")


class LocalMultiplayerSnakeGame:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.window = tk.Tk()
        self.window.title("Snake Game - Local Multiplayer")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.timer_interval = 200
        self.timer = None
        self.start_time = None
        self.game_over_flag = False
        self.frame = 0

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.info_label = tk.Label(
            self.window,
            text="P1: W A S D    P2: Arrow Keys",
            font=("Helvetica", 12),
        )
        self.info_label.pack()
        self.timer_label = tk.Label(self.window, text="Time: 0 s", font=("Helvetica", 14))
        self.timer_label.pack()

        self.score_frame = tk.Frame(self.window)
        self.score_frame.pack()
        self.player_one_label = tk.Label(
            self.score_frame, text="P1 Score: 0", font=("Helvetica", 14), fg="green"
        )
        self.player_one_label.pack(side=tk.LEFT, padx=10)
        self.player_two_label = tk.Label(
            self.score_frame, text="P2 Score: 0", font=("Helvetica", 14), fg="cyan"
        )
        self.player_two_label.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(self.window, text="", font=("Helvetica", 14))
        self.status_label.pack()

        self.save_hint_label = None
        self.p1_name_label = None
        self.p2_name_label = None
        self.p1_name_entry = None
        self.p2_name_entry = None
        self.save_button = None

        self.log_file = None
        self.record_saved = False

        self.window.bind_all("<Key>", self.on_key_press)

        self.reset_state()

    def reset_state(self):
        self.cleanup_log()
        os.makedirs("records", exist_ok=True)
        self.log_file = open(TEMP_RECORD_PATH, "w", encoding="utf-8")
        self.log_file.write(
            "MULTI_META "
            + json.dumps(
                {
                    "width": self.width,
                    "height": self.height,
                    "grid_size": GRID_SIZE,
                    "timer_interval": self.timer_interval,
                }
            )
            + "\n"
        )

        center_y = (self.height // 2 // GRID_SIZE) * GRID_SIZE
        left_start = max(GRID_SIZE * 3, (self.width // 4 // GRID_SIZE) * GRID_SIZE)
        right_start = min(
            self.width - GRID_SIZE * 4,
            (self.width * 3 // 4 // GRID_SIZE) * GRID_SIZE,
        )

        self.snakes = {
            "player1": [(left_start, center_y)],
            "player2": [(right_start, center_y)],
        }
        self.directions = {
            "player1": "Right",
            "player2": "Left",
        }
        self.alive = {
            "player1": True,
            "player2": True,
        }
        self.scores = {
            "player1": 0,
            "player2": 0,
        }
        self.food_positions = []
        first_food = self.create_food_position(self.all_occupied_positions(), [])
        if first_food is not None:
            self.food_positions.append(first_food)

        self.frame = 0
        self.start_time = None
        self.game_over_flag = False
        self.record_saved = False
        self.player_one_label.config(text="P1 Score: 0")
        self.player_two_label.config(text="P2 Score: 0")
        self.timer_label.config(text="Time: 0 s")
        self.status_label.config(text="")
        self.clear_save_widgets()
        self.render()
        self.log_state()

    def cleanup_log(self):
        if self.log_file and not self.log_file.closed:
            self.log_file.close()

    def clear_save_widgets(self):
        widgets = [
            self.save_hint_label,
            self.p1_name_label,
            self.p2_name_label,
            self.p1_name_entry,
            self.p2_name_entry,
            self.save_button,
        ]
        for widget in widgets:
            if widget is not None:
                widget.destroy()

        self.save_hint_label = None
        self.p1_name_label = None
        self.p2_name_label = None
        self.p1_name_entry = None
        self.p2_name_entry = None
        self.save_button = None

    def all_occupied_positions(self):
        occupied = set()
        for player in ("player1", "player2"):
            occupied.update(self.snakes[player])
        return occupied

    def create_food_position(self, occupied_positions, extra_blocked):
        blocked = set(occupied_positions) | set(extra_blocked)
        candidates = []
        for x in range(0, self.width, GRID_SIZE):
            for y in range(0, self.height, GRID_SIZE):
                if (x, y) not in blocked:
                    candidates.append((x, y))
        if not candidates:
            return None
        return random.choice(candidates)

    def on_key_press(self, event):
        if self.game_over_flag and event.keysym == "space":
            self.restart_game()
            return

        key_map = {
            "a": ("player1", "Left"),
            "d": ("player1", "Right"),
            "w": ("player1", "Up"),
            "s": ("player1", "Down"),
            "Left": ("player2", "Left"),
            "Right": ("player2", "Right"),
            "Up": ("player2", "Up"),
            "Down": ("player2", "Down"),
        }
        if event.keysym not in key_map:
            return

        player, next_direction = key_map[event.keysym]
        if not self.alive[player]:
            return

        current_direction = self.directions[player]
        opposites = {
            "Left": "Right",
            "Right": "Left",
            "Up": "Down",
            "Down": "Up",
        }
        if next_direction == current_direction or opposites[next_direction] == current_direction:
            return

        self.directions[player] = next_direction

    def next_head(self, player):
        x, y = self.snakes[player][0]
        direction = self.directions[player]
        if direction == "Left":
            return x - GRID_SIZE, y
        if direction == "Right":
            return x + GRID_SIZE, y
        if direction == "Up":
            return x, y - GRID_SIZE
        return x, y + GRID_SIZE

    def build_candidate_snake(self, player, next_head, ate_food):
        candidate = [next_head] + list(self.snakes[player])
        if not ate_food and candidate:
            candidate.pop()
        return candidate

    def is_out_of_bounds(self, position):
        x, y = position
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def resolve_deaths(self, active_players, next_heads, candidate_snakes, ate_food):
        deaths = set()

        for player in active_players:
            head = next_heads[player]
            if self.is_out_of_bounds(head):
                deaths.add(player)
                continue
            if head in candidate_snakes[player][1:]:
                deaths.add(player)

        if len(active_players) == 2:
            player_one, player_two = active_players
            player_one_head = next_heads[player_one]
            player_two_head = next_heads[player_two]

            if player_one_head == player_two_head:
                deaths.update(active_players)
                return deaths

            if (
                player_one_head == self.snakes[player_two][0]
                and player_two_head == self.snakes[player_one][0]
            ):
                deaths.update(active_players)
                return deaths

            for player, opponent in (
                (player_one, player_two),
                (player_two, player_one),
            ):
                opponent_body = list(self.snakes[opponent])
                if not ate_food[opponent] and opponent_body:
                    opponent_body = opponent_body[:-1]
                if next_heads[player] in opponent_body:
                    deaths.add(player)

        return deaths

    def corpse_to_food(self, corpse_segments, occupied_positions, existing_foods):
        corpse_foods = []
        blocked = set(occupied_positions) | set(existing_foods)
        alternating_segments = list(corpse_segments[::2])
        for segment in alternating_segments:
            if self.is_out_of_bounds(segment):
                continue
            if segment in blocked:
                continue
            corpse_foods.append(segment)
            blocked.add(segment)
        return corpse_foods

    def tick(self):
        if self.game_over_flag:
            return

        active_players = [player for player in ("player1", "player2") if self.alive[player]]
        if not active_players:
            self.finish_game()
            return

        next_heads = {}
        ate_food = {}
        candidate_snakes = {}

        for player in active_players:
            next_head = self.next_head(player)
            next_heads[player] = next_head
            ate_food[player] = next_head in self.food_positions
            candidate_snakes[player] = self.build_candidate_snake(
                player,
                next_head,
                ate_food[player],
            )

        deaths = self.resolve_deaths(active_players, next_heads, candidate_snakes, ate_food)
        survivors = [player for player in active_players if player not in deaths]

        consumed_foods = set()
        for player in survivors:
            self.snakes[player] = candidate_snakes[player]
            if ate_food[player]:
                self.scores[player] += 1
                consumed_foods.add(next_heads[player])

        survivor_positions = set()
        for player in survivors:
            survivor_positions.update(self.snakes[player])

        remaining_foods = [food for food in self.food_positions if food not in consumed_foods]
        for player in deaths:
            corpse_foods = self.corpse_to_food(
                self.snakes[player],
                survivor_positions,
                remaining_foods,
            )
            remaining_foods.extend(corpse_foods)
            self.alive[player] = False
            self.snakes[player] = []

        if survivors and not remaining_foods:
            extra_food = self.create_food_position(survivor_positions, [])
            if extra_food is not None:
                remaining_foods.append(extra_food)

        self.food_positions = remaining_foods
        self.player_one_label.config(text=f"P1 Score: {self.scores['player1']}")
        self.player_two_label.config(text=f"P2 Score: {self.scores['player2']}")

        self.render()
        self.log_state()

        if not any(self.alive.values()):
            self.finish_game()
        elif deaths:
            defeated = []
            if "player1" in deaths:
                defeated.append("P1")
            if "player2" in deaths:
                defeated.append("P2")
            self.status_label.config(text=f"{' & '.join(defeated)} died. Survive until both are down.")

    def winner_text(self):
        if self.scores["player1"] > self.scores["player2"]:
            return "Player 1 Wins"
        if self.scores["player2"] > self.scores["player1"]:
            return "Player 2 Wins"
        return "Draw"

    def finish_game(self):
        if self.game_over_flag:
            return

        self.game_over_flag = True
        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        result_text = self.winner_text()

        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.status_label.config(text=f"{result_text} - press Space to restart")
        self.canvas.create_text(
            self.width / 2,
            self.height / 2,
            text=result_text,
            font=("Helvetica", 24),
            fill="white",
        )

        if self.log_file and not self.log_file.closed:
            self.log_file.write(
                "MULTI_RESULT "
                + json.dumps(
                    {
                        "elapsed_time": elapsed_time,
                        "result": result_text,
                        "scores": self.scores,
                    }
                )
                + "\n"
            )
            self.log_file.flush()

        self.show_save_widgets()

    def show_save_widgets(self):
        self.clear_save_widgets()

        self.save_hint_label = tk.Label(
            self.window,
            text="Set names for P1 and P2, then save the replay.",
            font=("Helvetica", 12),
        )
        self.save_hint_label.pack()

        self.p1_name_label = tk.Label(self.window, text="P1 Name:", font=("Helvetica", 12))
        self.p1_name_label.pack()
        self.p1_name_entry = tk.Entry(self.window)
        self.p1_name_entry.insert(0, "P1")
        self.p1_name_entry.pack()

        self.p2_name_label = tk.Label(self.window, text="P2 Name:", font=("Helvetica", 12))
        self.p2_name_label.pack()
        self.p2_name_entry = tk.Entry(self.window)
        self.p2_name_entry.insert(0, "P2")
        self.p2_name_entry.pack()

        self.save_button = tk.Button(self.window, text="Save Replay", command=self.save_recording)
        self.save_button.pack()

    def sanitize_name(self, value, fallback):
        cleaned = value.strip()
        if not cleaned:
            cleaned = fallback
        cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", cleaned)
        return cleaned or fallback

    def save_recording(self):
        if self.record_saved or self.log_file is None or self.log_file.closed:
            return

        player_one_name = self.sanitize_name(self.p1_name_entry.get(), "P1")
        player_two_name = self.sanitize_name(self.p2_name_entry.get(), "P2")

        self.log_file.write(
            "MULTI_NAMES "
            + json.dumps(
                {
                    "player1": player_one_name,
                    "player2": player_two_name,
                }
            )
            + "\n"
        )
        self.log_file.flush()
        self.cleanup_log()

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        record_path = os.path.join(
            "records",
            f"multi_{player_one_name}_{player_two_name}_{timestamp}.log",
        )
        os.replace(TEMP_RECORD_PATH, record_path)
        self.record_saved = True
        self.status_label.config(text=f"Replay saved: {os.path.basename(record_path)}")
        self.clear_save_widgets()

    def render(self):
        self.canvas.delete("all")

        for segment in self.snakes["player1"]:
            self.canvas.create_rectangle(
                segment[0],
                segment[1],
                segment[0] + GRID_SIZE,
                segment[1] + GRID_SIZE,
                fill="green",
                outline="",
            )

        for segment in self.snakes["player2"]:
            self.canvas.create_rectangle(
                segment[0],
                segment[1],
                segment[0] + GRID_SIZE,
                segment[1] + GRID_SIZE,
                fill="cyan",
                outline="",
            )

        for food_x, food_y in self.food_positions:
            self.canvas.create_oval(
                food_x,
                food_y,
                food_x + GRID_SIZE,
                food_y + GRID_SIZE,
                fill="red",
                outline="",
            )

    def log_state(self):
        if self.log_file is None or self.log_file.closed:
            return

        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        snapshot = {
            "frame": self.frame,
            "elapsed_time": elapsed_time,
            "food_positions": self.food_positions,
            "player1": {
                "alive": self.alive["player1"],
                "direction": self.directions["player1"],
                "score": self.scores["player1"],
                "snake": self.snakes["player1"],
            },
            "player2": {
                "alive": self.alive["player2"],
                "direction": self.directions["player2"],
                "score": self.scores["player2"],
                "snake": self.snakes["player2"],
            },
        }
        self.log_file.write("MULTI_FRAME " + json.dumps(snapshot) + "\n")
        self.log_file.flush()

    def on_timer(self):
        if self.game_over_flag:
            return

        if self.start_time is None:
            self.start_time = time.time()

        self.frame += 1
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.tick()

        if not self.game_over_flag:
            self.timer = self.window.after(self.timer_interval, self.on_timer)

    def restart_game(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
            self.timer = None
        self.reset_state()
        self.start_time = time.time()
        self.timer = self.window.after(self.timer_interval, self.on_timer)

    def start(self):
        self.start_time = time.time()
        self.timer = self.window.after(self.timer_interval, self.on_timer)
        self.window.mainloop()

    def on_close(self):
        if self.timer is not None:
            self.window.after_cancel(self.timer)
        self.cleanup_log()
        self.window.quit()
        self.window.destroy()


if __name__ == "__main__":
    LocalMultiplayerSnakeGame(DEFAULT_WIDTH, DEFAULT_HEIGHT).start()
