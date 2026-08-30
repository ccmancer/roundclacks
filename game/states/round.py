import pygame
import colorsys

from game.states.state import State

from network.input import FrameInput

from physics.collision import (
    check_circle_collision,
    resolve_circle_collision,
    check_sword_player_collision,
    check_projectile_player_collision,
    check_beam_player_collision
)

from weapons.unarmed import Unarmed

from ui.upgrade_card import UpgradeCard


class RoundState(State):

    def __init__(
        self,
        match_state
    ):
        super().__init__(
            match_state.game
        )

        self.is_simulation_state = True

        self.match_state = match_state

        self.player1 = match_state.player1
        self.player2 = match_state.player2

        self.projectiles = []

        # -------------------------------------------------
        # Simulation frame
        # -------------------------------------------------

        self.simulation_frame = 0

        self.player1.simulation_frame = 0
        self.player2.simulation_frame = 0

        # -------------------------------------------------
        # Local input state
        # -------------------------------------------------

        self.player1_attack_held = False
        self.player2_attack_held = False

        # -------------------------------------------------
        # Input history
        # -------------------------------------------------

        self.input_history = {}

        # -------------------------------------------------
        # Collision contact
        # -------------------------------------------------
        #
        # True when the two players touched at any point
        # during the current simulation frame.
        #
        # This is important for Unarmed because high-speed
        # substepping may resolve the players apart before
        # the normal weapon-collision check occurs.
        # -------------------------------------------------

        self.player_collision_contact = False

        # -------------------------------------------------
        # Reset players
        # -------------------------------------------------

        match_rng = (
            self.match_state.match.rng
        )

        self.player1.reset(
            (150, 360),
            match_rng
        )

        self.player2.reset(
            (570, 360),
            match_rng
        )

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        self.background_time = 0

        # -------------------------------------------------
        # Upgrade HUD
        # -------------------------------------------------

        self.player1_upgrade_cards = [
            UpgradeCard(
                upgrade,
                (
                    10
                    + i * (
                        UpgradeCard.MINI_SIZE
                        + UpgradeCard.MINI_GAP
                    ),
                    42
                ),
                expand_direction="right"
            )
            for i, upgrade in enumerate(
                self.player1.weapon.upgrades
            )
        ]

        self.player2_upgrade_cards = [
            UpgradeCard(
                upgrade,
                expand_direction="left"
            )
            for upgrade in self.player2.weapon.upgrades
        ]

        self.update_player2_upgrade_positions()

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == self.player1.attack_key:

                    self.player1_attack_held = True

                elif event.key == self.player2.attack_key:

                    self.player2_attack_held = True

                elif event.key == pygame.K_ESCAPE:

                    self.game.running = False

            elif event.type == pygame.KEYUP:

                if event.key == self.player1.attack_key:

                    self.player1_attack_held = False

                elif event.key == self.player2.attack_key:

                    self.player2_attack_held = False

    # -------------------------------------------------
    # LOCAL INPUT
    # -------------------------------------------------

    def get_local_inputs(
        self
    ):
        frame = (
            self.simulation_frame
            + 1
        )

        return (
            FrameInput(
                frame,
                self.player1_attack_held
            ),
            FrameInput(
                frame,
                self.player2_attack_held
            )
        )

    # -------------------------------------------------
    # INPUT HISTORY
    # -------------------------------------------------

    def get_inputs_for_frame(
        self,
        frame
    ):
        return self.input_history.get(
            frame,
            (
                FrameInput(
                    frame
                ),
                FrameInput(
                    frame
                )
            )
        )

    def store_inputs(
        self,
        player1_input,
        player2_input
    ):
        frame = (
            player1_input.frame
        )

        if (
            player2_input.frame
            != frame
        ):
            raise ValueError(
                "Player inputs must belong "
                "to the same frame."
            )

        self.input_history[
            frame
        ] = (
            player1_input,
            player2_input
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        player1_input, player2_input = (
            self.get_local_inputs()
        )

        self.simulate_frame(
            player1_input,
            player2_input,
            self.game.simulation_dt
        )

    # -------------------------------------------------
    # SIMULATION SUBSTEPS
    # -------------------------------------------------

    def get_simulation_substeps(
        self,
        dt
    ):
        distance1 = (
            (
                self.player1.velocity
                + self.player1.external_velocity
            ).length()
            * dt
        )

        distance2 = (
            (
                self.player2.velocity
                + self.player2.external_velocity
            ).length()
            * dt
        )

        maximum_distance = max(
            distance1,
            distance2
        )

        max_distance_per_step = 8.0

        steps = max(
            1,
            int(
                maximum_distance
                / max_distance_per_step
            ) + 1
        )

        return min(
            steps,
            64
        )

    def simulate_player_movement(
        self,
        dt,
        width,
        height
    ):
        steps = self.get_simulation_substeps(
            dt
        )

        sub_dt = (
            dt / steps
        )

        for _ in range(
            steps
        ):

            # -------------------------------------------------
            # Player 1
            # -------------------------------------------------

            if self.player1.velocity.length_squared() > 0:

                self.player1.velocity.scale_to_length(
                    self.player1.get_speed()
                )

            self.player1.position += (
                self.player1.velocity
                + self.player1.external_velocity
            ) * sub_dt

            self.player1.weapon.handle_player_bounds(
                width,
                height
            )

            # -------------------------------------------------
            # Player 2
            # -------------------------------------------------

            if self.player2.velocity.length_squared() > 0:

                self.player2.velocity.scale_to_length(
                    self.player2.get_speed()
                )

            self.player2.position += (
                self.player2.velocity
                + self.player2.external_velocity
            ) * sub_dt

            self.player2.weapon.handle_player_bounds(
                width,
                height
            )

            # -------------------------------------------------
            # Player collision
            # -------------------------------------------------

            self.resolve_player_collision()

    # -------------------------------------------------
    # PLAYER COLLISION
    # -------------------------------------------------

    def resolve_player_collision(
        self
    ):
        if check_circle_collision(
            self.player1,
            self.player2
        ):

            # Remember that contact happened during this
            # simulation frame BEFORE separating the players.
            self.player_collision_contact = True

            tunnel_active = (
                (
                    isinstance(
                        self.player1.weapon,
                        Unarmed
                    )
                    and self.player1.weapon.is_attacking()
                    and self.player1.weapon.is_tunnel_effect()
                )
                or
                (
                    isinstance(
                        self.player2.weapon,
                        Unarmed
                    )
                    and self.player2.weapon.is_attacking()
                    and self.player2.weapon.is_tunnel_effect()
                )
            )

            if not tunnel_active:

                resolve_circle_collision(
                    self.player1,
                    self.player2
                )

        else:

            if isinstance(
                self.player1.weapon,
                Unarmed
            ):

                if self.player1.weapon.is_tunnel_effect():

                    self.player1.weapon.on_tunnel_separation(
                        self.player2
                    )

            if isinstance(
                self.player2.weapon,
                Unarmed
            ):

                if self.player2.weapon.is_tunnel_effect():

                    self.player2.weapon.on_tunnel_separation(
                        self.player1
                    )

    # -------------------------------------------------
    # SIMULATE FRAME
    # -------------------------------------------------

    def simulate_frame(
        self,
        player1_input,
        player2_input,
        dt=None
    ):
        # -------------------------------------------------
        # Always fixed timestep
        # -------------------------------------------------

        dt = self.game.simulation_dt

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        expected_frame = (
            self.simulation_frame
            + 1
        )

        if (
            player1_input.frame
            != expected_frame
        ):
            raise ValueError(
                "Input frame does not match "
                "the next simulation frame."
            )

        if (
            player2_input.frame
            != expected_frame
        ):
            raise ValueError(
                "Input frame does not match "
                "the next simulation frame."
            )

        # -------------------------------------------------
        # Store inputs
        # -------------------------------------------------

        self.store_inputs(
            player1_input,
            player2_input
        )

        # -------------------------------------------------
        # Advance frame
        # -------------------------------------------------

        self.simulation_frame = (
            expected_frame
        )

        self.player1.simulation_frame = (
            self.simulation_frame
        )

        self.player2.simulation_frame = (
            self.simulation_frame
        )

        # -------------------------------------------------
        # Reset per-frame collision contact
        # -------------------------------------------------

        self.player_collision_contact = False

        width = (
            self.game.screen.get_width()
        )

        height = (
            self.game.screen.get_height()
        )

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        self.background_time += dt

        # -------------------------------------------------
        # Player timers
        # -------------------------------------------------

        self.update_player_timers(
            self.player1,
            dt
        )

        self.update_player_timers(
            self.player2,
            dt
        )

        # -------------------------------------------------
        # Player movement
        # -------------------------------------------------

        self.simulate_player_movement(
            dt,
            width,
            height
        )

        # -------------------------------------------------
        # External movement timers
        # -------------------------------------------------

        self.update_external_velocity(
            self.player1,
            dt
        )

        self.update_external_velocity(
            self.player2,
            dt
        )

        # -------------------------------------------------
        # Weapon update
        # -------------------------------------------------

        self.player1.weapon.update(
            dt
        )

        self.player2.weapon.update(
            dt
        )

        # -------------------------------------------------
        # Weapon-spawned entities
        # -------------------------------------------------

        if hasattr(
            self.player1.weapon,
            "spawned_entities"
        ):

            self.projectiles.extend(
                self.player1.weapon.spawned_entities
            )

            self.player1.weapon.spawned_entities.clear()

        if hasattr(
            self.player2.weapon,
            "spawned_entities"
        ):

            self.projectiles.extend(
                self.player2.weapon.spawned_entities
            )

            self.player2.weapon.spawned_entities.clear()

        # -------------------------------------------------
        # Weapon input
        # -------------------------------------------------

        self.handle_weapon_input(
            player1_input,
            player2_input,
            width,
            height
        )

        # -------------------------------------------------
        # Weapon collisions
        # -------------------------------------------------

        self.handle_weapon_collisions()

        # -------------------------------------------------
        # Projectiles
        # -------------------------------------------------

        self.update_projectiles(
            dt,
            width,
            height
        )

        self.handle_projectile_collisions()

        self.remove_dead_projectiles()

        # -------------------------------------------------
        # HUD
        # -------------------------------------------------

        self.update_upgrade_hud()

        # -------------------------------------------------
        # Round end
        # -------------------------------------------------

        self.check_round_end()

    # -------------------------------------------------
    # PLAYER TIMERS
    # -------------------------------------------------

    def update_player_timers(
        self,
        player,
        dt
    ):
        if player.hurt_sound_timer > 0:

            player.hurt_sound_timer -= dt

            if player.hurt_sound_timer < 0:

                player.hurt_sound_timer = 0

        if player.damage_flash_timer > 0:

            player.damage_flash_timer -= dt

            if player.damage_flash_timer < 0:

                player.damage_flash_timer = 0

        if player.shellshock_timer > 0:

            player.shellshock_timer -= dt

            if player.shellshock_timer < 0:

                player.shellshock_timer = 0

    def update_external_velocity(
        self,
        player,
        dt
    ):
        if player.external_velocity_timer > 0:

            player.external_velocity_timer -= dt

        else:

            player.external_velocity = (
                pygame.Vector2()
            )

    # -------------------------------------------------
    # BACKGROUND
    # -------------------------------------------------

    def get_background_color(
        self
    ):
        hue = (
            self.background_time
            / 12
        ) % 1

        rgb = colorsys.hsv_to_rgb(
            hue,
            0.25,
            1.0
        )

        return tuple(
            int(value * 255)
            for value in rgb
        )

    # -------------------------------------------------
    # UPGRADE HUD
    # -------------------------------------------------

    def update_upgrade_hud(
        self
    ):
        mouse_position = pygame.mouse.get_pos()

        hovered_card = None

        for card in self.player1_upgrade_cards:

            if card.get_mini_rect().collidepoint(
                mouse_position
            ):

                hovered_card = card
                break

        if hovered_card is None:

            for card in self.player2_upgrade_cards:

                if card.get_mini_rect().collidepoint(
                    mouse_position
                ):

                    hovered_card = card
                    break

        for card in self.player1_upgrade_cards:

            card.set_display_mode(
                "mini"
            )

            card.set_hovered(
                card is hovered_card
            )

        for card in self.player2_upgrade_cards:

            card.set_display_mode(
                "mini"
            )

            card.set_hovered(
                card is hovered_card
            )

        self.update_player2_upgrade_positions()

    def update_player2_upgrade_positions(
        self
    ):
        screen_width = (
            self.game.screen.get_width()
        )

        for i, card in enumerate(
            self.player2_upgrade_cards
        ):

            x = (
                screen_width
                - 10
                - UpgradeCard.MINI_SIZE
                - i * (
                    UpgradeCard.MINI_SIZE
                    + UpgradeCard.MINI_GAP
                )
            )

            card.set_position(
                (
                    x,
                    42
                )
            )

    # -------------------------------------------------
    # OUTLINED TEXT
    # -------------------------------------------------

    def draw_outlined_text(
        self,
        screen,
        text,
        font,
        position,
        color,
        outline_color=(0, 0, 0),
        outline_width=2
    ):
        outline = font.render(
            text,
            True,
            outline_color
        )

        foreground = font.render(
            text,
            True,
            color
        )

        x, y = position

        for dx in range(
            -outline_width,
            outline_width + 1
        ):

            for dy in range(
                -outline_width,
                outline_width + 1
            ):

                if dx == 0 and dy == 0:
                    continue

                screen.blit(
                    outline,
                    (
                        x + dx,
                        y + dy
                    )
                )

        screen.blit(
            foreground,
            position
        )

    # -------------------------------------------------
    # HUD
    # -------------------------------------------------

    def draw_upgrade_hud(
        self,
        screen
    ):
        font = pygame.font.Font(
            None,
            24
        )

        player1_name = (
            self.player1.name
        )

        player2_name = (
            self.player2.name
        )

        player1_text = font.render(
            player1_name,
            True,
            self.player1.color
        )

        player2_text = font.render(
            player2_name,
            True,
            self.player2.color
        )

        self.draw_outlined_text(
            screen,
            player1_name,
            font,
            (
                10,
                10
            ),
            self.player1.color
        )

        player2_rect = player2_text.get_rect(
            top=10,
            right=(
                screen.get_width()
                - 10
            )
        )

        self.draw_outlined_text(
            screen,
            player2_name,
            font,
            player2_rect.topleft,
            self.player2.color
        )

        # -------------------------------------------------
        # FT5
        # -------------------------------------------------

        ft5_font = pygame.font.Font(
            None,
            18
        )

        ft5_text = ft5_font.render(
            "FT5",
            True,
            (0, 0, 0)
        )

        ft5_rect = ft5_text.get_rect(
            center=(
                screen.get_width() // 2,
                14
            )
        )

        screen.blit(
            ft5_text,
            ft5_rect
        )

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        score_font = pygame.font.Font(
            None,
            44
        )

        player1_score = getattr(
            self.match_state.match,
            "player1_wins",
            0
        )

        player2_score = getattr(
            self.match_state.match,
            "player2_wins",
            0
        )

        score = score_font.render(
            f"{player1_score} - {player2_score}",
            True,
            (0, 0, 0)
        )

        score_rect = score.get_rect(
            center=(
                screen.get_width() // 2,
                38
            )
        )

        screen.blit(
            score,
            score_rect
        )

        # -------------------------------------------------
        # Upgrade cards
        # -------------------------------------------------

        player1_hovered = next(
            (
                card
                for card in self.player1_upgrade_cards
                if card.hovered
            ),
            None
        )

        player2_hovered = next(
            (
                card
                for card in self.player2_upgrade_cards
                if card.hovered
            ),
            None
        )

        if player1_hovered is not None:

            player1_hovered.draw(
                screen
            )

        else:

            for card in self.player1_upgrade_cards:

                card.draw(
                    screen
                )

        if player2_hovered is not None:

            player2_hovered.draw(
                screen
            )

        else:

            for card in self.player2_upgrade_cards:

                card.draw(
                    screen
                )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        screen.fill(
            self.get_background_color()
        )

        self.player1.draw(
            screen
        )

        self.player2.draw(
            screen
        )

        for projectile in self.projectiles:

            projectile.draw(
                screen
            )

        self.draw_upgrade_hud(
            screen
        )

    # -------------------------------------------------
    # ROUND END
    # -------------------------------------------------

    def check_round_end(
        self
    ):
        if getattr(
            self.match_state,
            "is_rollback_replaying",
            False
        ):
            return

        if not self.player1.is_alive():

            self.finish(
                self.player2,
                self.player1
            )

        elif not self.player2.is_alive():

            self.finish(
                self.player1,
                self.player2
            )

    def finish(
        self,
        winner,
        loser
    ):
        self.player1.weapon.on_death()
        self.player2.weapon.on_death()

        self.match_state.round_finished(
            winner,
            loser
        )

    # -------------------------------------------------
    # WEAPON INPUT
    # -------------------------------------------------

    def handle_weapon_input(
        self,
        player1_input,
        player2_input,
        width,
        height
    ):
        # -------------------------------------------------
        # Player 1
        # -------------------------------------------------

        if player1_input.attack:

            if isinstance(
                self.player1.weapon,
                Unarmed
            ):

                projectiles = (
                    self.player1.weapon.attack(
                        width,
                        height
                    )
                )

            else:

                projectiles = (
                    self.player1.weapon.attack()
                )

            if projectiles:

                self.projectiles.extend(
                    projectiles
                )

        # -------------------------------------------------
        # Player 2
        # -------------------------------------------------

        if player2_input.attack:

            if isinstance(
                self.player2.weapon,
                Unarmed
            ):

                projectiles = (
                    self.player2.weapon.attack(
                        width,
                        height
                    )
                )

            else:

                projectiles = (
                    self.player2.weapon.attack()
                )

            if projectiles:

                self.projectiles.extend(
                    projectiles
                )

    # -------------------------------------------------
    # PROJECTILES
    # -------------------------------------------------

    def update_projectiles(
        self,
        dt,
        width,
        height
    ):
        spawned_projectiles = []

        for projectile in self.projectiles:

            if not projectile.alive:
                continue

            if getattr(
                projectile,
                "cluster_child",
                False
            ):

                projectile.update(
                    dt
                )

                if projectile.should_explode:

                    results = (
                        projectile.explode()
                    )

                    if results:

                        spawned_projectiles.extend(
                            results
                        )

                continue

            projectile.update(
                dt
            )

            if hasattr(
                projectile,
                "get_spawned_entities"
            ):

                results = (
                    projectile.get_spawned_entities()
                )

                if results:

                    spawned_projectiles.extend(
                        results
                    )

            if getattr(
                projectile,
                "should_explode",
                False
            ):

                results = (
                    projectile.explode()
                )

                if results:

                    spawned_projectiles.extend(
                        results
                    )

                projectile.should_explode = False

                continue

            if hasattr(
                projectile,
                "handle_boundary_collision"
            ):

                projectile.handle_boundary_collision(
                    width,
                    height
                )

            elif hasattr(
                projectile,
                "is_out_of_bounds"
            ):

                if projectile.is_out_of_bounds(
                    width,
                    height
                ):

                    if getattr(
                        projectile,
                        "is_mine",
                        False
                    ):

                        projectile.stick_to_border(
                            width,
                            height
                        )

                    elif hasattr(
                        projectile,
                        "explode"
                    ):

                        results = (
                            projectile.explode()
                        )

                        if results:

                            spawned_projectiles.extend(
                                results
                            )

                    else:

                        projectile.alive = False

        self.projectiles.extend(
            spawned_projectiles
        )

    def remove_dead_projectiles(
        self
    ):
        self.projectiles = [
            projectile
            for projectile in self.projectiles
            if projectile.alive
        ]

    # -------------------------------------------------
    # WEAPON COLLISIONS
    # -------------------------------------------------

    def handle_weapon_collisions(
        self
    ):
        # -------------------------------------------------
        # Unarmed player 1
        # -------------------------------------------------

        if isinstance(
            self.player1.weapon,
            Unarmed
        ):

            weapon = self.player1.weapon

            contact = (
                self.player_collision_contact
            )

            touching = (
                contact
                or check_circle_collision(
                    self.player1,
                    self.player2
                )
            )

            if touching:

                if weapon.can_hit(
                    self.player2
                ):

                    weapon.hit(
                        self.player2
                    )

        # -------------------------------------------------
        # Other player 1 melee weapons
        # -------------------------------------------------

        elif self.player1.weapon.melee:

            weapon = self.player1.weapon

            if check_sword_player_collision(
                weapon,
                self.player2
            ):

                if weapon.can_hit():

                    weapon.hit(
                        self.player2
                    )

        # -------------------------------------------------
        # Unarmed player 2
        # -------------------------------------------------

        if isinstance(
            self.player2.weapon,
            Unarmed
        ):

            weapon = self.player2.weapon

            contact = (
                self.player_collision_contact
            )

            touching = (
                contact
                or check_circle_collision(
                    self.player1,
                    self.player2
                )
            )

            if touching:

                if weapon.can_hit(
                    self.player1
                ):

                    weapon.hit(
                        self.player1
                    )

        # -------------------------------------------------
        # Other player 2 melee weapons
        # -------------------------------------------------

        elif self.player2.weapon.melee:

            weapon = self.player2.weapon

            if check_sword_player_collision(
                weapon,
                self.player1
            ):

                if weapon.can_hit():

                    weapon.hit(
                        self.player1
                    )

    # -------------------------------------------------
    # PROJECTILE COLLISIONS
    # -------------------------------------------------

    def handle_projectile_collisions(
        self
    ):
        spawned_projectiles = []

        for projectile in self.projectiles:

            if not projectile.alive:
                continue

            if getattr(
                projectile,
                "stuck_to",
                None
            ) is not None:
                continue

            if getattr(
                projectile,
                "cluster_child",
                False
            ):
                continue

            if getattr(
                projectile,
                "is_fire_patch",
                False
            ):

                if check_projectile_player_collision(
                    projectile,
                    self.player1
                ):

                    results = projectile.hit(
                        self.player1
                    )

                    if results:

                        spawned_projectiles.extend(
                            results
                        )

                if check_projectile_player_collision(
                    projectile,
                    self.player2
                ):

                    results = projectile.hit(
                        self.player2
                    )

                    if results:

                        spawned_projectiles.extend(
                            results
                        )

                continue

            if getattr(
                projectile,
                "is_beam",
                False
            ):

                opponent = (
                    projectile.weapon.player.opponent
                )

                if check_beam_player_collision(
                    projectile,
                    opponent
                ):

                    projectile.hit(
                        opponent
                    )

                continue

            if getattr(
                projectile,
                "ignore_collision",
                False
            ):
                continue

            if check_projectile_player_collision(
                projectile,
                self.player1
            ):

                results = projectile.hit(
                    self.player1
                )

                if results:

                    spawned_projectiles.extend(
                        results
                    )

            elif check_projectile_player_collision(
                projectile,
                self.player2
            ):

                results = projectile.hit(
                    self.player2
                )

                if results:

                    spawned_projectiles.extend(
                        results
                    )

        self.projectiles.extend(
            spawned_projectiles
        )