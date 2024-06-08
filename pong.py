import math
import pygame
import pygame.freetype as freetype
import random
from dataclasses import dataclass


@dataclass
class GameState:
    ball_pos: tuple[int]
    left_paddle_pos: tuple[int]
    right_paddle_pos: tuple[int]
    left_score: int
    right_score: int


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
