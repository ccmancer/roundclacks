from entities.weapon import Weapon
from entities.bullet import Bullet
from game.upgrade import Upgrade


class Gun(Weapon):
    def __init__(self, player):
        super().__init__(
            player,
            70,     # orbit distance
            3,      # rotation speed
            20,     # base damage
            0.5     # base cooldown
        )

        self.base_projectile_speed = 500

        self.upgrade_pool = [
            Upgrade(
                "Heavy Bullets",
                "common",
                "+25% projectile damage",
                damage_multiplier=1.25
            ),

            Upgrade(
                "Fast Projectiles",
                "common",
                "+30% projectile speed",
                projectile_speed_multiplier=1.30
            ),

            Upgrade(
                "Rapid Fire",
                "rare",
                "-25% attack cooldown",
                cooldown_multiplier=0.75
            ),

            Upgrade(
                "Ricochet",
                "rare",
                "Projectiles bounce off walls once"
            ),

            Upgrade(
                "Explosive Rounds",
                "super rare",
                "Projectiles explode on impact"
            )
        ]

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