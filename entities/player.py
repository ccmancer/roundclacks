import pygame
import random

from weapons.sword import Sword
from weapons.bow import Bow

class Player:
    def __init__(self, x, y, radius, color, speed):
        self.position = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.speed = speed

        self.weapon = Bow(self)

        self.base_max_health = 100
        self.max_health = self.get_max_health()
        self.health = self.max_health

        self.reset_velocity(speed)

        # Temporary movement caused by external effects
        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

    def update(self, dt, width, height):
        # Apply normal movement + temporary external movement
        if self.velocity.length_squared() > 0:
            self.velocity.scale_to_length(self.get_speed())

        self.position += (self.velocity + self.external_velocity) * dt

        # Handle temporary external movement
        if self.external_velocity_timer > 0:
            self.external_velocity_timer -= dt
        else:
            self.external_velocity = pygame.Vector2()

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
            self.get_radius()
        )

        self.weapon.draw(screen)

    def take_damage(self, damage):
        self.health -= damage

    def heal(self, amount):
        self.health = min(
            self.health + amount,
            self.max_health
        )

    def is_alive(self):
        return self.health > 0
    
    def reset(self, position):
        self.position = pygame.Vector2(position)

        self.max_health = self.get_max_health()
        self.health = self.max_health

        self.reset_velocity(self.speed)
        self.weapon.reset()

        # Clear any temporary movement effects
        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

    def reset_velocity(self, speed):
        angle = random.randint(0, 360)

        self.velocity = pygame.Vector2()
        self.velocity.from_polar((speed, angle))

    def apply_force(self, direction, force, duration):
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.external_velocity = direction * force
        self.external_velocity_timer = duration

    def get_max_health(self):
        health = self.base_max_health

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Armor":
                health *= 1.25 ** upgrade.stacks

            elif upgrade.name == "Juggernaut":
                health *= 2 ** upgrade.stacks

        return health

    def get_radius(self):
        radius = self.radius

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Juggernaut":
                radius *= 1.5 ** upgrade.stacks

        return radius

    def get_speed(self):
        speed = self.speed

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Rage":
                missing_health = 1 - self.get_health_ratio()
                speed *= 1 + missing_health * upgrade.stacks * 2

        return speed

    def get_health_ratio(self):
        return max(0, self.health / self.max_health)