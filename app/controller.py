import astar, math, sys, random

def grid_setup(food, width, height, snakes, mySnake, mySnakeID):

    generic_grid = []
    # General grid setup
    for y in range(0, height):
        new_list = []
        for x in range(0, width):
            new_list.append(1)
        generic_grid.append(new_list)

    food_grid = []
    # Food locations
    for point in food:
        locationX = point['x']
        locationY = point['y']
        food_grid.append([locationX, locationY])

    # Snake locations:
    for snake in snakes:
        body = snake['body']
        snakeID = snake['id']
        if snakeID != mySnakeID:
            head = body[0]
            headX = head['x']
            headY = head['y']

            top = headY - 1
            bottom = headY + 1
            left = headX - 1
            right = headX + 1

            # Possible next moves
            if top > 0:
                generic_grid[top][headX] = 0
            if bottom < height:
                generic_grid[bottom][headX] = 0
            if left > 0:
                generic_grid[headY][left] = 0
            if right < width:
                generic_grid[headY][right] = 0

        # Add snakes to the grid
        for point in body:
            pointX = point['x']
            pointY = point['y']
            generic_grid[pointY][pointX] = 0

    grid_options = []

    grid_options.append(generic_grid)
    grid_options.append(food_grid)

    return grid_options


def get_crows_dist(me, you):
    (x1, y1) = me
    (x2, y2) = you
    return abs(math.hypot(x2 - x1, y2 - y1))


def get_my_snake_coordinates(snakes, your_id):
    for snake in snakes:
        if snake['id'] == your_id:
            return snake['coords']


def get_closest_food(food_list, head_x, head_y):
    current_minimum = 10000
    for position in food_list:
        pellet_distance = get_crows_dist((head_x, head_y),position)
        if pellet_distance < current_minimum:
            current_minimum = pellet_distance
            target_position = position
    return tuple(target_position)


def get_neighbors(node, lines, height, width):
    (x, y) = node 
    return[(nx, ny) for nx, ny in[(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)] if 0 <= nx < width and 0 <= ny < height and lines[ny][nx] == 1]


# def flood_fill(grid, x, y, width, height, num_snakes, length):

#     # deepcopy the grid 
#     temp = [r[:] for r in grid]

#     stack = [(x, y)]
#     count = 0

#     while stack:
#         x, y = stack.pop()

#         if temp[x][y] == 1:
#             temp[x][y] = 0
#             count += 1
#             if x > 0:
#                 stack.append((x-1, y))
#             if x < width-1:
#                 stack.append((x+1, y))
#             if y > 0:
#                 stack.append((x, y-1))
#             if y < height-1:
#                 stack.append((x, y+1))

#     print('Floodfill count: %d' % count)

#     if 0 < count <  (width * height) - 2*(num_snakes * length):
#         grid = [r[:] for r in temp]

#     return grid


def get_direction(start, end):
    currX = start[0]
    currY = start[1]
    nextX = end[0]
    nextY = end[1]
    deltaX = nextX - currX
    deltaY = nextY - currY
    if deltaX > 0:
        return 'right'
    elif deltaY > 0:
        return 'down'
    elif deltaX < 0:
        return 'left'
    elif deltaY < 0:
        return 'up'


def move_to_food(a_star_object, food_list, head_x, head_y):
    current_minimum = float('inf')
    current_path = None
    for food in food_list:
        path = a_star_object.astar((head_x, head_y), tuple(food))
        if path:
            path = list(path)
            if len(path) < current_minimum:
                current_minimum = len(path)
                current_path = path
    if current_path:
        return get_direction((head_x, head_y), list(current_path)[1])
    return None


def chase_tail(a_star_object, grid_options, mySnake, head_x, head_y, isGonnaGrow, height, width):
    myTail = (mySnake[-1].get("x"), mySnake[-1].get("y"))
    grid_options[0][myTail[1]][myTail[0]] = 1
    path = a_star_object.astar((head_x, head_y), myTail)
    grid_options[0][myTail[1]][myTail[0]] = 0
    if path:
        if not isGonnaGrow:
            return get_direction((head_x, head_y), list(path)[1])
        else:
            neighbours = get_neighbors(myTail, grid_options[0], height, width)
            for neighbour in neighbours:
                path = a_star_object.astar((head_x, head_y), neighbour)
                if path:
                    return get_direction((head_x, head_y), list(path)[1])

    return None

# Quickly grow to a length of 10 then follow tail
def get_move(grid_options, target, head_x, head_y, height, width, mySnake, myHealth, num_snakes):

    # if head_x < width-1:
    #     grid_options[0] = flood_fill(grid_options[0], head_x+1, head_y, width, height, num_snakes, len(mySnake))
    # if 0 < head_x:
    #     grid_options[0] = flood_fill(grid_options[0], head_x-1, head_y, width, height, num_snakes, len(mySnake))
    # if head_y < height-1:
    #     grid_options[0] = flood_fill(grid_options[0], head_x, head_y+1, width, height, num_snakes, len(mySnake))
    # if 0 < head_y:
    #     grid_options[0] = flood_fill(grid_options[0], head_x, head_y-1, width, height, num_snakes, len(mySnake))

    a_star_object = astar.AStarAlgorithm(grid_options[0], width, height)

    myLength = len(mySnake)
    move = move_to_food(a_star_object, grid_options[1], head_x, head_y)

    if myLength > 10 and myHealth > 80 or move == None:
        gonnaGrow = False
        if myHealth == 100:
            gonnaGrow = True
        move = chase_tail(a_star_object, grid_options, mySnake, head_x, head_y, gonnaGrow, height, width)

    if move:
        return move
    else:
        neighbours = get_neighbors((head_x, head_y), grid_options[0], height, width)
        if neighbours:
            return get_direction((head_x, head_y), neighbours[0])
        else:
            return 'left'