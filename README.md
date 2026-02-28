# Snake Game

带录像与回放功能的 Tkinter 贪吃蛇项目，包含单人模式、本地双人模式，以及对应的回放工具。

## 环境

- Python 3.10 或更高版本
- 标准库 `tkinter`

## 运行方式

- 单人游戏：`python client/snake.py`
- 单人回放：`python client/robot.py`
- 本地双人游戏：`python client/multiplayer.py`
- 本地双人回放：`python client/multiplayer_robot.py`
- 菜单启动器：`python client/gameloader.py`

## 当前功能

### 单人模式

- 使用方向键控制移动。
- 死亡后可输入昵称保存录像。
- 录像保存在 `records/` 目录。

### 单人回放

- 通过昵称筛选本地录像。
- 选择录像后自动回放。

### 本地双人模式

- `P1` 使用 `W/A/S/D` 控制。
- `P2` 使用方向键控制。
- 双方共用同一张地图和食物。
- 游戏不会在第一个玩家死亡时结束，只有双方都死亡才结束。
- 先死亡的一方会从蛇头开始，按蛇身一隔一生成食物。
- 游戏结束后可分别为 `P1` 和 `P2` 命名并保存多人录像。

### 本地双人回放

- 独立脚本实现，不影响单人回放。
- 自动读取 `records/` 下的 `multi_*.log` 文件。
- 支持按玩家名搜索多人录像。
- 可回放双人对局中的双方蛇身、分数、时间和最终结果。

## 录像文件

- 单人录像：保存在 `records/` 目录，文件名形如 `player_2026-02-27_12-00.log`
- 双人录像：保存在 `records/` 目录，文件名形如 `multi_P1_P2_2026-02-27_12-00-00.log`

## 项目文件说明

- `client/snake.py`：单人游戏
- `client/robot.py`：单人回放
- `client/multiplayer.py`：本地双人游戏
- `client/multiplayer_robot.py`：本地双人回放
- `client/gameloader.py`：菜单入口

## English

This is a Tkinter snake game project with recording and replay support.

### Modes

- Single-player game with local recording
- Single-player replay browser
- Local multiplayer game for two players on one keyboard
- Dedicated multiplayer replay browser/player

### Controls

- Single-player: Arrow keys
- Multiplayer `P1`: `W/A/S/D`
- Multiplayer `P2`: Arrow keys

### Multiplayer Rules

- The match ends only after both players die.
- When the first player dies, that snake turns into food starting from the head, using every other segment.
- After the match ends, you can enter separate names for `P1` and `P2` and save the replay.

### Launch

- `python client/snake.py`
- `python client/robot.py`
- `python client/multiplayer.py`
- `python client/multiplayer_robot.py`
- `python client/gameloader.py`
