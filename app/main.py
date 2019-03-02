import json, os, bottle, controller
from controller import log_it
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
    log_it("=====BEGIN MOVE=====")
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

    log_it("=====TURN====\n" + str(data['turn']) + "=====TURN=====\n")

    # generate a board and add enemy snakes to it (should I add my body as well?)
    board = controller.setup_board(height, width, snakes, myID)
    log_it('====BOARD====\n')
    log_it(board)
    log_it('\n====END BOARD====\n')

    # calculate next move

    next_move = controller.check_direction(board, height, width, mySnake[0], mySnake[-1], health, next_move)
    log_it("\n=====MOVE=====\n")
    log_it(next_move)

    # NOTE create override for when the snake backtracks on itself
    # ie down then next turn does up

    # NOTE create a final check to ensure that if the snake does die that there
    # were no valid moves still left

    if debug:
        end = timer()
        print("RUNTIME: {0}ms. MAX 200ms, currently using {1}%".format(((end - start) * 1000),(((end - start) * 1000) / 2)))

    log_it("\n=====END MOVE=====\n")
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
