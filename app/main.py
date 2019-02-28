import json, os, bottle, controller

from timeit import default_timer as timer
from api import ping_response, start_response, move_response, end_response


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    color = "#420666"
    name = "Joel"
    headType = "pixel"
    tailType = "pixel"

    return start_response(color, name, headType, tailType)


@bottle.post('/move')
def move():
    debug = False
    data = bottle.request.json

    width = data['board']['width']
    height = data['board']['height']

    food = data['board']['food']
    snakes = data['board']['snakes']

    health = data['you']['health']
    mySnake = data['you']['body']
    myID = data['you']['id']

    if debug:
        start = timer()

    # generate a board and add enemy snakes to it (should I add my body as well?)
    board = brain.setup_board(height, width, snakes, mySnake, myID)

    # find the closest reachable piece of food
    food = controller.find_best_food(board, food, mySnake[0]['x'], mySnake[0]['y'])

    # calculate next move
    next_move = 'right'

    if debug:
        end = timer()
        print("RUNTIME: {0}ms. MAX 200ms, currently using {1}%".format(((end - start) * 1000),(((end - start) * 1000) / 2)))


    return move_response(next_move)


@bottle.post('/end')
def end():
    data = bottle.request.json

    return end_response()


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
