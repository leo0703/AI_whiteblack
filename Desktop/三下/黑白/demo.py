import tkinter as tk
import random
import time
import tkinter.messagebox as messagebox

class Reversi(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("黑白棋")
        self.geometry("400x510")

        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        self.board[3][3] = 'B'
        self.board[4][4] = 'B'
        self.board[3][4] = 'W'
        self.board[4][3] = 'W'

        self.canvas = tk.Canvas(self, width=400, height=400, bg="gray")
        self.canvas.pack()

        self.draw_board()
        self.draw_discs()

        self.pass_button = tk.Button(self, text="Pass", command=self.pass_move)
        self.pass_button.pack()

        self.canvas.bind("<Button-1>", self.click)

        self.player_turn = True
        self.game_over = False

        self.play_as = None
        self.player_color = None
        self.computer_color = None
        self.total_time = 0.0  # 修改為浮點數型態
        self.move_start_time = 0
        self.move_end_time = 0

        self.start_game()

    def draw_board(self):
        for i in range(8):
            for j in range(8):
                x1, y1 = i * 50, j * 50
                x2, y2 = x1 + 50, y1 + 50
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="gray")

    def draw_discs(self):
        self.canvas.delete("disc")
        for i in range(8):
            for j in range(8):
                if self.board[i][j] != ' ':
                    x, y = i * 50 + 25, j * 50 + 25
                    color = "black" if self.board[i][j] == 'B' else "white"
                    self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, tags="disc")

    def click(self, event):
        if self.player_turn and not self.game_over:
            x, y = event.x // 50, event.y // 50
            if self.board[x][y] == ' ' and self.is_valid_move(x, y, self.player_color):
                self.move_start_time = time.time()
                self.make_move(x, y, self.player_color)
                self.player_turn = False
                self.after(1000, self.computer_move)

    def pass_move(self):
        if self.player_turn and not self.game_over:
            if not self.get_valid_moves(self.player_color):
                print("玩家 pass，輪到電腦下棋")
                self.player_turn = False
                self.pass_button.config(state=tk.DISABLED)  # 禁用 Pass 按鈕
                self.after(1000, self.computer_move())
            else:
                print("仍有可下棋的位置")
        else:
            print("現在不是玩家的回合")

    def is_valid_move(self, x, y, color):
        if self.board[x][y] != ' ':
            return False

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]

        opponent_color = 'W' if color == 'B' else 'B'

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent_color:
                while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent_color:
                    nx, ny = nx + dx, ny + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == color:
                    return True

        return False

    def make_move(self, x, y, color):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]

        opponent_color = 'W' if color == 'B' else 'B'

        self.board[x][y] = color

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent_color:
                temp = []
                while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent_color:
                    temp.append((nx, ny))
                    nx, ny = nx + dx, ny + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == color:
                    for tx, ty in temp:
                        self.board[tx][ty] = color

        self.draw_discs()

        if not any(' ' in row for row in self.board):
            self.game_over = True
            self.display_winner()

        self.move_end_time = time.time()
        move_time = round(self.move_end_time - self.move_start_time, 5)
        print(f"執行時間 : {move_time} 秒, 位置: ({x},{y})")
        self.total_time += move_time
        print(f"電腦總執行時間：{round(self.total_time, 2)} 秒")

    def get_valid_moves(self, color):
        valid_moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j, color):
                    valid_moves.append((i, j))
        return valid_moves

    def computer_move(self):
        if not self.player_turn and not self.game_over:
            x, y = self.find_worst_move(self.computer_color)
            self.make_move(x, y, self.computer_color)
            self.player_turn = True
            self.pass_button.config(state=tk.NORMAL)  # 啟用 Pass 按鈕

    def find_worst_move(self, color):
        def negamax(board, depth, alpha, beta, color):
            if depth == 0 or self.game_over:
                return self.evaluate_board(board, color)

            valid_moves = self.get_valid_moves(color)
            min_eval = float('inf')

            for move in valid_moves:
                new_board = [row[:] for row in board]
                x, y = move
                self.make_move_in_temp_board(new_board, x, y, color)
                eval = -negamax(new_board, depth - 1, -beta, -alpha, self.opponent_color(color))
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if alpha >= beta:
                    break

            return min_eval

        best_move = None
        best_eval = float('inf')
        depth = 7  # 設定搜索深度，可以根據需要調整

        for move in self.get_valid_moves(color):
            new_board = [row[:] for row in self.board]
            x, y = move
            self.make_move_in_temp_board(new_board, x, y, color)
            eval = -negamax(new_board, depth - 1, float('-inf'), float('inf'), self.opponent_color(color))
            if eval < best_eval:
                best_eval = eval
                best_move = move

        return best_move

    def opponent_color(self, color):
        return 'B' if color == 'W' else 'W'

    def make_move_in_temp_board(self, board, x, y, color):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1),
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]

        opponent_color = 'W' if color == 'B' else 'B'
        board[x][y] = color

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == opponent_color:
                temp = []
                while 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == opponent_color:
                    temp.append((nx, ny))
                    nx, ny = nx + dx, ny + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == color:
                    for tx, ty in temp:
                        board[tx][ty] = color

    def evaluate_board(self, board, color):
        # 返回剩餘棋子較少的一方的棋子數量減去另一方的棋子數量
        black_count = sum(row.count('B') for row in board)
        white_count = sum(row.count('W') for row in board)
        if color == 'B':
            return black_count - white_count
        else:
            return white_count - black_count


    def display_winner(self):
        black_count = sum(row.count('B') for row in self.board)
        white_count = sum(row.count('W') for row in self.board)

        winner = "白棋" if black_count > white_count else "黑棋" if black_count < white_count else "平局"
        result = f"黑棋: {black_count}, 白棋: {white_count}. {winner} 勝利！"
        print(result)

    def start_game(self):
        def on_select(option):
            self.play_as = option
            self.player_color = 'B' if self.play_as == '1' else 'W'
            self.computer_color = 'W' if self.play_as == '1' else 'B'
            self.player_turn = self.play_as == '1'
            if not self.player_turn:
                self.move_start_time = time.time()
                self.after(1000, self.computer_move)
            self.selection_frame.destroy()

        self.selection_frame = tk.Frame(self)
        self.selection_frame.pack()
        tk.Label(self.selection_frame, text="選擇先後手：").pack()
        tk.Button(self.selection_frame, text="先手", command=lambda: on_select('1')).pack()
        tk.Button(self.selection_frame, text="後手", command=lambda: on_select('2')).pack()

if __name__ == "__main__":
    game = Reversi()
    game.mainloop()