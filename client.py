import pickle
import pygame
import pygame.freetype as freetype
import socket

import config as conf
from pong import GameState, Edges, Paddle, Ball, redrawWindow


def main():
    # Initialize pygame stuff
    pygame.init()
    window = pygame.display.set_mode((conf.WINDOW_WIDTH, conf.WINDOW_HEIGHT))
    pygame.display.set_caption(conf.CAPTION)
    game_font = freetype.SysFont('arial', size=24)
    clock = pygame.time.Clock()

    # Connected to the server and receive initial game state
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((conf.ADDRESS, conf.PORT))
    player = pickle.loads(server.recv(2048))
    print(f"Connected as player {player}")
    game_state: GameState = pickle.loads(server.recv(2048))

    # Set up window edges, paddles, and ball
    edges = Edges(bottom=conf.WINDOW_HEIGHT, top=0, left=0, right=conf.WINDOW_WIDTH)
    left_paddle = Paddle(game_state.left_paddle_pos[0], game_state.left_paddle_pos[1], conf.PADDLE_WIDTH,
                         conf.PADDLE_HEIGHT, conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)
    right_paddle = Paddle(game_state.right_paddle_pos[0], game_state.right_paddle_pos[1], conf.PADDLE_WIDTH,
                          conf.PADDLE_HEIGHT, conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)
    ball = Ball(conf.WINDOW_WIDTH / 2, conf.WINDOW_HEIGHT / 2, conf.BALL_RADIUS, None, None, edges,
                color=conf.BALL_COLOR)

    run = True
    while run:
        clock.tick(conf.FRAMERATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # Move paddle on the client side, send paddle position to server, and receive game state
        if player == 1:
            left_paddle.move()
            server.sendall(pickle.dumps((left_paddle.x, left_paddle.y)))
            reply = server.recv(2048)
        elif player == 2:
            right_paddle.move()
            server.sendall(pickle.dumps((right_paddle.x, right_paddle.y)))
            reply = server.recv(2048)
        else:
            reply = None

        # Update game state on client side
        game_state = pickle.loads(reply)
        (ball.x, ball.y) = game_state.ball_pos
        (left_paddle.x, left_paddle.y) = game_state.left_paddle_pos
        (right_paddle.x, right_paddle.y) = game_state.right_paddle_pos
        left_paddle.score = game_state.left_score
        right_paddle.score = game_state.right_score

        # Draw updated client side state
        redrawWindow(window, ball, left_paddle, right_paddle, game_font, conf.WINDOW_COLOR)


if __name__ == '__main__':
    main()
