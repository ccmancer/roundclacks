import pygame
import math
from entities.bullet import Bullet

class Weapon:
    def __init__(self, player, distance, rotation_speed):
        self.player = player
        self.distance = distance
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.position = pygame.Vector2()
    def update(self, dt):
        self.angle += self.rotation_speed * dt
        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )
        self.position = (
            self.player.position
            + self.direction * self.distance
        )
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "black",
            self.position,
            10
        )
    def attack(self):
        return Bullet(
            self.position,
            self.direction,
            600,
            8,
            self.player.color
        )