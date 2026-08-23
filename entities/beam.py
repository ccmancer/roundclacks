import pygame


class Beam:
    def __init__(
        self,
        weapon,
        damage,
        duration,
        width,
        tick_interval,
        knockback,
        lifesteal,
        angle_offset=0
    ):
        self.weapon = weapon

        self.position = pygame.Vector2(
            weapon.position
        )

        self.direction = pygame.Vector2(
            weapon.direction
        ).rotate(angle_offset)

        self.angle_offset = angle_offset

        self.damage = damage

        self.duration = duration
        self.timer = duration

        self.width = width
        self.length = 2000

        self.tick_interval = tick_interval
        self.tick_timer = 0

        self.knockback = knockback
        self.lifesteal = lifesteal

        self.alive = True
        self.is_beam = True

        # Prevents the same player from being hit
        # more than once during one tick.
        self.hit_this_tick = set()

    def update(self, dt):
        self.timer -= dt

        # Follow the book.
        self.position = pygame.Vector2(
            self.weapon.position
        )

        self.direction = pygame.Vector2(
            self.weapon.direction
        ).rotate(
            self.angle_offset
        )

        if self.timer <= 0:
            self.alive = False
            return

        self.tick_timer -= dt

        if self.tick_timer <= 0:
            self.tick_timer = self.tick_interval

            self.hit_this_tick.clear()

    def draw(self, screen):
        perpendicular = pygame.Vector2(
            -self.direction.y,
            self.direction.x
        )

        half_width = self.width / 2

        start = self.position

        end = (
            self.position
            + self.direction * self.length
        )

        top_start = (
            start
            + perpendicular * half_width
        )

        bottom_start = (
            start
            - perpendicular * half_width
        )

        top_end = (
            end
            + perpendicular * half_width
        )

        bottom_end = (
            end
            - perpendicular * half_width
        )

        pygame.draw.polygon(
            screen,
            "purple",
            [
                top_start,
                top_end,
                bottom_end,
                bottom_start
            ]
        )

    def hit(self, player):
        if player in self.hit_this_tick:
            return []

        self.hit_this_tick.add(player)

        player.take_damage(
            self.damage
        )

        if self.lifesteal > 0:
            self.weapon.player.heal(
                self.damage * self.lifesteal
            )

        if self.knockback > 0:
            direction = (
                player.position
                - self.position
            )

            if direction.length_squared() > 0:
                self.weapon.player.apply_force(
                    direction,
                    self.knockback,
                    0.1
                )

        return []