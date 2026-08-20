from entities.bullet import Bullet
from weapons.weapon import Weapon

from game.upgrade_pool import BOW_UPGRADES

class Bow(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            70,     # orbit distance
            3,      # rotation speed
            20,     # base damage
            0.5     # base cooldown
        )
        self.base_projectile_speed = 500
        self.upgrade_pool = BOW_UPGRADES

    def get_projectile_speed(self):
        speed = self.base_projectile_speed

        for upgrade in self.upgrades:
            speed *= upgrade.projectile_speed_multiplier

        return speed

    def attack(self):
        if not self.can_attack():
            return None

        self.start_cooldown()

        return Bullet(
            self.position,
            self.direction,
            self.get_projectile_speed(),
            8,
            self.player.color,
            self.player,
            self.get_damage()
        )

    def draw(self, screen):
        super().draw(screen)

        import pygame

        pygame.draw.circle(
            screen,
            "black",
            self.position,
            10
        )