import pygame
import random
from entities.gun import Gun


class Player:
    def __init__(self, x, y, radius, color, speed):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.speed = speed
        self.health = 100

        self.reset_velocity(speed)

        self.weapon = Gun(self)

    def update(self, dt, width, height):
        self.position += self.velocity * dt

        # Left wall
        if self.position.x - self.radius <= 0 and self.velocity.x < 0:
            self.position.x = self.radius
            self.velocity.x *= -1

        # Right wall
        elif self.position.x + self.radius >= width and self.velocity.x > 0:
            self.position.x = width - self.radius
            self.velocity.x *= -1

        # Top wall
        if self.position.y - self.radius <= 0 and self.velocity.y < 0:
            self.position.y = self.radius
            self.velocity.y *= -1

        # Bottom wall
        elif self.position.y + self.radius >= height and self.velocity.y > 0:
            self.position.y = height - self.radius
            self.velocity.y *= -1

        self.weapon.update(dt)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            self.radius
        )

        self.weapon.draw(screen)

    def take_damage(self, damage):
        self.health -= damage

    def is_alive(self):
        return self.health > 0

    def reset(self, position):
        self.position = pygame.Vector2(position)
        self.health = 100
        self.reset_velocity(self.speed)

    def reset_velocity(self, speed):
        angle = random.randint(0, 360)

        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))