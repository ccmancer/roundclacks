import pygame


class FirePatch:
    def __init__(
        self,
        position,
        damage,
        owner,
        radius=20,
        duration=0.5,
        tick_interval=0.1
    ):
        self.position = pygame.Vector2(
            position
        )

        self.damage = damage
        self.owner = owner

        self.radius = radius

        self.duration = duration
        self.timer = duration

        self.tick_interval = tick_interval
        self.damage_timers = {}

        self.alive = True

        # Used by collision handling.
        self.can_hit_owner = False
        self.is_fire_patch = True

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
        fade = max(
            0,
            self.timer / self.duration
        )

        outer_alpha = int(
            160 * fade
        )

        inner_alpha = int(
            220 * fade
        )

        surface_size = max(
            1,
            int(self.radius * 2)
        )

        surface = pygame.Surface(
            (
                surface_size,
                surface_size
            ),
            pygame.SRCALPHA
        )

        center = (
            self.radius,
            self.radius
        )

        pygame.draw.circle(
            surface,
            (
                255,
                100,
                0,
                outer_alpha
            ),
            center,
            int(self.radius)
        )

        pygame.draw.circle(
            surface,
            (
                255,
                220,
                0,
                inner_alpha
            ),
            center,
            int(self.radius * 0.6)
        )

        screen.blit(
            surface,
            (
                self.position.x
                - self.radius,
                self.position.y
                - self.radius
            )
        )

    def hit(self, player):
        # Fire cannot damage its owner.
        if player == self.owner:
            return []

        # First hit is immediate.
        if player not in self.damage_timers:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )

            return []

        # Subsequent hits happen at the tick rate.
        if self.damage_timers[player] <= 0:
            player.take_damage(
                self.damage
            )

            self.damage_timers[player] = (
                self.tick_interval
            )

        return []