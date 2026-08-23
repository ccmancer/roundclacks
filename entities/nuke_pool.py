import pygame


class NukePool:
    def __init__(
        self,
        position,
        radius,
        damage,
        owner,
        duration=3.0,
        tick_interval=0.02
    ):
        self.position = pygame.Vector2(position)

        self.radius = radius
        self.damage = damage
        self.owner = owner

        self.duration = duration
        self.timer = duration

        self.tick_interval = tick_interval
        self.damage_timers = {}

        self.alive = True
        self.can_hit_owner = True

    def update(self, dt):
        self.timer -= dt

        if self.timer <= 0:
            self.alive = False
            return

        for player in list(
            self.damage_timers
        ):
            self.damage_timers[player] -= dt

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "green",
            self.position,
            int(self.radius)
        )

    def hit(self, player):
        if player not in self.damage_timers:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )

            return

        if self.damage_timers[player] <= 0:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )