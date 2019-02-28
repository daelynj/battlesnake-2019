import astar, math, sys, random

def setup_board(height, width, snakes, mySnake, myID):
    # create general board
    board = [[1 for col in range(width)] for row in range(height)]

    # create list of snake locations
    for snake in snakes:
        if snake['id'] != myID:
            # NOTE maybe add places enemie snake head could move

            for segment in snake['body']:
                board[segment['x']][segment['y']] = 0
    
    return board

        
# Findest the closest reachable piece of food
def find_best_food(board, food, headX, headY):
    # do a floodfill to find reachable food
    # then find the closest piece
    return None 


# Quickly grow to size 10? then follow tail while heatlh is above 80%?
def get_next_move():
    #find food if needed
    
    return None
