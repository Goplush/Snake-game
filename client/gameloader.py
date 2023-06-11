import tkinter as tk
from tkinter import messagebox
from snake import SnakeGame

class MainMenu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("游戏主界面")

        # 单人游戏按钮
        self.single_player_button = tk.Button(self.window, text="单人游戏", command=self.start_single_player_game)
        self.single_player_button.pack()

        # 多人游戏按钮
        self.multiplayer_button = tk.Button(self.window, text="多人游戏", command=self.start_multiplayer_game)
        self.multiplayer_button.pack()

    def start_single_player_game(self):
        self.window.withdraw()  # 隐藏主界面
        single_player_game_interface = SinglePlayerGameInterface()
        single_player_game_interface.start()
        self.window.deiconify()  # 恢复主界面显示

    def start_multiplayer_game(self):
        messagebox.showinfo("提示", "多人游戏功能正在开发中")

    def start(self):
        self.window.mainloop()

class SinglePlayerGameInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("单人游戏界面")
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)


        # 长度输入框和标签
        self.width_label = tk.Label(self.window, text="请输入界面的宽度:")
        self.width_label.pack()
        self.width_entry = tk.Entry(self.window)
        self.width_entry.pack()

        # 宽度输入框和标签
        self.height_label = tk.Label(self.window, text="请输入界面的高度:")
        self.height_label.pack()
        self.height_entry = tk.Entry(self.window)
        self.height_entry.pack()

        # 开始游戏按钮
        self.start_game_button = tk.Button(self.window, text="开始游戏", command=self.start_game)
        self.start_game_button.pack()

    def isParaLegal(self):
        width = self.width_entry.get()
        height = self.height_entry.get()
        if not width or not height:
            return False
        try:
            if int(width)<200 or int(height)<200:
                return False
            return True
        except:
            return False
    
    def start_game(self):
        if not self.isParaLegal():
            messagebox.showwarning("警告", "请输入有效的宽度和高度")
            return
        self.window.withdraw()  # 隐藏主界面
        game = SnakeGame(int(self.width_entry.get()),int(self.height_entry.get()))
        game.start()
        self.window.deiconify() #重新显示主界面

    def start(self):
        self.window.mainloop()
    def onClose(self):
        self.window.quit()
        self.window.destroy()
# 创建游戏主界面对象并启动游戏
main = MainMenu()
main.start()
