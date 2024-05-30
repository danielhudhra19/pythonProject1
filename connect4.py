
import numpy as np
import tkinter as tk
from tkinter import messagebox

ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2
PLAYER_COLORS = {PLAYER_ONE: "red", PLAYER_TWO: "yellow"}

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

def winning_move(board, piece):
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4")
        self.board = create_board()
        self.turn = PLAYER_ONE
        self.game_over = False
        self.create_menu()
        self.info_label = tk.Label(root, text="Player 1's Turn (Red)", font=('Arial', 14))
        self.info_label.grid(row=0, column=0, columnspan=COLUMN_COUNT)
        self.buttons = []
        for col in range(COLUMN_COUNT):
            button = tk.Button(root, text=str(col), command=lambda col=col: self.handle_move(col),
                               width=4, height=1, bg='lightblue', fg='black', font=('Arial', 14, 'bold'), bd=3)
            button.grid(row=1, column=col, padx=5, pady=5, sticky='nsew')
            self.buttons.append(button)
        self.canvas = tk.Canvas(root, width=COLUMN_COUNT*100, height=ROW_COUNT*100, bg="blue")
        self.canvas.grid(row=2, column=0, columnspan=COLUMN_COUNT)
        self.draw_board()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        game_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Restart Game", command=self.restart_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

    def draw_board(self):
        self.canvas.delete("all")
        for c in range(COLUMN_COUNT):
            for r in range(ROW_COUNT):
                x0 = c * 100
                y0 = (ROW_COUNT - r - 1) * 100
                x1 = x0 + 100
                y1 = y0 + 100
                color = "white"
                if self.board[r][c] == PLAYER_ONE:
                    color = PLAYER_COLORS[PLAYER_ONE]
                elif self.board[r][c] == PLAYER_TWO:
                    color = PLAYER_COLORS[PLAYER_TWO]
                self.canvas.create_oval(x0+10, y0+10, x1-10, y1-10, fill=color, outline=color)

    def handle_move(self, col):
        if self.game_over:
            return
        if is_valid_location(self.board, col):
            row = get_next_open_row(self.board, col)
            drop_piece(self.board, row, col, self.turn)
            self.draw_board()
            if winning_move(self.board, self.turn):
                self.game_over = True
                winner = "Player 1" if self.turn == PLAYER_ONE else "Player 2"
                messagebox.showinfo("Connect 4", f"{winner} wins!")
            self.turn = PLAYER_TWO if self.turn == PLAYER_ONE else PLAYER_ONE
            self.update_info_label()

    def update_info_label(self):
        player = "Player 1" if self.turn == PLAYER_ONE else "Player 2"
        color = "Red" if self.turn == PLAYER_ONE else "Yellow"
        self.info_label.config(text=f"{player}'s Turn ({color})")

    def new_game(self):
        self.board = create_board()
        self.turn = PLAYER_ONE
        self.game_over = False
        self.draw_board()
        self.update_info_label()

    def restart_game(self):
        self.board = create_board()
        self.turn = PLAYER_ONE
        self.game_over = False
        self.draw_board()
        self.update_info_label()

if __name__ == "__main__":
    root = tk.Tk()
    game = Connect4GUI(root)
    root.mainloop()

