import turtle
import random

global writer
highlighter = None  # để quản lý vùng tô nổi bật của AI
score_marker = None  # Turtle chuyên dùng để vẽ điểm đánh giá nước đi

writer = turtle.Turtle()
writer.hideturtle()
writer.penup()
writer.color("red")

# =================== GLOBALS ===================
MAX_DEPTH = 2
move_history = []

# =================== BOARD LOGIC ===================
def make_empty_board(sz):
    return [[" "] * sz for _ in range(sz)]

def is_empty(board):
    return all(cell == " " for row in board for cell in row)

def is_in(board, y, x):
    return 0 <= y < len(board) and 0 <= x < len(board)

def is_win(board):
    black = score_of_col(board, 'b')
    white = score_of_col(board, 'w')
    sum_sumcol_values(black)
    sum_sumcol_values(white)

    if 5 in black and black[5] == 1:
        return 'Người chơi thắng'
    elif 5 in white and white[5] == 1:
        return 'Máy thắng'

    if sum(black.values()) == black[-1] and sum(white.values()) == white[-1] or not possible_moves(board):
        return 'Draw'
    return 'Continue playing'

def reset_game():
    global board, move_history
    move_history.clear()
    board = make_empty_board(len(board))
    turtle.clearscreen()
    initialize(len(board))

def show_help():
    writer.clear()
    board_size = len(board)
    writer.color("blue")
    help_text = [
        "Người chơi cần xếp 5 quân liên tiếp",
        "trên cùng một hàng, cột hoặc đường chéo.",
        "Bấm nút Restart để chơi lại.",
        "Luật chơi Game:"
    ]
    for i, line in enumerate(help_text):
        writer.goto(board_size / 2, board_size / 2 + 2 - i * 0.8)
        writer.write(line, align="center", font=("Arial", 14, "normal"))
   
def show_result(message):
    writer.clear()
    board_size = len(board)
    base_y = board_size + 15  # toạ độ cao gần đáy bàn cờ
    background = turtle.Turtle()
    background.hideturtle()
    background.penup()
    background.goto(board_size / 2 - 4, base_y / 2 + 1)
    background.color("lightgreen")
    background.begin_fill()
    background.pendown()
    background.goto(board_size / 2 + 4, base_y / 2 + 1)
    background.goto(board_size / 2 + 4, base_y / 2 - 1.5)
    background.goto(board_size / 2 - 4, base_y / 2 - 1.5)
    background.goto(board_size / 2 - 4, base_y / 2 + 1)
    background.end_fill()
    background.penup()
    writer.color("black")
    lines = message.split("\n")
    for i, line in enumerate(lines):
        writer.goto(board_size / 2, base_y/ 2 + 0.5 - i * 0.8)
        writer.write(line, align="center", font=("Arial", 20, "bold"))

def highlight_move(x, y):
    global highlighter
    if highlighter is None:
        highlighter = turtle.Turtle()
        highlighter.hideturtle()
        highlighter.penup()
        highlighter.speed(0)

    highlighter.clear()
    highlighter.color("lightgreen")
    highlighter.goto(x + 0.5, y + 0.5)
    highlighter.dot(40)

def draw_scored_moves(board, col='w'):
    global score_marker
    if score_marker is None:
        score_marker = turtle.Turtle()
        score_marker.hideturtle()
        score_marker.penup()
        score_marker.speed(0)
    else:
        score_marker.clear()  # XÓA các chấm cũ trước khi vẽ chấm mới

    anticol = 'b' if col == 'w' else 'w'
    moves = possible_moves(board)
    scores = {}

    for (y, x) in moves:
        board[y][x] = col
        score = evaluate(board, col, anticol)
        scores[(y, x)] = score
        board[y][x] = ' '

    if not scores:
        return

    max_score = max(scores.values())
    average_score = sum(scores.values()) / len(scores)
    
    for (y, x), score in scores.items():
        score_marker.goto(x + 0.5, y + 0.5)
        if score == max_score:
            score_marker.color("red")
            score_marker.dot(10)
        elif score >= average_score:
            score_marker.color("blue")
            score_marker.dot(6)



# =================== SCORING ===================
def march(board, y, x, dy, dx, length):
    yf, xf = y + length * dy, x + length * dx
    while not is_in(board, yf, xf):
        yf -= dy
        xf -= dx
    return yf, xf

def score_ready(scorecol):
    sumcol = {0: {},1: {},2: {},3: {},4: {},5: {},-1: {}}
    for key in scorecol:
        for score in scorecol[key]:
            if key in sumcol[score]:
                sumcol[score][key] += 1
            else:
                sumcol[score][key] = 1
    return sumcol

def sum_sumcol_values(sumcol):
    for key in sumcol:
        if key == 5:
            sumcol[5] = int(1 in sumcol[5].values())
        else:
            sumcol[key] = sum(sumcol[key].values())

