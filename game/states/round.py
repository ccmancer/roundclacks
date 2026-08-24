import pygame

from game.states.state import State

from physics.collision import (
    check_circle_collision,
    resolve_circle_collision,
    check_sword_player_collision,
    check_projectile_player_collision,
    check_beam_player_collision
)

from weapons.unarmed import Unarmed


class RoundState(State):
    def __init__(self, match_state):
        super().__init__(match_state.game)

        self.match_state = match_state

        self.player1 = match_state.player1
        self.player2 = match_state.player2

        self.projectiles = []

        self.player1.reset((150, 360))
        self.player2.reset((570, 360))

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt):
        width = self.game.screen.get_width()
        height = self.game.screen.get_height()

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

        # Collect entities spawned by weapons.
        if hasattr(
            self.player1.weapon,
            "spawned_entities"
        ):
            self.projectiles.extend(
                self.player1.weapon.spawned_entities
            )

        if hasattr(
            self.player2.weapon,
            "spawned_entities"
        ):
            self.projectiles.extend(
                self.player2.weapon.spawned_entities
            )

        self.handle_weapon_input(
            width,
            height
        )

        # Player-player collision.
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

        self.handle_weapon_collisions()

        self.update_projectiles(
            dt,
            width,
            height
        )

        self.handle_projectile_collisions()

        self.remove_dead_projectiles()

        self.check_round_end()

    def draw(self, screen):
        screen.fill("grey")

        self.player1.draw(screen)
        self.player2.draw(screen)

        for projectile in self.projectiles:
            projectile.draw(screen)

    def check_round_end(self):
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

    def finish(self, winner, loser):
        self.match_state.round_finished(
            winner,
            loser
        )

    def handle_weapon_input(
        self,
        width,
        height
    ):
        keys = pygame.key.get_pressed()

        if keys[self.player1.attack_key]:
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

            self.projectiles.extend(
                projectiles
            )

        if keys[self.player2.attack_key]:
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

            self.projectiles.extend(
                projectiles
            )

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

            # Cluster fragments.
            if getattr(
                projectile,
                "cluster_child",
                False
            ):
                projectile.update(dt)

                if projectile.should_explode:
                    results = projectile.explode()

                    if results:
                        spawned_projectiles.extend(
                            results
                        )

                continue

            projectile.update(dt)

            # Explosion-spawned entities.
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

            # Mine triggered.
            if getattr(
                projectile,
                "should_explode",
                False
            ):
                results = projectile.explode()

                if results:
                    spawned_projectiles.extend(
                        results
                    )

                projectile.should_explode = False

                continue

            # Boundary behavior.
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
                        results = projectile.explode()

                        if results:
                            spawned_projectiles.extend(
                                results
                            )

                    else:
                        projectile.alive = False

        self.projectiles.extend(
            spawned_projectiles
        )

    def remove_dead_projectiles(self):
        self.projectiles = [
            projectile
            for projectile in self.projectiles
            if projectile.alive
        ]

    def handle_weapon_collisions(self):
        # Player 1 -> Player 2.
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

        # Player 2 -> Player 1.
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

    def handle_projectile_collisions(self):
        spawned_projectiles = []

        for projectile in self.projectiles:

            if not projectile.alive:
                continue

            # Pincushion arrows.
            if getattr(
                projectile,
                "stuck_to",
                None
            ) is not None:
                continue

            # Cluster fragments.
            if getattr(
                projectile,
                "cluster_child",
                False
            ):
                continue

            # Fire patches.
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

            # Beam collision.
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

            # Earthlight Ray first-frame protection.
            if getattr(
                projectile,
                "ignore_collision",
                False
            ):
                continue

            # Normal projectile -> Player 1.
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

            # Normal projectile -> Player 2.
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
