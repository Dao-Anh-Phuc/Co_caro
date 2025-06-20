import tkinter as tk
import random
import math

# ------------------------- MCTS (Monte Carlo Tree Search) -------------------------
class MCTS:
    def __init__(self, board, player, simulations=500):  # Tăng số lần mô phỏng lên 1000
        self.board = board
        self.player = player
        self.opponent = 'X' if player == 'O' else 'O'
        self.simulations = simulations
        self.visits = {}
        self.wins = {}

    def get_possible_moves(self, board):
        return [(i, j) for i in range(len(board)) for j in range(len(board)) if board[i][j] == ' ']

    def is_winner(self, board, player):
        # Kiểm tra 3 quân liên tiếp trên bàn 4x4
        size = len(board)
        
        # Kiểm tra hàng ngang
        for i in range(size):
            for j in range(size - 2):
                if all([board[i][j+k] == player for k in range(3)]):
                    return True
        
        # Kiểm tra cột dọc
        for i in range(size - 2):
            for j in range(size):
                if all([board[i+k][j] == player for k in range(3)]):
                    return True
        
        # Kiểm tra đường chéo chính (từ trên xuống dưới)
        for i in range(size - 2):
            for j in range(size - 2):
                if all([board[i+k][j+k] == player for k in range(3)]):
                    return True
        
        # Kiểm tra đường chéo phụ (từ dưới lên)
        for i in range(2, size):
            for j in range(size - 2):
                if all([board[i-k][j+k] == player for k in range(3)]):
                    return True
        
        return False

    def is_draw(self, board):
        return all([board[i][j] != ' ' for i in range(len(board)) for j in range(len(board))])

    def simulate_game(self, board, current_player):
        possible_moves = self.get_possible_moves(board)
        while possible_moves:
            move = random.choice(possible_moves)
            board[move[0]][move[1]] = current_player
            if self.is_winner(board, current_player):
                return current_player
            if self.is_draw(board):
                return 'Draw'
            current_player = 'X' if current_player == 'O' else 'O'
            possible_moves = self.get_possible_moves(board)
        return 'Draw'

    def ucb1(self, move, total_simulations):
        wins = self.wins.get(move, 0)
        visits = self.visits.get(move, 0)
        if visits == 0:
            return float('inf')
        return wins / visits + math.sqrt(2 * math.log(total_simulations) / visits)

    def check_threat(self, board, player):
        """Kiểm tra xem đối thủ có thể chiến thắng trong một nước đi không"""
        possible_moves = self.get_possible_moves(board)
        for move in possible_moves:
            board_clone = [row[:] for row in board]
            board_clone[move[0]][move[1]] = player
            if self.is_winner(board_clone, player):
                return move
        return None

    def mcts(self, board):
        best_move = None
        possible_moves = self.get_possible_moves(board)
        total_simulations = 0

        # Kiểm tra nếu mình có thể thắng ngay
        winning_move = self.check_threat(board, self.player)
        if winning_move:
            return winning_move

        # Kiểm tra nếu đối thủ có thể thắng ngay (phải chặn)
        threat_move = self.check_threat(board, self.opponent)
        if threat_move:
            return threat_move

        # Khởi tạo visits và wins cho các nước đi có thể
        for move in possible_moves:
            self.visits[move] = 0
            self.wins[move] = 0

        # Thực hiện mô phỏng
        for _ in range(self.simulations):
            move = random.choice(possible_moves)
            board_clone = [row[:] for row in board]
            board_clone[move[0]][move[1]] = self.player
            winner = self.simulate_game(board_clone, self.opponent)
            
            self.visits[move] += 1
            if winner == self.player:
                self.wins[move] += 1
            elif winner == 'Draw':
                self.wins[move] += 0.5  # Cho điểm một nửa nếu hòa
                
            total_simulations += 1

        # Chọn nước đi có UCB1 cao nhất
        best_ucb1 = -float('inf')
        for move in possible_moves:
            ucb_value = self.ucb1(move, total_simulations)
            if ucb_value > best_ucb1:
                best_ucb1 = ucb_value
                best_move = move

        return best_move if best_move else random.choice(possible_moves)