def score_of_list(lis, col):
    blank = lis.count(' ')
    filled = lis.count(col)
    if blank + filled < 5:
        return -1
    elif blank == 5:
        return 0
    else:
        return filled

def row_to_list(board, y, x, dy, dx, yf, xf):
    row = []
    while y != yf + dy or x != xf + dx:
        row.append(board[y][x])
        y += dy
        x += dx
    return row

def score_of_row(board, cordi, dy, dx, cordf, col):
    colscores = []
    y, x = cordi
    yf, xf = cordf
    row = row_to_list(board, y, x, dy, dx, yf, xf)
    for start in range(len(row) - 4):
        score = score_of_list(row[start:start + 5], col)
        colscores.append(score)
    return colscores

def score_of_col(board, col):
    f = len(board)
    scores = {(0,1):[], (-1,1):[], (1,0):[], (1,1):[]}
    for start in range(f):
        scores[(0,1)].extend(score_of_row(board, (start, 0), 0, 1, (start, f-1), col))
        scores[(1,0)].extend(score_of_row(board, (0, start), 1, 0, (f-1, start), col))
        scores[(1,1)].extend(score_of_row(board, (start, 0), 1, 1, (f-1, f-1-start), col))
        scores[(-1,1)].extend(score_of_row(board, (start,0), -1, 1, (0,start), col))
        if start + 1 < f:
            scores[(1,1)].extend(score_of_row(board, (0, start+1), 1, 1, (f-2-start, f-1), col)) 
            scores[(-1,1)].extend(score_of_row(board, (f -1 , start + 1), -1,1, (start+1, f-1), col))
    return score_ready(scores)

# =================== AI (Minimax + Alpha-Beta) ===================
def score_line(segment, col):
    opp = 'w' if col == 'b' else 'b'
    if opp in segment and col in segment:
        return 0  # xen lẫn thì không tính
    count = segment.count(col)
    blank = segment.count(' ')
    if count == 5:
        return 1000000
    elif count == 4 and blank == 1:
        if segment[0] == ' ' and segment[4] == ' ':
            return 100000  # bốn quân hai đầu trống
        return 10000  # bốn quân một đầu trống
    elif count == 3 and blank == 2:
        if segment[0] == ' ' and segment[4] == ' ':
            return 1000  # ba quân hai đầu trống
        return 100  # ba quân một đầu trống
    elif count == 2 and blank == 3:
        return 50
    elif count == 1 and blank == 4:
        return 10
    return 0
# hàm đánh giá (evaluate) để tính điểm cho mỗi nước đi, giúp AI chọn nước đi tốt nhất.
# Heuristic là một phương pháp tìm kiếm không tối ưu nhưng hiệu quả, giúp AI đưa ra quyết định nhanh chóng.
def evaluate(board, col, anticol):
    total_score = 0
    directions = [(0,1), (1,0), (1,1), (-1,1)]
    size = len(board)

    for y in range(size):
        for x in range(size):
            for dy, dx in directions:
                segment = []
                for i in range(5):
                    ny = y + i * dy
                    nx = x + i * dx
                    if not is_in(board, ny, nx):
                        break
                    segment.append(board[ny][nx])
                if len(segment) == 5:
                    total_score += score_line(segment, col)
                    total_score -= score_line(segment, anticol)
    return total_score

# minimax sử dụng duyệt qua các nước đi có thể và tính điểm cho mỗi nc đi
# alpha và beta được sử dụng để cắt bớt nhánh trong cây tìm kiếm
def minimax(board, depth, alpha, beta, maximizingPlayer, col, anticol):
    result = is_win(board)
    if result == 'White won':
        return None, 10**6
    if result == 'Black won':
        return None, -10**6
    if result == 'Draw' or depth == 0:
        return None, evaluate(board, col, anticol)

    best_move = None  # nước đi tối ưu mà thuật toán minimax tìm ra
    moves = list(possible_moves(board).keys())  # lấy tất cả các nước đi hợp lệ

    if maximizingPlayer:   # AI chơi
        max_eval = -float('inf')
        for move in moves:
            y, x = move
            board[y][x] = col
            _, eval = minimax(board, depth - 1, alpha, beta, False, col, anticol)
            board[y][x] = ' '
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return best_move, max_eval
    else:     # Người chơi
        min_eval = float('inf')
        for move in moves:
            y, x = move
            board[y][x] = anticol
            _, eval = minimax(board, depth - 1, alpha, beta, True, col, anticol)
            board[y][x] = ' '
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return best_move, min_eval

def best_move_minimax(board, col):
    anticol = 'b' if col == 'w' else 'w'
    move, _ = minimax(board, MAX_DEPTH, -float('inf'), float('inf'), True, col, anticol)
    draw_scored_moves(board, col)
    return move

