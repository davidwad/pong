import concurrent.futures
import pickle
import pygame
import socket

import config as conf
from pong import GameState, Edges, Paddle, Ball, generate_start_velocity


game_state = GameState(
    ball_pos=(conf.WINDOW_WIDTH / 2, conf.WINDOW_HEIGHT / 2),
    left_paddle_pos=(conf.PADDLE_START_X, conf.PADDLE_START_Y),
    right_paddle_pos=(conf.WINDOW_WIDTH - conf.PADDLE_START_X, conf.PADDLE_START_Y),
    left_score=0,
    right_score=0
)


def client_connection(conn: socket.socket, player: int):
    # Send player number and initial game state when player connects to server
    global game_state
    conn.send(pickle.dumps(player))
    conn.send(pickle.dumps(game_state))

    # Wait for updated paddle positions from clients, update game state, and reply with game state
    while True:
        try:
            data = conn.recv(2048)
            if not data:
                print(f"Player {player} disconnected")
                break

            paddle_pos = pickle.loads(data)
            if player == 1:
                game_state.left_paddle_pos = paddle_pos
            elif player == 2:
                game_state.right_paddle_pos = paddle_pos

            conn.sendall(pickle.dumps(game_state))
        except Exception as e:
            print(e)
            break

    print(f"Lost connection to player {player}")
    conn.close()


def main():
    # Set up pygame stuff
    pygame.init()
    clock = pygame.time.Clock()

    # Listen for client connections
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((conf.ADDRESS, conf.PORT))
    s.listen(2)
    print("Waiting for a connection, Server Started")
    conn1, _ = s.accept()
    print("Player 1 connected")
    conn2, _ = s.accept()
    print("Player 2 connected")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start threads that handle communication with clients
        executor.submit(client_connection, conn=conn1, player=1)
        executor.submit(client_connection, conn=conn2, player=2)

        # Set up initial game state
        edges = Edges(bottom=conf.WINDOW_HEIGHT, top=0, left=0, right=conf.WINDOW_WIDTH)
        left_paddle = Paddle(conf.PADDLE_START_X, conf.PADDLE_START_Y, conf.PADDLE_WIDTH, conf.PADDLE_HEIGHT,
                             conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)
        right_paddle = Paddle(conf.WINDOW_WIDTH - conf.PADDLE_START_X, conf.PADDLE_START_Y, conf.PADDLE_WIDTH,
                              conf.PADDLE_HEIGHT, conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)
        (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
        ball = Ball(conf.WINDOW_WIDTH / 2, conf.WINDOW_HEIGHT / 2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                    color=conf.BALL_COLOR)

        run = True
        while run:
            clock.tick(conf.FRAMERATE)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

            # Update paddle positions in case a client moved their paddle
            (left_paddle.x, left_paddle.y) = game_state.left_paddle_pos
            (right_paddle.x, right_paddle.y) = game_state.right_paddle_pos

            # Move the ball and handle bounces with paddles and roof/floor
            ball.move(left_paddle, right_paddle)

            # If a ball hits a wall, reset the ball and update the score
            if ball.inside_left_wall():
                right_paddle.score += 1
                (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
                ball = Ball(conf.WINDOW_WIDTH/2, conf.WINDOW_HEIGHT/2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                            color=conf.BALL_COLOR)
                game_state.right_score += 1
            elif ball.inside_right_wall():
                left_paddle.score += 1
                (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
                ball = Ball(conf.WINDOW_WIDTH/2, conf.WINDOW_HEIGHT/2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                            color=conf.BALL_COLOR)
                game_state.left_score += 1

            # Update game state with the new ball position for the clients
            game_state.ball_pos = (ball.x, ball.y)


if __name__ == "__main__":
    main()
