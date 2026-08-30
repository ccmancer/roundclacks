import pygame
import random

from game.asset_helper import load_image


HEALTH_FONT = pygame.font.Font(
    None,
    24
)


class Player:
    def __init__(
        self,
        game,
        x,
        y,
        radius,
        color,
        speed,
        weapon_class,
        attack_key,
        name="Player",
        player_number=None
    ):
        self.game = game

        # -------------------------------------------------
        # Network identity
        # -------------------------------------------------

        self.player_number = player_number

        # -------------------------------------------------
        # Position
        # -------------------------------------------------

        self.position = pygame.Vector2(
            x,
            y
        )

        self.radius = radius
        self.color = color
        self.name = name
        self.speed = speed

        # -------------------------------------------------
        # Simulation
        # -------------------------------------------------

        self.simulation_frame = 0

        # -------------------------------------------------
        # Sprite / Sound
        # -------------------------------------------------

        self.sprite = load_image(
            "sprites",
            "game",
            "player.png"
        )

        self.hurt_sound = (
            self.game.audio.load_game_sound(
                "hurt.mp3"
            )
        )

        self.hurt_sound_timer = 0
        self.hurt_sound_cooldown = 0.1

        # -------------------------------------------------
        # Weapon
        # -------------------------------------------------

        self.weapon = weapon_class(
            self
        )

        self.attack_key = attack_key

        # -------------------------------------------------
        # Health
        # -------------------------------------------------

        self.base_max_health = 100

        self.max_health = (
            self.get_max_health()
        )

        self.health = self.max_health

        # -------------------------------------------------
        # Movement
        # -------------------------------------------------

        self.reset_velocity(
            speed
        )

        self.external_velocity = (
            pygame.Vector2()
        )

        self.external_velocity_timer = 0

        # -------------------------------------------------
        # Status Effects
        # -------------------------------------------------

        self.pinned_arrows = []
        self.shellshock_timer = 0

        # -------------------------------------------------
        # Damage Flash
        # -------------------------------------------------

        self.damage_flash_timer = 0
        self.damage_flash_duration = 0.5

    # -------------------------------------------------
    # UPDATE / DRAW
    # -------------------------------------------------

    def update(
        self,
        dt,
        width,
        height
    ):
        """
        Update non-collision player state.

        Movement is performed with deterministic substeps so
        very high movement speeds do not jump huge distances
        in one simulation step.

        Player-vs-player collision is handled by RoundState,
        which moves both players together and resolves their
        collision after every substep.
        """

        if self.hurt_sound_timer > 0:

            self.hurt_sound_timer -= dt

            if self.hurt_sound_timer < 0:
                self.hurt_sound_timer = 0

        if self.damage_flash_timer > 0:

            self.damage_flash_timer -= dt

            if self.damage_flash_timer < 0:
                self.damage_flash_timer = 0

        # -------------------------------------------------
        # Movement
        # -------------------------------------------------
        #
        # RoundState normally calls move_substeps() for the
        # two-player simulation. This fallback keeps Player
        # itself safe if update() is called elsewhere.
        # -------------------------------------------------

        self.move_substeps(
            dt,
            width,
            height
        )

        # -------------------------------------------------
        # Shellshock
        # -------------------------------------------------

        if self.shellshock_timer > 0:

            self.shellshock_timer -= dt

            if self.shellshock_timer < 0:
                self.shellshock_timer = 0

        # -------------------------------------------------
        # External movement
        # -------------------------------------------------

        if self.external_velocity_timer > 0:

            self.external_velocity_timer -= dt

        else:

            self.external_velocity = (
                pygame.Vector2()
            )

        # -------------------------------------------------
        # Weapon
        # -------------------------------------------------

        self.weapon.handle_player_bounds(
            width,
            height
        )

        self.weapon.update(
            dt
        )

    # -------------------------------------------------
    # MOVEMENT SUBSTEPS
    # -------------------------------------------------

    def get_movement_substeps(
        self,
        dt
    ):
        """
        Determine how many deterministic movement steps are
        needed for this player during one simulation frame.

        The maximum distance per substep is intentionally
        fixed and independent of frame rate.

        This is not a speed cap.
        """

        movement_velocity = (
            self.velocity
            + self.external_velocity
        )

        distance = (
            movement_velocity.length()
            * dt
        )

        # Keep individual movement chunks reasonably small.
        max_distance_per_step = 8.0

        steps = max(
            1,
            int(
                distance
                / max_distance_per_step
            ) + 1
        )

        # Prevent pathological CPU usage while still allowing
        # extremely fast gameplay.
        return min(
            steps,
            64
        )

    def move_substeps(
        self,
        dt,
        width,
        height
    ):
        """
        Move this player using deterministic substeps.

        Player-vs-player collision is intentionally NOT handled
        here because the collision system needs both players
        simultaneously.
        """

        steps = self.get_movement_substeps(
            dt
        )

        sub_dt = (
            dt / steps
        )

        for _ in range(
            steps
        ):

            # Keep the current velocity normalized to the
            # player's current gameplay speed.
            if self.velocity.length_squared() > 0:

                self.velocity.scale_to_length(
                    self.get_speed()
                )

            self.position += (
                self.velocity
                + self.external_velocity
            ) * sub_dt

            self.weapon.handle_player_bounds(
                width,
                height
            )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        self.weapon.draw_before_player(
            screen
        )

        sprite = self.get_sprite()

        rect = sprite.get_rect(
            center=self.position
        )

        screen.blit(
            sprite,
            rect
        )

        health_text = HEALTH_FONT.render(
            str(round(self.health)),
            True,
            "black"
        )

        health_rect = health_text.get_rect(
            center=(
                self.position.x,
                self.position.y
                - self.get_hitbox_radius()
                - 15
            )
        )

        screen.blit(
            health_text,
            health_rect
        )

        self.weapon.draw(
            screen
        )

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_sprite_size(
        self
    ):
        return (
            self.get_hitbox_radius() * 2
        )

    def get_sprite(
        self
    ):
        size = max(
            1,
            int(
                self.get_sprite_size()
            )
        )

        sprite = pygame.transform.scale(
            self.sprite,
            (
                size,
                size
            )
        )

        sprite = sprite.copy()

        sprite.fill(
            (
                self.color[0],
                self.color[1],
                self.color[2],
                255
            ),
            special_flags=pygame.BLEND_RGBA_MULT
        )

        if self.damage_flash_timer > 0:

            flash_strength = (
                self.damage_flash_timer
                / self.damage_flash_duration
            )

            amount = int(
                255
                * flash_strength
            )

            sprite.fill(
                (
                    amount,
                    amount,
                    amount
                ),
                special_flags=pygame.BLEND_RGB_ADD
            )

            return sprite

        return self.weapon.modify_player_sprite(
            sprite
        )

    # -------------------------------------------------
    # HEALTH
    # -------------------------------------------------

    def take_damage(
        self,
        damage
    ):
        damage = (
            self.weapon.modify_incoming_damage(
                damage
            )
        )

        self.health -= damage

        self.damage_flash_timer = (
            self.damage_flash_duration
        )

        if self.hurt_sound_timer <= 0:

            self.hurt_sound.play()

            self.hurt_sound_timer = (
                self.hurt_sound_cooldown
            )

    def heal(
        self,
        amount
    ):
        self.health = min(
            self.health + amount,
            self.max_health
        )

    def is_alive(
        self
    ):
        return self.health > 0

    def get_health_ratio(
        self
    ):
        if self.max_health <= 0:

            return 0

        return max(
            0,
            self.health / self.max_health
        )

    # -------------------------------------------------
    # PLAYER STATS
    # -------------------------------------------------

    def get_max_health(
        self
    ):
        return (
            self.base_max_health
            * self.weapon.get_max_health_multiplier()
        )

    def get_hitbox_radius(
        self
    ):
        return (
            self.radius
            * self.weapon.get_radius_multiplier()
        )

    def get_speed(
        self
    ):
        speed = (
            self.speed
            * self.weapon.get_speed_multiplier()
        )

        for arrow in self.pinned_arrows:

            if arrow.is_pincushion_active_for(
                self
            ):

                speed *= (
                    arrow.get_pincushion_speed_multiplier()
                )

        if self.shellshock_timer > 0:

            speed *= 0.5

        return speed

    # -------------------------------------------------
    # MOVEMENT
    # -------------------------------------------------

    def reset_velocity(
        self,
        speed,
        rng=None
    ):
        if rng is None:
            rng = random

        # -------------------------------------------------
        # Deterministic netplay starting direction
        # -------------------------------------------------

        if (
            self.player_number in (
                1,
                2
            )
            and hasattr(
                rng,
                "randint"
            )
        ):

            angle = rng.randint(
                0,
                self.player_number,
                "starting_velocity",
                0,
                360
            )

        else:

            angle = rng.randint(
                0,
                360
            )

        self.velocity = pygame.Vector2()

        self.velocity.from_polar(
            (
                speed,
                angle
            )
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
            direction
            * force
        )

        self.external_velocity_timer = (
            duration
        )

    # -------------------------------------------------
    # STATUS EFFECTS
    # -------------------------------------------------

    def apply_shellshock(
        self,
        duration
    ):
        self.shellshock_timer = max(
            self.shellshock_timer,
            duration
        )

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(
        self,
        position,
        rng=None
    ):
        self.position = pygame.Vector2(
            position
        )

        self.max_health = (
            self.get_max_health()
        )

        self.health = self.max_health

        self.reset_velocity(
            self.speed,
            rng
        )

        self.external_velocity = (
            pygame.Vector2()
        )

        self.external_velocity_timer = 0

        self.shellshock_timer = 0

        self.pinned_arrows = []

        self.damage_flash_timer = 0
        self.hurt_sound_timer = 0

        self.weapon.reset(
            rng
        )