# ------------------------- Minimax with Alpha-Beta Pruning -------------------------
class MinimaxAlphaBeta:
    def __init__(self, board, player, max_depth=4):  # Giảm độ sâu để tăng tốc độ
        self.board = board
        self.player = player
        self.max_depth = max_depth
        self.opponent = 'X' if player == 'O' else 'O'

    def is_winner(self, board, player):
        size = len(board)
        
        # Kiểm tra hàng ngang
        for i in range(size):
            for j in range(size - 2):
                if all([board[i][j+k] == player for k in range(3)]):
                    return True
        
        # Kiểm tra cột dọc
        for i in range(size - 2):
            for j in range(size):
                if all([board[i+k][j] == player for k in range(3)]):
                    return True
        
        # Kiểm tra đường chéo chính (từ trên xuống dưới)
        for i in range(size - 2):
            for j in range(size - 2):
                if all([board[i+k][j+k] == player for k in range(3)]):
                    return True
        
        # Kiểm tra đường chéo phụ (từ dưới lên)
        for i in range(2, size):
            for j in range(size - 2):
                if all([board[i-k][j+k] == player for k in range(3)]):
                    return True
        
        return False

    def is_draw(self, board):
        return all([board[i][j] != ' ' for i in range(len(board)) for j in range(len(board))])

    def evaluate(self, board):
        score = 0
        size = len(board)
        center = size // 2
        
        # Đánh giá dựa trên số lượng 2 quân liên tiếp và 3 quân liên tiếp
        for player in [self.player, self.opponent]:
            weight = 1 if player == self.player else -1
            
            # Kiểm tra hàng ngang
            for i in range(size):
                for j in range(size - 2):
                    line = [board[i][j+k] for k in range(3)]
                    count = line.count(player)
                    empty = line.count(' ')
                    if count == 3:
                        score += 100 * weight
                    elif count == 2 and empty == 1:
                        score += 10 * weight
                    elif count == 1 and empty == 2:
                        score += 1 * weight
            
            # Kiểm tra cột dọc (tương tự)
            # Kiểm tra đường chéo (tương tự)
        
        # Ưu tiên trung tâm
        if board[center][center] == self.player:
            score += 5
        elif board[center][center] == self.opponent:
            score -= 5
            
        return score

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if self.is_winner(board, self.player):
            return 100 - depth
        elif self.is_winner(board, self.opponent):
            return depth - 100
        elif self.is_draw(board):
            return 0

        if depth == 0:
            return self.evaluate(board)

        possible_moves = self.get_possible_moves(board)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in possible_moves:
                board[move[0]][move[1]] = self.player
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board[move[0]][move[1]] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                board[move[0]][move[1]] = self.opponent
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board[move[0]][move[1]] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def best_move(self, board):
        best_value = float('-inf')
        best_move = None
        possible_moves = self.get_possible_moves(board)
        
        # Kiểm tra nếu có thể thắng ngay
        for move in possible_moves:
            board[move[0]][move[1]] = self.player
            if self.is_winner(board, self.player):
                board[move[0]][move[1]] = ' '
                return move
            board[move[0]][move[1]] = ' '
        
        # Kiểm tra nếu đối thủ có thể thắng ngay (phải chặn)
        for move in possible_moves:
            board[move[0]][move[1]] = self.opponent
            if self.is_winner(board, self.opponent):
                board[move[0]][move[1]] = ' '
                return move
            board[move[0]][move[1]] = ' '
        
        # Nếu không, sử dụng Minimax
        for move in possible_moves:
            board[move[0]][move[1]] = self.player
            move_value = self.minimax(board, self.max_depth, float('-inf'), float('inf'), False)
            board[move[0]][move[1]] = ' '
            if move_value > best_value or (move_value == best_value and random.random() < 0.3):  # Thêm yếu tố ngẫu nhiên
                best_value = move_value
                best_move = move
                
        return best_move if best_move else random.choice(possible_moves)

    def get_possible_moves(self, board):
        return [(i, j) for i in range(len(board)) for j in range(len(board)) if board[i][j] == ' ']

