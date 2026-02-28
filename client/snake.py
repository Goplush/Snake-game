import os
import random
import time
import tkinter as tk


GRID_SIZE = 10
DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 400


class SnakeGame:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.timer_interval = 200
        self.timer = None
        self.frame = 0

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

        self.timer_label = tk.Label(self.window, text="Time: 0 s", font=("Helvetica", 14))
        self.score_label = tk.Label(self.window, text="Score: 0", font=("Helvetica", 14))
        self.timer_label.pack()
        self.score_label.pack()

        self.restart_hint = None
        self.nickname_label = None
        self.nickname_entry = None
        self.confirm_button = None

        self.window.bind_all("<Key>", self.on_key_press)

        self.log_file = None
        self.reset_state()

    def reset_state(self):
        self.cleanup_log()
        os.makedirs("records", exist_ok=True)
        self.log_file = open("records/game_log.log", "w", encoding="utf-8")
        self.log_file.write(f"game_size:w{self.width}h{self.height}\n")

        center_x = (self.width // 2 // GRID_SIZE) * GRID_SIZE
        center_y = (self.height // 2 // GRID_SIZE) * GRID_SIZE
        self.snake = [(center_x, center_y)]
        self.direction = "Right"
        self.frame = 0
        self.game_over_flag = False
        self.start_time = None
        self.score = 0
        self.score_label.config(text="Score: 0")
        self.timer_label.config(text="Time: 0 s")
        self.clear_game_over_widgets()
        self.window.unbind("<space>")

        self.food_position = self.create_food_position()
        self.render()

    def cleanup_log(self):
        if self.log_file and not self.log_file.closed:
            self.log_file.close()

    def clear_game_over_widgets(self):
        widgets = [
            self.restart_hint,
            self.nickname_label,
            self.nickname_entry,
            self.confirm_button,
        ]
        for widget in widgets:
            if widget is not None:
                widget.destroy()
        self.restart_hint = None
        self.nickname_label = None
        self.nickname_entry = None
        self.confirm_button = None

    def random_grid_position(self):
        max_x = max(0, self.width // GRID_SIZE - 1)
        max_y = max(0, self.height // GRID_SIZE - 1)
        x = random.randint(0, max_x) * GRID_SIZE
        y = random.randint(0, max_y) * GRID_SIZE
        return x, y

    def create_food_position(self):
        while True:
            position = self.random_grid_position()
            if position not in self.snake:
                self.log_file.write(
                    f"[Frame: {self.frame}] Food created at position ({position[0]}, {position[1]})\n"
                )
                return position

    def on_key_press(self, event):
        next_direction = event.keysym
        opposites = {
            "Left": "Right",
            "Right": "Left",
            "Up": "Down",
            "Down": "Up",
        }
        if next_direction not in opposites:
            return
        if next_direction == self.direction or opposites[next_direction] == self.direction:
            return

        self.direction = next_direction
        self.log_file.write(f"[Frame: {self.frame}] Direction change: ({next_direction})\n")

    def next_head(self):
        x, y = self.snake[0]
        if self.direction == "Left":
            return x - GRID_SIZE, y
        if self.direction == "Right":
            return x + GRID_SIZE, y
        if self.direction == "Up":
            return x, y - GRID_SIZE
        return x, y + GRID_SIZE

    def move_snake(self):
        if self.game_over_flag:
            return

        next_head = self.next_head()
        ate_food = next_head == self.food_position

        self.snake.insert(0, next_head)
        if ate_food:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.food_position = self.create_food_position()
        else:
            self.snake.pop()

        if self.check_collision():
            self.game_over()
            return

        self.render()

    def check_collision(self):
        x, y = self.snake[0]
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.snake[0] in self.snake[1:]

    def render(self):
        self.canvas.delete("all")
        for segment in self.snake:
            self.canvas.create_rectangle(
                segment[0],
                segment[1],
                segment[0] + GRID_SIZE,
                segment[1] + GRID_SIZE,
                fill="green",
                outline="",
            )

        food_x, food_y = self.food_position
        self.canvas.create_oval(
            food_x,
            food_y,
            food_x + GRID_SIZE,
            food_y + GRID_SIZE,
            fill="red",
            outline="",
        )

    def on_timer(self):
        if self.game_over_flag:
            return

        self.frame += 1
        if self.start_time is None:
            self.start_time = time.time()

        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.move_snake()

        if not self.game_over_flag:
            self.timer = self.window.after(self.timer_interval, self.on_timer)

    def game_over(self):
        if self.game_over_flag:
            return

        self.game_over_flag = True
        elapsed_time = int(time.time() - self.start_time) if self.start_time else 0
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.canvas.create_text(
            self.width / 2,
            self.height / 2,
            text="Game Over",
            font=("Helvetica", 24),
            fill="white",
        )

        self.log_file.write(f"[Frame: {self.frame}] Game Over\n")
        self.log_file.write(f"Survival Time: {elapsed_time} s\n")
        self.log_file.write(f"Score: {self.score}\n")
        self.cleanup_log()

        self.window.bind("<space>", self.restart_game)

        self.restart_hint = tk.Label(
            self.window,
            text="Enter a nickname to save the record, or press Space to restart.",
            font=("Helvetica", 12),
        )
        self.restart_hint.pack()
        self.nickname_label = tk.Label(self.window, text="Nickname:", font=("Helvetica", 12))
        self.nickname_label.pack()
        self.nickname_entry = tk.Entry(self.window)
        self.nickname_entry.pack()
        self.confirm_button = tk.Button(self.window, text="Save Record", command=self.rename_log)
        self.confirm_button.pack()

    def rename_log(self):
        if not os.path.exists("records/game_log.log"):
            return

        nickname = self.nickname_entry.get().strip() if self.nickname_entry else ""
        if not nickname:
            nickname = "player"

        timestamp = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
        new_log_name = os.path.join("records", f"{nickname}_{timestamp}.log")
        os.rename("records/game_log.log", new_log_name)
        self.clear_game_over_widgets()

    def restart_game(self, event=None):
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
    SnakeGame(DEFAULT_WIDTH, DEFAULT_HEIGHT).start()
