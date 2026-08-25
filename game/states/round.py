import pygame
import colorsys

from game.states.state import State

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

        self.match_state = match_state

        self.player1 = match_state.player1
        self.player2 = match_state.player2

        self.projectiles = []

        # -------------------------------------------------
        # Reset players for the new round
        # -------------------------------------------------

        self.player1.reset(
            (150, 360)
        )

        self.player2.reset(
            (570, 360)
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

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.game.running = False

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
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
        # Players
        # -------------------------------------------------

        self.player1.update(
            dt,
            width,
            height
        )

        self.player2.update(
            dt,
            width,
            height
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
            width,
            height
        )

        # -------------------------------------------------
        # Player collision
        # -------------------------------------------------

        if check_circle_collision(
            self.player1,
            self.player2
        ):

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

        # -------------------------------------------------
        # Player 1
        # -------------------------------------------------

        for card in self.player1_upgrade_cards:

            if card.get_mini_rect().collidepoint(
                mouse_position
            ):
                hovered_card = card
                break

        # -------------------------------------------------
        # Player 2
        # -------------------------------------------------

        if hovered_card is None:

            for card in self.player2_upgrade_cards:

                if card.get_mini_rect().collidepoint(
                    mouse_position
                ):
                    hovered_card = card
                    break

        # -------------------------------------------------
        # Display state
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Player names
        # -------------------------------------------------

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
        # -------------------------------------------------
        # Weapon cleanup
        # -------------------------------------------------

        self.player1.weapon.on_death()
        self.player2.weapon.on_death()

        # -------------------------------------------------
        # Leave round
        # -------------------------------------------------

        self.match_state.round_finished(
            winner,
            loser
        )

    # -------------------------------------------------
    # WEAPON INPUT
    # -------------------------------------------------

    def handle_weapon_input(
        self,
        width,
        height
    ):
        keys = pygame.key.get_pressed()

        # -------------------------------------------------
        # Player 1
        # -------------------------------------------------

        if keys[
            self.player1.attack_key
        ]:

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

        if keys[
            self.player2.attack_key
        ]:

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

            # -------------------------------------------------
            # Cluster fragments
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Normal update
            # -------------------------------------------------

            projectile.update(
                dt
            )

            # -------------------------------------------------
            # Explosion-spawned entities
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Delayed explosion
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Boundary behavior
            # -------------------------------------------------

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
        # Player 1
        # -------------------------------------------------

        if isinstance(
            self.player1.weapon,
            Unarmed
        ):

            weapon = self.player1.weapon

            if check_circle_collision(
                self.player1,
                self.player2
            ):

                if weapon.can_hit(
                    self.player2
                ):

                    weapon.hit(
                        self.player2
                    )

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
        # Player 2
        # -------------------------------------------------

        if isinstance(
            self.player2.weapon,
            Unarmed
        ):

            weapon = self.player2.weapon

            if check_circle_collision(
                self.player1,
                self.player2
            ):

                if weapon.can_hit(
                    self.player1
                ):

                    weapon.hit(
                        self.player1
                    )

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

            # -------------------------------------------------
            # Pincushion arrows
            # -------------------------------------------------

            if getattr(
                projectile,
                "stuck_to",
                None
            ) is not None:
                continue

            # -------------------------------------------------
            # Cluster fragments
            # -------------------------------------------------

            if getattr(
                projectile,
                "cluster_child",
                False
            ):
                continue

            # -------------------------------------------------
            # Fire patches
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Beam
            # -------------------------------------------------

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

            # -------------------------------------------------
            # First-frame protection
            # -------------------------------------------------

            if getattr(
                projectile,
                "ignore_collision",
                False
            ):
                continue

            # -------------------------------------------------
            # Projectile -> Player 1
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Projectile -> Player 2
            # -------------------------------------------------

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