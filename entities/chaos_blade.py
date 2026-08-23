import pygame


class ChaosBlade:
    def __init__(
        self,
        position,
        direction,
        max_distance,
        damage,
        owner,
        size,
        duration=1.5,
        rotation_speed=720,
        outward_speed=250
    ):
        self.center = pygame.Vector2(position)

        self.direction = pygame.Vector2(direction)

        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        self.distance = 0
        self.max_distance = max_distance

        self.damage = damage
        self.owner = owner
        self.size = size

        self.duration = duration
        self.timer = duration

        self.rotation_speed = rotation_speed
        self.outward_speed = outward_speed

        self.alive = True
        self.can_hit_owner = False

        self.hit_players = set()

        self.radius = max(
            5,
            self.size * 0.4
        )

        self.position = self.center.copy()

        # Movement phases
        self.phase = "outward"

        self.outward_time = (
            self.max_distance
            / self.outward_speed
        )

        self.pause_time = 0.5
        self.return_time = 0.35

        self.phase_timer = self.outward_time

        self.return_speed = (
            self.max_distance
            / self.return_time
        )

    def update(self, dt):
        if not self.alive:
            return

        self.timer -= dt

        if self.timer <= 0:
            self.alive = False
            return

        # Keep spinning throughout the entire motion.
        self.direction = self.direction.rotate(
            self.rotation_speed * dt
        )

        # -------------------------
        # Fly outward
        # -------------------------
        if self.phase == "outward":
            self.distance += (
                self.outward_speed * dt
            )

            if self.distance >= self.max_distance:
                self.distance = self.max_distance
                self.phase = "pause"
                self.phase_timer = self.pause_time

        # -------------------------
        # Pause at the outside
        # -------------------------
        elif self.phase == "pause":
            self.phase_timer -= dt

            if self.phase_timer <= 0:
                self.phase = "return"

        # -------------------------
        # Return inward
        # -------------------------
        elif self.phase == "return":
            self.distance -= (
                self.return_speed * dt
            )

            if self.distance <= 0:
                self.distance = 0
                self.alive = False

        self.position = (
            self.center
            + self.direction * self.distance
        )

    def draw(self, screen):
        perpendicular = pygame.Vector2(
            -self.direction.y,
            self.direction.x
        )

        length = self.size

        tip = (
            self.position
            + self.direction * length
        )

        left = (
            self.position
            - self.direction * length * 0.5
            + perpendicular * length * 0.5
        )

        right = (
            self.position
            - self.direction * length * 0.5
            - perpendicular * length * 0.5
        )

        pygame.draw.polygon(
            screen,
            "purple",
            [
                tip,
                left,
                right
            ]
        )

    def hit(self, player):
        if player in self.hit_players:
            return []

        self.hit_players.add(player)

        player.take_damage(
            self.damage
        )

        return []