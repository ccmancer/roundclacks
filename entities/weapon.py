import pygame
import math

class Weapon:
    def __init__(self, player, distance, rotation_speed):
        self.player = player
        self.distance = distance
        self.rotation_speed = rotation_speed
        self.angle = 0
        self.position = pygame.Vector2()
    def update(self, dt):
        self.angle += self.rotation_speed * dt
        self.position.x = (
            self.player.position.x
            + math.cos(self.angle) * self.distance
        )
        self.position.y = (
            self.player.position.y
            + math.sin(self.angle) * self.distance
        )
        self.direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "black",
            self.position,
            10
        )