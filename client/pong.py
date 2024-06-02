import math
import pygame
import random
from dataclasses import dataclass
import pygame.freetype as freetype

import config as conf


@dataclass
class Edges:
    bottom: int
    top: int
    left: int
    right: int


class Paddle:
    def __init__(self, x: int, y: int, width: int, height: int, speed: int, edges: Edges, color: tuple[int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.edges = edges
        self.color = color
        self.score = 0

    def draw(self, window: pygame.Surface):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and self.y >= self.edges.top:
            self.y -= self.speed

        if keys[pygame.K_DOWN] and self.y <= self.edges.bottom - self.height:
            self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self, x: int, y: int, radius: int, vel_x: int, vel_y: int, edges: Edges, color: tuple[int]):
        self.x = x
        self.y = y
        self.radius = radius
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.edges = edges
        self.color = color

    def draw(self, window: pygame.Surface):
        pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

    def move(self, left_paddle: Paddle, right_paddle: Paddle):
        self.x += self.vel_x
        self.y += self.vel_y

        if self.inside_floor() or self.inside_roof():
            self.vel_y = -self.vel_y

        if self.inside_left_wall() or self.inside_right_wall():
            self.vel_x = -self.vel_x
        elif self.inside_paddle(left_paddle) or self.inside_paddle(right_paddle):
            self.vel_x = -self.vel_x

    def inside_floor(self) -> bool:
        return self.y >= self.edges.bottom

    def inside_roof(self) -> bool:
        return self.y <= self.edges.top

    def inside_left_wall(self) -> bool:
        return self.x <= self.edges.left

    def inside_right_wall(self) -> bool:
        return self.x >= self.edges.right

    def inside_paddle(self, paddle: Paddle) -> bool:
        if paddle.get_rect().collidepoint(self.x, self.y):
            return True
        return False


def redrawWindow(window: pygame.Surface, ball: Ball, paddle_left: Paddle, paddle_right: Paddle, font: freetype.Font,
                 window_color: tuple[int]):
    window.fill(window_color)
    paddle_left.draw(window)
    paddle_right.draw(window)
    ball.draw(window)
    font.render_to(window, (20, 20), f"Score: {paddle_left.score}", (255, 255, 255))
    font.render_to(window, (window.get_width() - 100, 20), f"Score: {paddle_right.score}", (255, 255, 255))
    pygame.display.update()


def generate_start_velocity(max_angle: int, speed: float) -> tuple[int]:
    """
    The ball starts moving from the center of the window at a random angle
    between -30 and 30 or between 150 and 210 degrees

    Returns:
        tuple[int]: Magnitudes of the x- and y-components of the velocity vector
    """
    angle = random.uniform(-max_angle * math.pi / 180, max_angle * math.pi / 180)
    vel_x = math.cos(angle) * speed
    vel_y = math.sin(angle) * speed
    direction = random.choice([-1, 1])
    vel_x *= direction
    return (vel_x, vel_y)


def main():
    pygame.init()
    window = pygame.display.set_mode((conf.WINDOW_WIDTH, conf.WINDOW_HEIGHT))
    pygame.display.set_caption(conf.CAPTION)
    game_font = freetype.SysFont('arial', size=24)
    run = True

    edges = Edges(bottom=conf.WINDOW_HEIGHT, top=0, left=0, right=conf.WINDOW_WIDTH)

    left_paddle = Paddle(conf.PADDLE_START_X, conf.PADDLE_START_Y, conf.PADDLE_WIDTH, conf.PADDLE_HEIGHT,
                         conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)

    right_paddle = Paddle(conf.WINDOW_WIDTH - conf.PADDLE_START_X, conf.PADDLE_START_Y, conf.PADDLE_WIDTH,
                          conf.PADDLE_HEIGHT, conf.PADDLE_SPEED, edges, conf.PADDLE_COLOR)

    (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
    ball = Ball(conf.WINDOW_WIDTH / 2, conf.WINDOW_HEIGHT / 2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                color=conf.BALL_COLOR)

    clock = pygame.time.Clock()

    while run:
        clock.tick(conf.FRAMERATE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        left_paddle.move()
        right_paddle.move()
        ball.move(left_paddle, right_paddle)
        if ball.inside_left_wall():
            right_paddle.score += 1
            (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
            ball = Ball(conf.WINDOW_WIDTH/2, conf.WINDOW_HEIGHT/2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                        color=conf.BALL_COLOR)
        elif ball.inside_right_wall():
            left_paddle.score += 1
            (vel_x, vel_y) = generate_start_velocity(conf.BALL_MAX_START_ANGLE, conf.BALL_SPEED)
            ball = Ball(conf.WINDOW_WIDTH/2, conf.WINDOW_HEIGHT/2, conf.BALL_RADIUS, vel_x, vel_y, edges,
                        color=conf.BALL_COLOR)

        redrawWindow(window, ball, left_paddle, right_paddle, game_font, conf.WINDOW_COLOR)


if __name__ == '__main__':
    main()
