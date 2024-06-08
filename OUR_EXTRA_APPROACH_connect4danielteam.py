import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog
import pickle
import math

EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2
PLAYER_COLORS = {PLAYER_ONE: "red", PLAYER_TWO: "yellow"}
WINDOW_LENGTH = 4
AI_DEPTH = 4      # We are adjusting this for difficulty level


class Connect4Board:
    def __init__(self, rows=6, columns=7):
        self.rows = rows
        self.columns = columns
        self.board = self.create_board()

    def create_board(self):
        return np.zeros((self.rows, self.columns), dtype=int)

    def drop_piece(self, row, col, piece):
        self.board[row][col] = piece

    def is_valid_location(self, col):
        return self.board[self.rows - 1][col] == EMPTY

    def get_next_open_row(self, col):
        for r in range(self.rows):
            if self.board[r][col] == EMPTY:
                return r

    def winning_move(self, piece):
        # We are checking horizontal locations
        for c in range(self.columns - 3):
            for r in range(self.rows):
                if self.board[r][c] == piece and self.board[r][c + 1] == piece and self.board[r][c + 2] == piece and \
                        self.board[r][c + 3] == piece:
                    return True

        # '--' vertical locations
        for c in range(self.columns):
            for r in range(self.rows - 3):
                if self.board[r][c] == piece and self.board[r + 1][c] == piece and self.board[r + 2][c] == piece and \
                        self.board[r + 3][c] == piece:
                    return True

        # '---' positively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(self.rows - 3):
                if self.board[r][c] == piece and self.board[r + 1][c + 1] == piece and self.board[r + 2][
                    c + 2] == piece and self.board[r + 3][c + 3] == piece:
                    return True

        # '---' negatively sloped diagonals
        for c in range(self.columns - 3):
            for r in range(3, self.rows):
                if self.board[r][c] == piece and self.board[r - 1][c + 1] == piece and self.board[r - 2][
                    c + 2] == piece and self.board[r - 3][c + 3] == piece:
                    return True

        return False

    def get_valid_locations(self):
        valid_locations = []
        for col in range(self.columns):
            if self.is_valid_location(col):
                valid_locations.append(col)
        return valid_locations

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = PLAYER_ONE if piece == PLAYER_TWO else PLAYER_TWO

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
            score -= 4

        return score

    def score_position(self, piece):
        score = 0

        # Centering column score...
        center_array = [int(i) for i in list(self.board[:, self.columns // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Horizontal score:
        for r in range(self.rows):
            row_array = [int(i) for i in list(self.board[r, :])]
            for c in range(self.columns - 3):
                window = row_array[c:c + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Vertical score:
        for c in range(self.columns):
            col_array = [int(i) for i in list(self.board[:, c])]
            for r in range(self.rows - 3):
                window = col_array[r:r + WINDOW_LENGTH]
                score += self.evaluate_window(window, piece)

        # Positive sloped diagonal:
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                window = [self.board[r + i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        # Negative sloped diagonal:
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                window = [self.board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self):
        return self.winning_move(PLAYER_ONE) or self.winning_move(PLAYER_TWO) or len(self.get_valid_locations()) == 0

    def minimax(self, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations()
        is_terminal = self.is_terminal_node()
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.winning_move(PLAYER_TWO):
                    return (None, 100000000000000)
                elif self.winning_move(PLAYER_ONE):
                    return (None, -10000000000000)
                else:  # Else ==> game is over (so no more valid moves)
                    return (None, 0)
            else:  # Depth = zero
                return (None, self.score_position(PLAYER_TWO))
        if maximizingPlayer:
            value = -math.inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(col)
                b_copy = self.board.copy()
                self.drop_piece(row, col, PLAYER_TWO)
                new_score = self.minimax(depth - 1, alpha, beta, False)[1]
                self.board = b_copy
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else:  # Minimizing player
            value = math.inf
            column = np.random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(col)
                b_copy = self.board.copy()
                self.drop_piece(row, col, PLAYER_ONE)
                new_score = self.minimax(depth - 1, alpha, beta, True)[1]
                self.board = b_copy
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value


class Connect4Game:
    def __init__(self, rows=6, columns=7, ai_enabled=False):
        self.board = Connect4Board(rows, columns)
        self.turn = PLAYER_ONE
        self.game_over = False
        self.history = []
        self.ai_enabled = ai_enabled

    def make_move(self, col):
        if not self.game_over and self.board.is_valid_location(col):
            row = self.board.get_next_open_row(col)
            self.board.drop_piece(row, col, self.turn)
            self.history.append((row, col))
            if self.board.winning_move(self.turn):
                self.game_over = True
                return f"Player {self.turn} wins!"
            self.turn = PLAYER_TWO if self.turn == PLAYER_ONE else PLAYER_ONE
            return None
        return "Invalid move"

    def ai_move(self):
        if not self.game_over:
            col, minimax_score = self.board.minimax(AI_DEPTH, -math.inf, math.inf, True)
            self.make_move(col)

    def undo_move(self):
        if self.history:
            row, col = self.history.pop()
            self.board.board[row][col] = EMPTY
            self.turn = PLAYER_TWO if self.turn == PLAYER_ONE else PLAYER_ONE
            self.game_over = False
            return True
        return False

    def save_game(self, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_game(file_path):
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def reset_game(self):
        self.board = Connect4Board(self.board.rows, self.board.columns)
        self.turn = PLAYER_ONE
        self.game_over = False
        self.history = []


class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4")
        self.rows = 6
        self.columns = 7
        self.ai_enabled = False
        self.game = Connect4Game(self.rows, self.columns, self.ai_enabled)
        self.create_menu()
        self.info_label = tk.Label(root, text="Player 1's Turn (Red)", font=('Arial', 14))
        self.info_label.grid(row=0, column=0, columnspan=self.columns)
        self.buttons = self.create_buttons()
        self.canvas = tk.Canvas(root, width=self.columns * 100, height=self.rows * 100, bg="blue")
        self.canvas.grid(row=2, column=0, columnspan=self.columns)
        self.draw_board()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        # Game Menu
        game_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Save Game", command=self.save_game)
        game_menu.add_command(label="Load Game", command=self.load_game)
        game_menu.add_command(label="Undo Move", command=self.undo_move)
        game_menu.add_separator()
        game_menu.add_command(label="Play Against AI", command=self.toggle_ai)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

        # Game Info Menu
        info_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Game Info", menu=info_menu)
        info_menu.add_command(label="About", command=self.show_info)

    def show_info(self):
        messagebox.showinfo("Game Info",
                            "Connect 4 Game\n\n"
                            "Developed by: Daniel Hudhra, Denisa Kercanaj, Glears Canaj, Ebube Mbakogu\n"
                            "Description: This is a Connect 4 game implemented using Python and Tkinter.\n"
                            "Enjoy playing!")

    def create_buttons(self):
        buttons = []
        for col in range(self.columns):
            button = tk.Button(self.root, text=str(col), command=lambda col=col: self.handle_move(col),
                               width=4, height=1, bg='lightblue', fg='black', font=('Arial', 14, 'bold'), bd=3)
            button.grid(row=1, column=col, padx=5, pady=5, sticky='nsew')
            buttons.append(button)
        return buttons

    def draw_board(self):
        self.canvas.delete("all")
        for c in range(self.columns):
            for r in range(self.rows):
                x0 = c * 100
                y0 = (self.rows - r - 1) * 100
                x1 = x0 + 100
                y1 = y0 + 100
                color = "white"
                if self.game.board.board[r][c] == PLAYER_ONE:
                    color = PLAYER_COLORS[PLAYER_ONE]
                elif self.game.board.board[r][c] == PLAYER_TWO:
                    color = PLAYER_COLORS[PLAYER_TWO]
                self.canvas.create_oval(x0 + 10, y0 + 10, x1 - 10, y1 - 10, fill=color, outline=color)

    def handle_move(self, col):
        result = self.game.make_move(col)
        self.draw_board()
        if result:
            messagebox.showinfo("Connect 4", result)
        self.update_info_label()
        if self.game.ai_enabled and not self.game.game_over and self.game.turn == PLAYER_TWO:
            self.game.ai_move()
            self.draw_board()
            if self.game.board.winning_move(PLAYER_TWO):
                messagebox.showinfo("Connect 4", "AI wins!")
            self.update_info_label()

    def update_info_label(self):
        if self.game.game_over:
            player = "Player 1" if self.game.turn == PLAYER_ONE else "Player 2"
            color = "Red" if self.game.turn == PLAYER_ONE else "Yellow"
            self.info_label.config(text=f"{player}'s Turn ({color})")
        else:
            player = "Player 1" if self.game.turn == PLAYER_ONE else "Player 2"
            color = "Red" if self.game.turn == PLAYER_ONE else "Yellow"
            self.info_label.config(text=f"{player}'s Turn ({color})")

    def new_game(self):
        self.game = Connect4Game(self.rows, self.columns, self.ai_enabled)
        self.draw_board()
        self.update_info_label()

    def save_game(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            self.game.save_game(file_path)

    def load_game(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            self.game = Connect4Game.load_game(file_path)
            self.draw_board()
            self.update_info_label()

    def undo_move(self):
        if self.game.undo_move():
            self.draw_board()
            self.update_info_label()

    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        self.game.ai_enabled = self.ai_enabled
        self.update_info_label()
        if self.ai_enabled:
            messagebox.showinfo("Connect 4", "AI is now enabled :)")
        else:
            messagebox.showinfo("Connect 4", "AI is now disabled")


if __name__ == "__main__":
    root = tk.Tk()
    game_gui = Connect4GUI(root)
    root.mainloop()

