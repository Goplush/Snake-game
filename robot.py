import os
import tkinter as tk
import time
from tkinter import filedialog
import fnmatch
from tkinter import ttk



class ReplayRobot:
    def __init__(self, width, height,log_file):
        self.width = width
        self.height = height

        self.actions = {}
        self.food_positions = {}

        self.window = tk.Tk()
        self.window.title("贪吃蛇游戏")

        self.timer_interval = 200
        self.timer = None
        self.frame = 0 #本局游戏目前的所处的帧的计数

        self.eat_flag = False#标志着该帧蛇是否吃到食物

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.snake = [(self.width / 2, self.height / 2)]
        self.direction = "Right"

        #read log file
        with open(log_file, "r") as file:
            for line in file:
                if line.startswith("[Frame"):
                    file_frame = int(line.split(":")[1].split("]")[0])
                    if "Direction change" in line:
                        direction = line[line.find('(')+1:line.find(')')]
                        self.actions[file_frame] = direction
                    elif "Food created" in line:
                        position = line.split("(")[1].split(")")[0].split(",")
                        x = int(position[0].strip())
                        y = int(position[1].strip())
                        self.food_positions[file_frame] = (x,y)

        (food_first_x,food_first_y) = self.food_positions[0]
        self.food = self.canvas.create_oval(food_first_x, food_first_y, food_first_x+10, food_first_y+10, fill="red")

        self.game_over_flag = False
        self.start_time = None
        self.score = 0
        self.score_label = None

        self.timer_label = tk.Label(self.window, text="Time: 0 s", font=("Helvetica", 16))
        self.score_label = tk.Label(self.window, text="Score: 0", font=("Helvetica", 16))
        self.timer_label.pack()
        self.score_label.pack()


    def move_snake(self):
        if self.game_over_flag:
            return
        
        x, y = self.snake[0]
        if self.direction == "Left":
            x -= 10
        elif self.direction == "Right":
            x += 10
        elif self.direction == "Up":
            y -= 10
        elif self.direction == "Down":
            y += 10

        self.snake.insert(0, (x, y))
        if self.eat_flag:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.eat_flag = False
        else:
            self.snake.pop()

        x1, y1, x2, y2 = self.canvas.coords(self.food)
        self.canvas.delete("all")
        for segment in self.snake:
            self.canvas.create_rectangle(segment[0], segment[1], segment[0] + 10, segment[1] + 10, fill="green")
        self.food = self.canvas.create_oval(x1, y1, x2, y2, fill="red")

        if self.check_collision():
            self.game_over()

    def check_collision(self):
        x, y = self.snake[0]
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        for segment in self.snake[1:]:
            if x == segment[0] and y == segment[1]:
                return True
        return False

    def on_timer(self):
        self.frame = self.frame+1
        try:
            direct = self.actions[self.frame]
            self.direction = direct
        except Exception as e:
            print(f"no direction change in frame {self.frame}")
        try:
            (x,y) = self.food_positions[self.frame]
            self.eat_flag = True
            self.food = self.canvas.create_oval(x, y, x+10, y+10, fill="red")
        except:
            print(f"no food eating in frame {self.frame}")
        
        if not self.start_time:
            self.start_time = time.time()
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")

        self.move_snake()

        if not self.game_over_flag:
            self.timer = self.window.after(self.timer_interval, self.on_timer)
        else:
            print(0)

    def game_over(self):
        self.game_over_flag = True
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Game Over", font=("Helvetica", 24), fill="red")


    def start(self):
        self.start_time = time.time()
        self.timer = self.window.after(self.timer_interval, self.on_timer)
        self.window.mainloop()


class GuidedInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("引导界面")

        # 昵称输入框
        self.nickname_label = tk.Label(self.window, text="请输入昵称:")
        self.nickname_label.pack()
        self.nickname_entry = tk.Entry(self.window)
        self.nickname_entry.pack()
        self.nickname = '0'
        self.file_list = []
        self.selected_file_path = None

        # 创建昵称输入确认按钮
        confirm_button = tk.Button(self.window, text="确认", command= self.confirm_nickname)
        confirm_button.pack()

    def confirm_nickname (self):
            self.nickname = self.nickname_entry.get()
            self.file_list = self.find_files(self.nickname)
            self.list_show()


    

    def find_files(self,pattern):
        matches = []
        for root, dirnames, filenames in os.walk('./records'):  # 当前目录及其子目录遍历
            for filename in fnmatch.filter(filenames, '*' + pattern + '*'):  # 使用通配符匹配文件名
                matches.append(os.path.join(root, filename))  # 将匹配到的文件路径添加到列表中
        return matches


    def list_show(self):
        # 创建下拉列表
        self.dropdown = ttk.Combobox(self.window, values=self.file_list)
        self.dropdown.bind("<<ComboboxSelected>>", self.on_file_selected)  # 绑定选项选中事件
        self.dropdown.pack(pady=10)

    def on_file_selected(self,file):
        self.selected_file_path = self.dropdown.get()
        if self.selected_file_path and os.path.isfile(self.selected_file_path):
            replay = ReplayRobot(400,400,self.selected_file_path)
            replay.start()
        else:
            remind_label = tk.Label(self.window, text="No record found, please try again", font=("Helvetica", 16))
            self.dropdown.destroy()
    

    def start(self):
        self.window.mainloop()




guided_interface = GuidedInterface()
guided_interface.start()

