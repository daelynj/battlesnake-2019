import astar, math, sys, random

g_headWeight = 5
g_bodyWeight = 50
g_freeWeight = 1

file = open("game_log.txt", 'a')

def log_it(msg):
    file.write(msg)

def setup_board(height, width, snakes, myID):
    # create general board
    board = [[1 for col in range(width)] for row in range(height)]

    # create list of snake locations
    for snake in snakes:

        # add other snakes potential next moves to the board
        # NOTE this can cause issues if the snake is near a corner
        if snake['id'] != myID:
            head = snake['body'][0]

            top = head['y'] - 1
            bottom = head['y'] + 1
            left = head['x'] - 1
            right = head['x'] + 1

            if top > 0:
                board[top][head['x']] = board[top][head['x']] + g_headWeight
            if bottom < height:
                board[bottom][head['x']] = board[bottom][head['x']] + g_headWeight
            if left > 0:
                board[head['y']][left] = board[head['y']][left] + g_headWeight
            if right < width:
                board[head['y']][right] = board[head['y']][right] + g_headWeight

        # add my snake and other snakes bodies to the board
        for segment in snake['body']:
            board[segment['y']][segment['x']] = g_bodyWeight

    return board

def get_path_to_food(a_star_object, head, food):
    min_distance = float('inf')
    min_path = None

    for snack in food:
        path = a_star_object.astar((head['x'], head['y']), (snack['x'], snack['y']))

        if path:
            path = list(path)
            if len(path) < min_distance:
                min_distance = len(path)
                min_path = path

    return (min_path if min_path else None)

def move_to_food_t(head, path):
    return get_direction_from_path((head['x'], head['y']), path[1])

# NOTE maybe do a flood fill to check that getting the food won't trap it
def move_to_food (a_star_object, head, food):
    min_distance = float('inf')
    min_path = None

    for snack in food:
        path = a_star_object.astar((head['x'], head['y']), (snack['x'], snack['y']))

        if path:
            path = list(path)
            if len(path) < min_distance:
                min_distance = len(path)
                min_path = path

    if min_path:
        return get_direction_from_path((head['x'], head['y']), min_path[1])
    return None

def chase_tail(a_star_object, board, height, width, mySnake, growing):
    head = (mySnake[0]['x'], mySnake[0]['y'])
    tail = (mySnake[-1]['x'], mySnake[-1]['y'])

    # temporarily let the tail be a valid place to path to
    board[tail[1]][tail[0]] = g_freeWeight
    path = a_star_object.astar(head, tail)
    board[tail[1]][tail[0]] = g_bodyWeight

    # if there is a path and the tail is growing path to a square next to the tail
    if path and growing:
        squares = get_adjacent_squares(board, height, width, tail)
        for square in squares:
            path = a_star_object.astar(head, square)
            if path:
                return get_direction_from_path(head, list(path)[1])
    elif path and not growing:
        return get_direction_from_path(head, list(path)[1])
    else:
        return None

# even though the snake may have a clear path to the food
# the hypot may cause it to collide with another snake
# NOTE maybe return a list of prioratized moves
# if the snake needs to move diagonal up and right then right is always tried first in this case
# returning a list or other valid moves may prevent the snake from doing stupid shit
def get_direction_from_path(start, finish):
    x0, y0 = start
    x1, y1 = finish

    dx = x1 - x0
    dy = y1 - y0

    if dx > 0:
        return 'right'
    elif dy > 0:
        return 'down'
    elif dx < 0:
        return 'left'
    elif dy < 0:
        return 'up'

    # directions = []

    # if dx > 0:
    #     directions.append['right']
    # if dy > 0:
    #     directions.append['down']
    # if dx < 0:
    #     directions.append['left']
    # if dy < 0:
    #     directions.append['up']

    # return directions[0]

