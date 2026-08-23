import pygame
import random

HEALTH_FONT = pygame.font.Font(None, 24)


class Player:
    def __init__(
        self,
        x,
        y,
        radius,
        color,
        speed,
        weapon_class,
        attack_key
    ):
        self.position = pygame.Vector2(x, y)

        self.radius = radius
        self.color = color
        self.speed = speed

        self.weapon = weapon_class(self)
        self.attack_key = attack_key

        self.base_max_health = 100
        self.max_health = self.get_max_health()
        self.health = self.max_health

        self.reset_velocity(speed)

        # Arrows currently attached by Pincushion.
        self.pinned_arrows = []

        # Shellshock.
        self.shellshock_timer = 0

        # Temporary movement caused by external effects.
        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

        # Unarmed afterimages.
        self.afterimages = []
        self.afterimage_timer = 0
        self.afterimage_interval = 0.04

    def update(self, dt, width, height):
        # Apply normal movement + temporary external movement.
        if self.velocity.length_squared() > 0:
            self.velocity.scale_to_length(
                self.get_speed()
            )

        self.position += (
            self.velocity
            + self.external_velocity
        ) * dt

        # Shellshock.
        if self.shellshock_timer > 0:
            self.shellshock_timer -= dt

            if self.shellshock_timer < 0:
                self.shellshock_timer = 0

        # Temporary external movement.
        if self.external_velocity_timer > 0:
            self.external_velocity_timer -= dt
        else:
            self.external_velocity = pygame.Vector2()

        # Create afterimages while attacking.
        if (
            hasattr(
                self.weapon,
                "is_attacking"
            )
            and self.weapon.is_attacking()
        ):
            self.afterimage_timer -= dt

            if self.afterimage_timer <= 0:
                self.afterimages.append({
                    "position": self.position.copy(),
                    "radius": self.get_radius(),
                    "color": self.color,
                    "alpha": 140,
                    "timer": 0.18
                })

                self.afterimage_timer = (
                    self.afterimage_interval
                )
        else:
            self.afterimage_timer = 0

        # Update afterimages.
        for afterimage in self.afterimages:
            afterimage["timer"] -= dt

            afterimage["alpha"] = max(
                0,
                int(
                    140
                    * (
                        afterimage["timer"]
                        / 0.18
                    )
                )
            )

        self.afterimages = [
            afterimage
            for afterimage in self.afterimages
            if afterimage["timer"] > 0
        ]

        radius = self.get_radius()

        # Check whether PAC-MAN is active.
        pacman_active = (
            hasattr(
                self.weapon,
                "pacman_speed_stacks"
            )
            and hasattr(
                self.weapon,
                "is_attacking"
            )
            and self.weapon.is_attacking()
            and any(
                upgrade.name == "PAC-MAN"
                for upgrade in self.weapon.upgrades
            )
        )

        if pacman_active:
            wrapped = False

            # Left -> right.
            if self.position.x + radius < 0:
                self.position.x = (
                    width + radius
                )
                wrapped = True

            # Right -> left.
            elif self.position.x - radius > width:
                self.position.x = -radius
                wrapped = True

            # Top -> bottom.
            if self.position.y + radius < 0:
                self.position.y = (
                    height + radius
                )
                wrapped = True

            # Bottom -> top.
            elif self.position.y - radius > height:
                self.position.y = -radius
                wrapped = True

            if wrapped:
                self.weapon.pacman_speed_stacks += 1

        else:
            # Normal wall collisions.
            bounced = False

            # Left wall.
            if self.position.x - radius <= 0:
                self.position.x = radius

                if self.velocity.x < 0:
                    self.velocity.x *= -1
                    self.velocity.y += random.uniform(
                        -75,
                        75
                    )
                    bounced = True

                if self.external_velocity.x < 0:
                    self.external_velocity.x = 0

            # Right wall.
            elif self.position.x + radius >= width:
                self.position.x = width - radius

                if self.velocity.x > 0:
                    self.velocity.x *= -1
                    self.velocity.y += random.uniform(
                        -75,
                        75
                    )
                    bounced = True

                if self.external_velocity.x > 0:
                    self.external_velocity.x = 0

            # Top wall.
            if self.position.y - radius <= 0:
                self.position.y = radius

                if self.velocity.y < 0:
                    self.velocity.y *= -1
                    self.velocity.x += random.uniform(
                        -75,
                        75
                    )
                    bounced = True

                if self.external_velocity.y < 0:
                    self.external_velocity.y = 0

            # Bottom wall.
            elif self.position.y + radius >= height:
                self.position.y = height - radius

                if self.velocity.y > 0:
                    self.velocity.y *= -1
                    self.velocity.x += random.uniform(
                        -75,
                        75
                    )
                    bounced = True

                if self.external_velocity.y > 0:
                    self.external_velocity.y = 0

            # Preserve normal movement speed after bounce.
            if (
                bounced
                and self.velocity.length_squared() > 0
            ):
                self.velocity.scale_to_length(
                    self.get_speed()
                )

        self.weapon.update(dt)

    def draw(self, screen):
        # Draw afterimages first.
        for afterimage in self.afterimages:
            radius = afterimage["radius"]

            surface = pygame.Surface(
                (
                    radius * 2,
                    radius * 2
                ),
                pygame.SRCALPHA
            )

            color = pygame.Color(
                afterimage["color"]
            )

            pygame.draw.circle(
                surface,
                (
                    color.r,
                    color.g,
                    color.b,
                    afterimage["alpha"]
                ),
                (radius, radius),
                radius
            )

            screen.blit(
                surface,
                (
                    afterimage["position"].x - radius,
                    afterimage["position"].y - radius
                )
            )

        # Current player.
        radius = self.get_radius()

        pygame.draw.circle(
            screen,
            self.color,
            self.position,
            radius
        )

        # Health number.
        health_text = HEALTH_FONT.render(
            str(round(self.health)),
            True,
            "black"
        )

        health_rect = health_text.get_rect(
            center=(
                self.position.x,
                self.position.y - radius - 15
            )
        )

        screen.blit(
            health_text,
            health_rect
        )

        self.weapon.draw(screen)

    def take_damage(self, damage):
        # Unarmed Superarmor.
        if (
            hasattr(
                self.weapon,
                "is_attacking"
            )
            and self.weapon.is_attacking()
        ):
            for upgrade in self.weapon.upgrades:
                if upgrade.name == "Superarmor":
                    damage *= (
                        0.5 ** upgrade.stacks
                    )

        # Grimoire Magic Barrier.
        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Magic Barrier":
                if (
                    hasattr(
                        self.weapon,
                        "attack_slow_timer"
                    )
                    and self.weapon.attack_slow_timer > 0
                ):
                    damage *= (
                        0.1 ** upgrade.stacks
                    )

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

        # Clear temporary movement effects.
        self.external_velocity = pygame.Vector2()
        self.external_velocity_timer = 0

        # Shellshock.
        self.shellshock_timer = 0

        # Pincushion.
        self.pinned_arrows = []

        # Afterimages.
        self.afterimages = []
        self.afterimage_timer = 0

    def reset_velocity(self, speed):
        angle = random.randint(0, 360)

        self.velocity = pygame.Vector2()

        self.velocity.from_polar(
            (speed, angle)
        )

    def apply_force(
        self,
        direction,
        force,
        duration
    ):
        if direction.length_squared() == 0:
            return

        direction = direction.normalize()

        self.external_velocity = (
            direction * force
        )

        self.external_velocity_timer = duration

    def get_max_health(self):
        health = self.base_max_health

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Armor":
                health *= (
                    1.25 ** upgrade.stacks
                )

            elif upgrade.name == "Juggernaut":
                health *= (
                    2 ** upgrade.stacks
                )

            elif upgrade.name == "Light Armor":
                health *= (
                    1.1 ** upgrade.stacks
                )

            elif upgrade.name == "Brute":
                health *= (
                    1.5 ** upgrade.stacks
                )

        return health

    def get_radius(self):
        radius = self.radius

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Juggernaut":
                radius *= (
                    1.5 ** upgrade.stacks
                )

            elif upgrade.name == "Lightweight":
                radius *= (
                    0.75 ** upgrade.stacks
                )

        if hasattr(
            self.weapon,
            "get_radius_multiplier"
        ):
            radius *= (
                self.weapon.get_radius_multiplier()
            )

        return radius

    def get_speed(self):
        speed = self.speed

        for upgrade in self.weapon.upgrades:
            if upgrade.name == "Rage":
                missing_health = (
                    1
                    - self.get_health_ratio()
                )

                speed *= (
                    1
                    + missing_health
                    * upgrade.stacks
                    * 2
                )

            elif upgrade.name == "Light Armor":
                speed *= (
                    1.25 ** upgrade.stacks
                )

        # Pincushion.
        for arrow in self.pinned_arrows:
            speed *= 0.75

        # Shellshock.
        if self.shellshock_timer > 0:
            speed *= 0.5

        # Grimoire firing slowdown.
        if (
            hasattr(
                self.weapon,
                "attack_slow_timer"
            )
            and self.weapon.attack_slow_timer > 0
        ):
            speed *= 0.5

        # Unarmed attack speed.
        if hasattr(
            self.weapon,
            "get_speed_multiplier"
        ):
            speed *= (
                self.weapon.get_speed_multiplier()
            )

        return speed

    def get_health_ratio(self):
        return max(
            0,
            self.health / self.max_health
        )

    def apply_shellshock(self, duration):
        self.shellshock_timer = max(
            self.shellshock_timer,
            duration
        )