# ------------------------- Giao diện Game -------------------------
class CaroGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Caro Game: MCTS vs Minimax (3x3)")
        self.board_size = 3
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.ai1 = MCTS(self.board, 'X')  # AI1 sử dụng MCTS (X)
        self.ai2 = MinimaxAlphaBeta(self.board, 'O')  # AI2 sử dụng Minimax (O)
        self.buttons = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 'X'  # X bắt đầu trước
        self.game_over = False
        self.create_board()

    def create_board(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.buttons[i][j] = tk.Button(
                    self.root, text=' ', width=25, height=10, 
                    font=("Arial", 12), 
                    command=lambda row=i, col=j: self.human_move(row, col) if self.current_player == 'X' else None
                )
                self.buttons[i][j].grid(row=i, column=j)

        self.status_label = tk.Label(self.root, text="Lượt X (MiniMax)", font=("Arial", 14))
        self.status_label.grid(row=self.board_size, column=0, columnspan=self.board_size)

        start_ai_button = tk.Button(
            self.root, text="AI tự đấu", font=("Arial", 14), 
            command=self.start_ai_vs_ai
        )
        start_ai_button.grid(row=self.board_size+1, column=0, columnspan=self.board_size)

        reset_button = tk.Button(
            self.root, text="Reset", font=("Arial", 14), 
            command=self.restart_game
        )
        reset_button.grid(row=self.board_size+2, column=0, columnspan=self.board_size)

    def start_ai_vs_ai(self):
        if not self.game_over:
            self.ai_move()

    def ai_move(self):
        if self.game_over:
            return

        if self.current_player == 'X':
            move = self.ai1.mcts(self.board)
            player_name = "Minimax (X)"
        else:
            move = self.ai2.best_move(self.board)
            player_name = "MCTS (O)"

        if move:
            row, col = move
            self.make_move(row, col, self.current_player)
            
            # Kiểm tra kết quả
            result = self.check_game_result()
            if result:
                self.display_result(result)
                self.game_over = True
            else:
                # Đổi lượt
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.status_label.config(text=f"Lượt {self.current_player} ({'Minimax' if self.current_player == 'X' else 'MCTS'})")
                
                # Tiếp tục nếu chưa kết thúc
                if not self.game_over:
                    self.root.after(1000, self.ai_move)  # Thêm độ trễ 500ms để dễ quan sát

    def human_move(self, row, col):
        if self.board[row][col] == ' ' and not self.game_over and self.current_player == 'X':
            self.make_move(row, col, 'X')
            result = self.check_game_result()
            if result:
                self.display_result(result)
                self.game_over = True
            else:
                self.current_player = 'O'
                self.status_label.config(text="Lượt O (MCTS)")
                self.root.after(500, self.ai_move)  # AI (O) đi sau khi người chơi (X) đi

    def make_move(self, row, col, player):
        self.board[row][col] = player
        self.buttons[row][col].config(text=player)
        self.buttons[row][col].config(
            bg='white' if player == 'X' else 'black',
            fg='black' if player == 'X' else 'white'
        )

    def check_game_result(self):
        if self.ai1.is_winner(self.board, 'X'):
            return "Minimax (X) thắng!"
        elif self.ai1.is_winner(self.board, 'O'):
            return "MCTS (O) thắng!"
        elif self.ai1.is_draw(self.board):
            return "Hòa!"
        return None

    def display_result(self, message):
        self.status_label.config(text=message)
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.buttons[i][j].config(state=tk.DISABLED)

    def restart_game(self):
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.buttons[i][j].config(text=' ', bg='SystemButtonFace', fg='black', state=tk.NORMAL)
        self.current_player = 'X'
        self.game_over = False
        self.status_label.config(text="Lượt X (MCTS)")

if __name__ == "__main__":
    root = tk.Tk()
    game = CaroGame(root)
    root.mainloop()