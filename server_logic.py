import random
from typing import List, Dict

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""


def avoid_my_neck(my_head: Dict[str, int], my_body: List[dict], possible_moves: List[str]) -> List[str]:
    """
    my_head: Dictionary of x/y coordinates of the Battlesnake head.
            e.g. {"x": 0, "y": 0}
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        try_remove_move("left", possible_moves)
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        try_remove_move("right", possible_moves)
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        try_remove_move("down", possible_moves)
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        try_remove_move("up", possible_moves)

    return possible_moves


def avoid_the_wall(my_head, the_board_height, the_board_width, possible_moves: List[str]) -> List[str]:    
    if my_head["x"] == 0:
        try_remove_move("left", possible_moves)
    if my_head["y"] == 0:
        try_remove_move("down", possible_moves)
    if my_head["x"] == the_board_width-1:
        try_remove_move("right", possible_moves)
    if my_head["y"] == the_board_height-1:
        try_remove_move("up", possible_moves)

    return possible_moves


def avoid_snake(my_head: Dict[str, int], snake_body: List[dict], possible_moves: List[str]) -> List[str]:
    for i in range(0, len(snake_body)):
        body_part = snake_body[i]
        if body_part["x"] < my_head["x"]:
            try_remove_move("left", possible_moves)
        elif body_part["x"] > my_head["x"]:
            try_remove_move("right", possible_moves)
        elif body_part["y"] < my_head["y"]:
            try_remove_move("down", possible_moves)
        elif body_part["y"] > my_head["y"]:
            try_remove_move("up", possible_moves)

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
    print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]
    print(possible_moves)

    # Don't allow your Battlesnake to move back in on it's own neck
    possible_moves = avoid_my_neck(my_head, my_body, possible_moves)
    print(possible_moves)


    # TODO: Using information from 'data', find the edges of the board and don't let your Battlesnake move beyond them
    the_board_height = data["board"]["height"]
    the_board_width = data["board"]["width"]
    possible_moves = avoid_the_wall(my_head, the_board_height, the_board_width, possible_moves)
    print(possible_moves)


    # TODO Using information from 'data', don't let your Battlesnake pick a move that would hit its own body
    possible_moves = avoid_snake(my_head, my_body[2:], possible_moves)
    print(possible_moves)


    # TODO: Using information from 'data', don't let your Battlesnake pick a move that would collide with another Battlesnake
    for snake in data["board"]["snakes"]:
        snake_body = snake["body"]
        possible_moves = avoid_snake(my_head, snake_body, possible_moves)

    print(possible_moves)

    # TODO: Using information from 'data', make your Battlesnake move towards a piece of food on the board

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    move = random.choice(possible_moves)
    # TODO: Explore new strategies for picking a move that are better than random

    print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked from all valid options in {possible_moves}")

    return move

def try_remove_move(move, possible_moves):
    if move in possible_moves:
        possible_moves.remove(move)