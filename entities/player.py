import pygame
import random
from entities.weapon import Weapon

class Player:
    def __init__(self, x, y, radius, color, speed):
        self.position = pygame.Vector2(x, y)
        angle = random.randint(0, 360)
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))
        self.radius = radius
        self.color = color
        self.health = 100
        self.weapon = Weapon(
            self,
            70,
            3
        )       
    def update(self, dt, width, height):
        self.position += self.velocity * dt
        if self.position.x - self.radius <= 0 and self.velocity.x < 0:
            self.position.x = self.radius
            self.velocity.x *= -1
        elif self.position.x + self.radius >= width and self.velocity.x > 0:
            self.position.x = width - self.radius
            self.velocity.x *= -1
        if self.position.y - self.radius <= 0 and self.velocity.y < 0:
            self.position.y = self.radius
            self.velocity.y *= -1
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