# check that moving in a direction won't kill it
# if it won't die return the current direction
# else try another direction
# return the next best move that won't kill it (hopefully)
def check_direction(board, height, width, head, tail, health, direction):
    next_head = head

    if direction == 'right':
        next_head['x'] = next_head['x'] + 1
    elif direction == 'left':
        next_head['x'] = next_head['x'] - 1
    elif direction == 'up':
        next_head['y'] = next_head['y'] - 1
    elif direction == 'down':
        next_head['y'] = next_head['y'] + 1

    if health != 100:
        board[tail['y']][tail['x']] = 1

    if board[next_head['y']][next_head['x']] == 1:
        print('direction okay')
        return direction
    else:
        print('direction not okay')
        squares = get_adjacent_squares(board, height, width, (head['x'], head['y']))
        if squares:
            return get_direction_from_path((head['x'], head['y']), squares[0])
        return None

    # Need to improve this but it kinda works
    # deepcopy the board
    # temp = [r[:] for r in board]

    # stack = [(x, y)]
    # count = 0

    # while stack:
    #     x, y = stack.pop()

    #     if temp[x][y] == 1:
    #         temp[x][y] = 0
    #         count += 1
    #         if x > 0:
    #             stack.append((x-1, y))
    #         if x < width-1:
    #             stack.append((x+1, y))
    #         if y > 0:
    #             stack.append((x, y-1))
    #         if y < height-1:
    #             stack.append((x, y+1))

    # print('Floodfill count: %d' % count)

    # if 0 < count <  (width * height) - 2*(num_snakes * length):
    #     board = [r[:] for r in temp]

    # return board
    return None

# returns a list of squares that are on the board adjacent to the snake head
def get_adjacent_squares(board, height, width, location):
    x, y = location
    return[(ax, ay) for ax, ay in[(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)] if 0 <= ax < width and 0 <= ay < height and board[ay][ax] == 1]

# quickly grow to size 10? then follow tail while health is above 80%?
# NOTE maybe try to trap another snake if it is along the edge of the board
# NOTE maybe look for encirclements when the snake is much larger than an enemy
def get_next_move(board, height, width, food, mySnake, health):

    # get coords for my snakes head
    headX, headY = mySnake[0]['x'], mySnake[0]['y']

    # create a_star_object for pathfinding
    a_star_object = astar.AStarAlgorithm(board, width, height)

    path = get_path_to_food(a_star_object, mySnake[0], food)
    next_move = None
    if path:
        next_move = move_to_food_t( mySnake[0], path)

    # find food
    # NOTE maybe break this into 2 functions... 1 to get the distance to the closest food and 1 to move there
    # NOTE this could be useful for when the snake gets long and should only try to get food when it is close
    #next_move = move_to_food(a_star_object, mySnake[0], food)

    # chase tale when larger or health is high
    if (len(mySnake) in range(10,21) and health > 80) or next_move == None:
        growing = (True if health == 100 else False)
        next_move = chase_tail(a_star_object, board, height, width, mySnake, growing)

     # chase tale when larger or health is high
     # NOTE might be worth prioratizing getting food that is close by (3 tiles?)
    if (len(mySnake) > 20 and health > 60) or next_move == None:
        if path and len(path) < width / 4 and health < 80:
            next_move = move_to_food_t( mySnake[0], path)
        else:
            growing = (True if health == 100 else False)
            next_move = chase_tail(a_star_object, board, height, width, mySnake, growing)

    # if we can eat or chase tail do that
    if next_move:
        return next_move

    # otherwise hope that we don't die
    squares = get_adjacent_squares(board, height, width, (mySnake[0]['x'], mySnake[0]['y']))

    # move to the next avaliable square
    if squares:
        return get_direction_from_path((mySnake[0]['x'], mySnake[0]['y']), squares[0])
    # all moves have been exhausted, pray to RNJesus because it's probably GG
    else:
        print('Why the f are we here?')
        moves = ['up', 'right', 'down', 'left']
        return moves[random.randint(0,3)]
