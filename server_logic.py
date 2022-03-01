from operator import pos
import random
import math
from typing import List, Dict

FREE = 0
BLOCKED = 1
POSSIBLE_MOVES = ["up", "down", "left", "right"]
OPPOSITE_MOVES = {"up": "down", "down": "up", "left": "right", "right": "left"}


def generate_board(data):
    # the board
    board_height = data["board"]["height"]
    board_width = data["board"]["width"]
    board = [[FREE for _ in range(board_width)] for _ in range(board_height)]

    # blocked by my body or other snakes
    my_body = data["you"]["body"]
    my_length = data["you"]["length"]
    snakes = data["board"]["snakes"]
    bodies = [snake["body"] for snake in snakes]
    bodies.append(my_body)

    blocked_points = [item for sublist in bodies for item in sublist]
    # do not run into positions longer snakes could go    
    for head in [snake["head"] for snake in snakes if snake["length"] > my_length]:
        x = head["x"]
        y = head["y"] 
        blocked_points.append({"x": x-1, "y": y})
        blocked_points.append({"x": x, "y": y+1})
        blocked_points.append({"x": x+1, "y": y})
        blocked_points.append({"x": x, "y": y-1})
    
    # mark blocked points on the board
    for point in blocked_points:
        x = point["x"]
        y = point["y"]        
        if not (x < 0 or y < 0 or x >= board_width or y >= board_height):
            board[y][x] = BLOCKED
    
    return board

def is_legal_move(board, x, y):
    board_width = len(board[0])
    board_height = len(board)
    if x < 0 or y < 0 or x >= board_width or y >= board_height:
        return False
    
    return board[y][x] == FREE

def get_legal_moves(my_head, board):
    legal_moves = POSSIBLE_MOVES
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


def free_space(my_head, board, move):
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
    
    nx = new_head["x"]
    ny = new_head["y"]
    next_moves = POSSIBLE_MOVES
    next_moves.remove(OPPOSITE_MOVES[move])

    if is_legal_move(board, nx, ny):
        space = 1
        for next_move in next_moves:
            space += free_space(new_head, board, next_move)
        return space
    
    return 0


def point_distance(point1, point2):
    return math.sqrt((point1["x"]-point2["x"])**2 + (point1["y"]-point2["y"])**2)


def find_food_moves(my_head, my_health, foods, possible_moves):
    if len(possible_moves) < 1:
        return possible_moves
    if len(foods) == 0:
        return possible_moves

    closest_food = foods[0]
    closest_distance = point_distance(my_head, closest_food)
    for food in foods[1:]:
        current_distance = point_distance(my_head, food)
        if current_distance < closest_distance:
            closest_food = food
            closest_distance = current_distance

    #health_buffer = 10
    #if my_health - closest_distance > health_buffer:
    #    return possible_moves

    good_moves = []
    if my_head["x"] > closest_food["x"]:
        good_moves.append("left")
    elif my_head["x"] < closest_food["x"]:
        good_moves.append("right")
    if my_head["y"] > closest_food["y"]:
        good_moves.append("down")
    elif my_head["y"] < closest_food["y"]:
        good_moves.append("up")

    move_intersection = set(possible_moves).intersection(set(good_moves))
    if len(move_intersection) > 0:
        return list(move_intersection)
    return possible_moves
    
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
    print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    # generate the game board with all occupied points
    board = generate_board(data)
    print("Current board:")
    for line in reversed(board):
        print(line)

    # get the legal moves from current position and board
    possible_moves = get_legal_moves(my_head, board)
    print(f"Possible moves: {possible_moves}")

    # try to move towards food
    possible_moves = find_food_moves(my_head, data["you"]["health"], data["board"]["food"], possible_moves)

    # if have a choice go centric
    # possible_moves = go_centric(my_head, the_board_height, the_board_width, possible_moves)

    # head in direction of most free space
    move = random.choice(possible_moves)
    space = 0
    for tmp_move in possible_moves:
        tmp_space = free_space(my_head, board, move)
        print(tmp_space)
        if tmp_space > space:
            space = tmp_space
            move = tmp_move
    
    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")
    return move

def try_remove_move(move, possible_moves):
    if move in possible_moves:
        possible_moves.remove(move)