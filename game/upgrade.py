class Upgrade:
    def __init__(
        self,
        name,
        rarity,
        description,
        damage_multiplier=1,
        projectile_speed_multiplier=1,
        cooldown_multiplier=1
    ):
        self.name = name
        self.rarity = rarity
        self.description = description

        self.damage_multiplier = damage_multiplier
        self.projectile_speed_multiplier = projectile_speed_multiplier
        self.cooldown_multiplier = cooldown_multiplier

        