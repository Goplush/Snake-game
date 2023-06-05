# Snake-game

带回放功能的贪吃蛇游戏

目前的python文件均可直接运行（python版本 3.10）

打包命令：

- snake.py:  `pyinstaller -Dw -i snake.png --distpath out/snake snake.py`
- robot.py: `pyinstaller -Fw -i replay.png -n replay.exe --distpath out/snake robot.py`

功能：

- snake：进行游戏，死亡后输入昵称，点击确认保存录像，默认昵称为`player`
- robot：录像回放，通过昵称查找录像，列出本机该昵称的所有录像，之后的后缀为时间，点击选择后自动播放

snake game with replay function

All current python files can run directly (Python version 3.10)

The command to packaging it into executable file:

- snake.py:  `pyinstaller -Dw -i snake.png --distpath out/snake snake.py`
- robot.py: `pyinstaller -Fw -i replay.png -n replay.exe --distpath out/snake robot.py`

Features:

- Snake: Play the game. After dying, enter a nickname and click confirm to save the recording. The default nickname is "player."
- Robot: Playback recordings. Search for recordings by nickname and display all recordings on the local machine associated with that nickname. The suffix of each recording is the time it was saved. Click on a recording to automatically start playing it.