# =================== MOVE MANAGEMENT ===================
def possible_moves(board):  
    size = len(board)
    moves = set()
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    for y in range(size):
        for x in range(size):
            if board[y][x] != ' ':
                for dy, dx in directions:
                    ny, nx = y + dy, x + dx
                    if is_in(board, ny, nx) and board[ny][nx] == ' ':
                        moves.add((ny, nx))

    # Nếu bàn cờ rỗng thì đi chính giữa
    if not moves:
        center = size // 2
        moves.add((center, center))

    return {move: False for move in moves}

# =================== GRAPHICS ===================
def draw_stone(x, y, turtle_obj):
    turtle_obj.goto(x + 0.5, y + 0.5 - 0.3)
    turtle_obj.pendown()
    turtle_obj.begin_fill()
    turtle_obj.circle(0.3)
    turtle_obj.end_fill()
    turtle_obj.penup()


def getindexposition(x, y):
    return int(x), int(y)


def click(x, y):
    global board, colors, move_history
    global score_marker
    if score_marker:
        score_marker.clear()

    x, y = getindexposition(x, y)
    if not is_in(board, y, x) or board[y][x] != ' ':
        return
    if highlighter:
        highlighter.clear()  # << XÓA VÒNG SÁNG CỦA AI TRƯỚC ĐÓ
    board[y][x] = 'b'
    draw_stone(x, y, colors['b'])
    move_history.append((x, y))
    result = is_win(board)
    if result != 'Continue playing':
        show_result(f"{result}\nNhấn restart để chơi lại hihi.")
        screen.onkey(reset_game, 'r')
        screen.listen()
        return

    ay, ax = best_move_minimax(board, 'w')
    board[ay][ax] = 'w'
    highlight_move(ax, ay)  # ← THÊM VÀO ĐÂY
    draw_stone(ax, ay, colors['w'])
    move_history.append((ax, ay))
    result = is_win(board)
    if result != 'Continue playing':
        show_result(f"{result}\nNhấn restart để chơi lại hihi.")
        screen.onkey(reset_game, 'r')
        screen.listen()
        return

def button_area(x, y):
    if -0.5 <= x <= 2.5 and len(board) + 1.1 <= y <= len(board) + 1.7:
        reset_game()
    elif len(board) - 2.5 <= x <= len(board) + 0.5 and len(board) + 1.1 <= y <= len(board) + 1.7:
        show_help()

def add_buttons():
    def draw_button(t, x, y, text):
        t.penup()
        t.goto(x, y)
        t.color("black", "lightblue")
        t.begin_fill()
        t.pendown()
        for _ in range(2):
            t.forward(3)
            t.left(90)
            t.forward(1)
            t.left(90)
        t.end_fill()
        t.penup()
        t.goto(x + 1.5, y + 0.5)
        t.color("black")
        t.write(text, align="center", font=("Arial", 12, "bold"))

    btn_restart = turtle.Turtle()
    btn_restart.hideturtle()
    btn_restart.speed(0)
    draw_button(btn_restart, -0.3, len(board) + 1.1, "Restart")

    btn_help = turtle.Turtle()
    btn_help.hideturtle()
    btn_help.speed(0)
    draw_button(btn_help, len(board) - 2.2, len(board) + 1.1, "Help")

# =================== GRAPHICS ===================
def initialize(size):
    global board, screen, colors
    board = make_empty_board(size)
    screen = turtle.Screen()
    screen.setup(920, 900)
    screen.setworldcoordinates(-0.5, size + 3, size + 0.5, -1.5)
    screen.bgcolor('orange')
    screen.tracer(0)

    colors = {
        'w': turtle.Turtle(),
        'b': turtle.Turtle()
    }

    color_map = {
        'w': 'white',
        'b': 'black'
    }

    for k in colors:
        colors[k].ht()
        colors[k].penup()
        colors[k].speed(0)
        colors[k].color(color_map[k])

    border = turtle.Turtle()
    border.speed(0)
    border.penup()
    for i in range(size + 1):
        y = i
        border.goto(0, y)
        border.pendown()
        border.goto(size, y)
        border.penup()

    for j in range(size + 1):
        x = j
        border.goto(x, 0)
        border.pendown()
        border.goto(x, size)
        border.penup()

    border.hideturtle()
    draw_labels(size)


    screen.onclick(click)
    screen.onclick(button_area, btn=1, add=True)
    add_buttons()
    screen.mainloop()
def draw_labels(board_size):
    label_turtle = turtle.Turtle()
    label_turtle.hideturtle()
    label_turtle.penup()
    label_turtle.color("black")
    label_turtle.speed(0)

    font = ("Arial", 10, "normal")

    # Cột: A, B, C, ...
    for x in range(board_size):
        char = chr(ord('A') + x)
        label_turtle.goto(x + 0.5, -0.3)
        label_turtle.write(char, align="center", font=font)

    # Hàng: 1, 2, 3, ...
    for y in range(board_size):
        label_turtle.goto(-0.2, y + 0.7)
        label_turtle.write(str(y + 1), align="right", font=font)

if __name__ == "__main__":
    initialize(15)
