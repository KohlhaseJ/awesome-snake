from operator import pos
import math

FREE = 0
BLOCKED = 1
POSSIBLE_MOVES = ["up", "down", "left", "right"]
OPPOSITE_MOVES = {"up": "down", "down": "up", "left": "right", "right": "left"}

def set_board_value(board, x, y, value):
    xi = x
    yi = len(board) - 1 - y
    board[yi][xi] = value

def get_board_value(board, x, y):
    xi = x
    yi = len(board) - 1 - y
    return board[yi][xi]

def generate_board(data):
    # the board
    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    board = [[FREE for _ in range(board_width)] for _ in range(board_height)]

    # blocked by my body or other snakes
    my_body = data["you"]["body"]
    snakes = data["board"]["snakes"]
    bodies = [snake["body"] for snake in snakes]
    bodies.append(my_body)

    blocked_points = [item for sublist in bodies for item in sublist]
        
    # mark blocked points on the board
    for point in blocked_points:
        x = point["x"]
        y = point["y"]        
        if not (x < 0 or y < 0 or x >= board_width or y >= board_height):
            set_board_value(board, x, y, BLOCKED)
    
    return board

def deep_copy_board(board):
    board_height = len(board)
    board_width = len(board[0])
    new_board = [[FREE for _ in range(board_width)] for _ in range(board_height)]
    for y in range(board_height):
        for x in range(board_width):
            new_board[y][x] = board[y][x]
    return new_board


def is_legal_move(board, x, y):
    board_width = len(board[0])
    board_height = len(board)
    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        return False
    
    return get_board_value(board, x, y) == FREE

def get_legal_moves(my_head, board):
    legal_moves = POSSIBLE_MOVES.copy()
    x = my_head["x"]
    y = my_head["y"]

    if not is_legal_move(board, x-1, y):
        try_remove_move("left", legal_moves)

    if not is_legal_move(board, x, y+1):
        try_remove_move("up", legal_moves)

    if not is_legal_move(board, x+1, y):
        try_remove_move("right", legal_moves)

    if not is_legal_move(board, x, y-1):
        try_remove_move("down", legal_moves)
    
    return legal_moves

def would_hit_longer_snake(my_head, move, my_length, snakes):
    for snake in snakes:
        snake_head = snake["head"]
        snake_length = snake["length"]
        if my_length <= snake_length:
            new_head = move_my_head(my_head, move)
            if new_head == snake_head:
                return True
    return False

def move_my_head(my_head, move):
    x = my_head["x"]
    y = my_head["y"]
    
    if move == "left":
        new_head = {"x": x-1, "y": y}
    if move == "up":
        new_head = {"x": x, "y": y+1}
    if move == "right":
        new_head = {"x": x+1, "y": y}
    if move == "down":
        new_head = {"x": x, "y": y-1}
    
    return new_head

def board_space(board):
    flat_board = [item for sublist in board for item in sublist]
    return sum(1 for position in flat_board if position == FREE)


def free_space(my_head, board, move):
    new_head = move_my_head(my_head, move)
    space = 1 if get_board_value(board, new_head["x"], new_head["y"]) == FREE else 0
    set_board_value(board, new_head["x"], new_head["y"], BLOCKED)
    next_moves = get_legal_moves(new_head, board)
    for next_move in next_moves:
        space += free_space(new_head, board, next_move)
    return space


def point_distance(point1, point2):
    return math.sqrt((point1["x"]-point2["x"])**2 + (point1["y"]-point2["y"])**2)


def get_food_moves(my_head, foods, legal_moves):
    if len(legal_moves) < 1:
        return legal_moves
    if len(foods) == 0:
        return legal_moves

    closest_food = foods[0]
    closest_distance = point_distance(my_head, closest_food)
    for food in foods[1:]:
        current_distance = point_distance(my_head, food)
        if current_distance < closest_distance:
            closest_food = food
            closest_distance = current_distance

    good_moves = []
    if my_head["x"] > closest_food["x"]:
        good_moves.append("left")
    elif my_head["x"] < closest_food["x"]:
        good_moves.append("right")
    if my_head["y"] > closest_food["y"]:
        good_moves.append("down")
    elif my_head["y"] < closest_food["y"]:
        good_moves.append("up")

    return list(set(legal_moves).intersection(set(good_moves)))

def get_space_per_move(my_head, board, legal_moves):
    space_per_move = {}
    for move in legal_moves:
        board_copy = deep_copy_board(board)
        space = free_space(my_head, board_copy, move)
        space_per_move[move] = space
    return space_per_move
    
def go_centric(my_head, the_board_height, the_board_width, possible_moves):
    if(len(possible_moves) < 1):
        return possible_moves
    
    cy = (int)(the_board_height/2)
    cx = (int)(the_board_width/2)

    good_moves = []

    if my_head["x"] > cx:
        good_moves.append("left")
    elif my_head["x"] < cx:
        good_moves.append("right")
    if my_head["y"] > cy:
        good_moves.append("down")
    elif my_head["y"] < cy:
        good_moves.append("up")

    move_intersection = set(possible_moves).intersection(set(good_moves))
    if len(move_intersection) > 0:
        return list(move_intersection)
    return possible_moves


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]

    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    # generate the game board with all occupied points
    board = generate_board(data)

    # get the legal moves from current position and board
    legal_moves = get_legal_moves(my_head, board)

    # initially rate all legal moves
    rated_moves = {}
    my_length = data["you"]["length"]
    snakes = data["board"]["snakes"]
    for move in legal_moves:
        if would_hit_longer_snake(my_head, move, my_length, snakes):
            rated_moves[move] = -1
        else:
            rated_moves[move] = 0
    
    # rate moves bringing me closer to food by my health
    foods = data["board"]["food"]
    my_health = data["you"]["health"]
    food_moves = get_food_moves(my_head, foods, legal_moves)
    for move in food_moves:
        rated_moves[move] += (150 - my_health)

    # rate moves based on space left
    total_space = board_space(board)
    space_per_move = get_space_per_move(my_head, board, legal_moves)
    for key, value in space_per_move.items():
        rated_moves[key] += (value/total_space)*100
    
    # select best rated move
    move = max(rated_moves, key=rated_moves.get)
    
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {legal_moves}")
    return move

def try_remove_move(move, possible_moves):
    if move in possible_moves:
        possible_moves.remove(move)