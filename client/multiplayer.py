import os
import random
import re
import socket
import tkinter as tk
import time
from tkinter import filedialog
import fnmatch
from tkinter import ttk



class MultiRemote:
    def __init__(self,socket):

        self.actions = {}
        self.food_positions = {}

        self.window = tk.Tk()
        self.window.title("贪吃蛇游戏")

        self.timer_interval = 200
        self.timer = None
        self.frame = 0 #本局游戏目前的所处的帧的计数
        self.log_file = open("records/remote_log.log", "w")

        self.eat_flag = False#标志着该帧蛇是否吃到食物
        start_flag = False#标志着对方是否开始游戏

        #消息列表初始化
        self.food_positions = dict()
        self.actions = dict()

        #连接远程主机
        self.sock = socket
        
        #从远程主机中读取游戏初始化数据，包括最开始的食物位置
        self.recv_game_data()
        

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.snake = [(self.width / 2, self.height / 2)]
        self.direction = "Right"

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
        self.recv_game_data()
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
        self.log_file.close()
        self.game_over_flag = True
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Game Over", font=("Helvetica", 24), fill="red")


    def start(self):
        self.start_time = time.time()
        self.timer = self.window.after(self.timer_interval, self.on_timer)
        self.window.mainloop()
    
    def extract_size(self,string):
        pattern = r'w(\d+)h(\d+)'  # 正则表达式模式
        match = re.search(pattern, string)  # 在字符串中搜索匹配项
        if match:
            width = match.group(1)  # 获取第一个括号中的匹配项
            height = match.group(2)  # 获取第二个括号中的匹配项
            return int(width), int(height)
        else:
            return None
    def recv_game_data(self):
        #从远程主机中读取游戏数据的方法，包括最开始的食物位置
        data = self.sock.recv(1024)
        decoded_data = data.decode()
        lines = decoded_data.splitlines()
        for line in lines:
            self.log_file.write(line)
            if line.startswith('game_size'):
                self.width,self.height = self.extract_size(line.__str__())
            elif line.startswith("[Frame"):
                file_frame = int(line.split(":")[1].split("]")[0])
                if "Direction change" in line:
                    direction = line[line.find('(')+1:line.find(')')]
                    self.actions[file_frame] = direction
                elif "Food created" in line:
                    position = line.split("(")[1].split(")")[0].split(",")
                    x = int(position[0].strip())
                    y = int(position[1].strip())
                    self.food_positions[file_frame] = (x,y)





class MultiLocalHost:
    def __init__(self, width, height,socket):
        self.width = width
        self.height = height
        self.socket = socket
        self.window = tk.Tk()
        self.window.title("贪吃蛇游戏")
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        self.client_socket, self.client_address = server_socket.accept()
        

        self.log_file = open("records/game_log.log", "w")
        self.log_file.write(f"game_size:w{width}h{height}\n")
        self.timer_interval = 200
        self.timer = None
        self.frame = 0 #本局游戏目前的所处的帧的计数

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.snake = [(self.width / 2, self.height / 2)]
        self.direction = "Right"

        self.food = self.create_food()
        self.canvas.bind_all("<Key>", self.on_key_press)

        self.game_over_flag = False
        self.start_time = None
        self.score = 0
        self.score_label = None

        self.timer_label = tk.Label(self.window, text="Time: 0 s", font=("Helvetica", 16))
        self.score_label = tk.Label(self.window, text="Score: 0", font=("Helvetica", 16))
        self.timer_label.pack()
        self.score_label.pack()



    def create_food(self):
        x = random.randint(30, self.width - 30)
        y = random.randint(30, self.height - 30)
        self.log_file.write(f"[Frame: {self. frame}] Food created at position ({x}, {y})\n")
        return self.canvas.create_oval(x, y, x + 10, y + 10, fill="red")

    def on_key_press(self, event):
        key = event.keysym
        if key ==self.direction:
            return
        if key == "Left" and self.direction != "Right":
            self.direction = "Left"
            #log the directon change
            self.log_file.write(f"[Frame: {self. frame}] Direction change: ({key})\n")
        elif key == "Right" and self.direction != "Left":
            self.direction = "Right"
            #log the directon change
            self.log_file.write(f"[Frame: {self. frame}] Direction change: ({key})\n")
        elif key == "Up" and self.direction != "Down":
            self.direction = "Up"
            #log the directon change
            self.log_file.write(f"[Frame: {self. frame}] Direction change: ({key})\n")
        elif key == "Down" and self.direction != "Up":
            self.direction = "Down"
            #log the directon change
            self.log_file.write(f"[Frame: {self. frame}] Direction change: ({key})\n")


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
        if self.canvas.coords(self.food)[0]+5>=x >= self.canvas.coords(self.food)[0]-5 and self.canvas.coords(self.food)[1]+5>=y >= self.canvas.coords(self.food)[1]-5:
            self.canvas.delete(self.food)
            self.food = self.create_food()
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
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
        if not self.start_time:
            self.start_time = time.time()
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")

        self.move_snake()

        if not self.game_over_flag:
            self.timer = self.window.after(self.timer_interval, self.on_timer)
        else:
            self.log_file.close()

    def game_over(self):
        self.game_over_flag = True
        self.window.bind("<space>", self.restart_game)
        elapsed_time = int(time.time() - self.start_time)
        self.timer_label.config(text=f"Time: {elapsed_time} s")
        self.canvas.create_text(self.width / 2, self.height / 2, text="Game Over", font=("Helvetica", 24), fill="red")
        self.log_file.write(f"[Frame: {self. frame}] Game Over\n")
        self.log_file.write(f"Survival Time: {elapsed_time} s\n")
        self.log_file.write(f"Score: {self.score}\n")
        self.log_file.close()
        
        # 创建昵称输入框
        input_remind_label = tk.Label(self.window, text="Please input your nickname to save the game record\nAnd/Or press space to restart", font=("Helvetica", 16))
        nickname_entry = tk.Entry(self.window)
        input_remind_label.pack()
        nickname_entry.pack()

        def rename_log():
            nickname = nickname_entry.get().strip()
            if nickname.__len__()==0:
                nickname = 'player'
            timestamp = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
            new_log_name = f"{nickname}_{timestamp}.log"
            self.log_file.close()
            os.rename("records/game_log.log", 'records/'+new_log_name)
            nickname_entry.destroy()
            confirm_button.destroy()
            input_remind_label.destroy()


        # 创建确认按钮
        confirm_button = tk.Button(self.window, text="确认", command=rename_log)
        confirm_button.pack()

    def restart_game(self, event=None):
        
        self.window.unbind("<space>")
        self.log_file = open("records/game_log.log", "w")
        self.snake = [(self.width / 2, self.height / 2)]
        self.direction = "Right"
        self.food = self.create_food()
        self.game_over_flag = False
        self.start_time = None
        self.score = 0
        self.score_label.config(text="Score: 0")
        self.timer = self.window.after(self.timer_interval, self.on_timer)
        

    def start(self):
        self.start_time = time.time()
        self.timer = self.window.after(self.timer_interval, self.on_timer)
        self.window.mainloop()
    
    #close event hendeler
    def onClose(self):
        self.window.quit()
        self.window.destroy()
    def get_local_ip():
        # 创建一个临时的套接字对象
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            # 连接到一个虚拟的目标地址和端口
            temp_socket.connect(('8.8.8.8', 80))

            # 获取本地套接字的 IP 地址
            local_ip = temp_socket.getsockname()[0]
            return local_ip
        finally:
            # 关闭临时套接字
            temp_socket.close()


