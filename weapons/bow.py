import pygame

from weapons.weapon import Weapon
from entities.arrow import Arrow
from game.upgrade_pool import BOW_UPGRADES


class Bow(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            50,    # orbit distance
            3,      # rotation speed
            25,     # base damage
            0.75    # base cooldown
        )

        self.upgrade_pool = BOW_UPGRADES

    def draw(self, screen):
        direction = self.direction.normalize()

        # Perpendicular to the bow direction
        perpendicular = pygame.Vector2(
            -direction.y,
            direction.x
        )

        # Bow dimensions
        bow_length = 70
        bow_curve = 20

        center = self.position

        # Endpoints of the bow
        top = center + perpendicular * (bow_length / 2)
        bottom = center - perpendicular * (bow_length / 2)

        # Bow curves away from the firing direction
        curve = center + direction * bow_curve

        # Draw the curved bow using several line segments
        points = []

        for i in range(11):
            t = i / 10

            point = (
                (1 - t) ** 2 * top
                + 2 * (1 - t) * t * curve
                + t ** 2 * bottom
            )

            points.append(point)

        pygame.draw.lines(
            screen,
            "brown",
            False,
            points,
            8
        )

        # Draw the bow string
        pygame.draw.line(
            screen,
            "black",
            top,
            bottom,
            2
        )

    def attack(self):
        if not self.can_attack():
            return []

        self.start_cooldown()

        return [
            Arrow(
                self.position,
                self.direction,
                self.get_damage(),
                self.player,
                self.get_projectile_speed()
            )
        ]

    def get_projectile_speed(self):
        speed = 500

        for upgrade in self.upgrades:
            if upgrade.name == "Aerodynamic":
                speed *= 2 ** upgrade.stacks

        return speed