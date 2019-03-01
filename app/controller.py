import astar, math, sys, random

def setup_board(height, width, snakes, mySnake, myID):
    # create general board
    board = [[1 for col in range(width)] for row in range(height)]

    # create list of snake locations
    for snake in snakes:
        
        if snake['id'] != myID:
            head = snake['body'][0]

            top = head['y'] - 1
            bottom = head['y'] + 1
            left = head['x'] - 1
            right = head['x'] + 1

            if top > 0:
                board[top][head['x']] = 0
            if bottom < height:
                board[bottom][head['x']] = 0
            if left > 0:
                board[head['y']][left] = 0
            if right < width:
                 board[head['y']][right] = 0
            
        for segment in snake['body']:
            board[segment['y']][segment['x']] = 0
    
    return board

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
    board[tail[1]][tail[0]] = 1
    path = a_star_object.astar(tuple(head), tuple(tail))
    board[tail[1]][tail[0]] = 0

    # if there is a path and the tail is growing path to a square next to the tail
    if path and growing:
        squares = get_adjacent_squares(board, height, width, tail)
        for square in squares:
            path = a_star_object.astar(tuple(head), tuple(square))
            if path:
                return get_direction_from_path(head, list(path)[1])
    elif path and not growing:
        return get_direction_from_path(head, list(path)[1])
    else:
        return None

# even though the snake may have a clear path to the food 
# the hypot may cause it to collide with another snake
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

def get_adjacent_squares(board, height, width, location):
    x, y = location
    return[(ax, ay) for ax, ay in[(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)] if 0 <= ax < width and 0 <= ay < height and board[ay][ax] == 1]

# quickly grow to size 10? then follow tail while health is above 80%?
def get_next_move(board, height, width, food, mySnake, health):

    # get coords for my snakes head
    headX, headY = mySnake[0]['x'], mySnake[0]['y']

    # create a_star_object for pathfinding
    a_star_object = astar.AStarAlgorithm(board, width, height)
   
    #find food
    next_move = move_to_food(a_star_object, mySnake[0], food)

    print(next_move)
   
    # chase tale when larger or health is high
    if 10 < len(mySnake) < 20 and 80 < health or next_move == None:
        growing = (True if health == 100 else False)
        next_move = chase_tail(a_star_object, board, height, width, mySnake, growing)
        print('chasing %d' % health)

     # chase tale when larger or health is high
    if 20 < len(mySnake) and 60 < health or next_move == None:
        growing = (True if health == 100 else False)
        next_move = chase_tail(a_star_object, board, height, width, mySnake, growing)
        print('chasing %d' % health)
   
    # if we can eat or chase tail do that
    if next_move:
        return next_move
    
    # otherwise hope that we don't die 
    squares = get_adjacent_squares(board, height, width, (mySnake[0]['x'], mySnake[0]['x']))
    
    # move to the next avaliable square
    if squares:
        return get_direction_from_path((mySnake[0]['x'], mySnake[0]['y']), squares[0])
    # all moves have been exhausted, pray to RNJesus because it's probably GG
    else:
        print('Why the f are we here?')
        moves = ['up', 'right', 'down', 'left']
        return moves[random.randint(0,3)]

    

