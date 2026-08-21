import pygame

from entities.player import Player
from physics.collision import (
    check_circle_collision,
    resolve_circle_collision,
    check_projectile_player_collision,
    check_sword_player_collision
)
from game.round import RoundManager
from weapons.sword import Sword


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((720, 720))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.player1 = Player(
            150,
            360,
            40,
            "red",
            375
        )
        self.player2 = Player(
            570,
            360,
            40,
            "blue",
            375
        )
        self.round_manager = RoundManager(
            self.player1,
            self.player2
        )
        self.projectiles = []
        self.player1.weapon.add_upgrade(
            next(
                upgrade
                for upgrade in self.player1.weapon.upgrade_pool
                if upgrade.name == "Aerodynamic"
            )
        )
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.round_manager.state == "upgrade_selection":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.select_upgrade(0)
                    elif event.key == pygame.K_2:
                        self.select_upgrade(1)
                    elif event.key == pygame.K_3:
                        self.select_upgrade(2)
    def update(self):
        if self.round_manager.state != "fighting":
            return
        self.player1.update(
            self.dt,
            self.screen.get_width(),
            self.screen.get_height()
        )
        self.player2.update(
            self.dt,
            self.screen.get_width(),
            self.screen.get_height()
        )
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            projectiles = self.player1.weapon.attack()

            if projectiles:
                self.projectiles.extend(projectiles)

                self.apply_step_in(
                    self.player1,
                    self.player2
                )

        if keys[pygame.K_RETURN]:
            projectiles = self.player2.weapon.attack()

            if projectiles:
                self.projectiles.extend(projectiles)

                self.apply_step_in(
                    self.player2,
                    self.player1
                )
        for projectile in self.projectiles[:]:
            projectile.update(self.dt)

            if projectile.is_out_of_bounds(
                self.screen.get_width(),
                self.screen.get_height()
            ):
                self.projectiles.remove(projectile)
                continue

            if check_projectile_player_collision(
                projectile,
                self.player1
            ):
                self.player1.take_damage(projectile.damage)
                self.projectiles.remove(projectile)
                continue

            if check_projectile_player_collision(
                projectile,
                self.player2
            ):
                self.player2.take_damage(projectile.damage)
                self.projectiles.remove(projectile)
                continue
        if isinstance(self.player1.weapon, Sword):
            if (
                check_sword_player_collision(
                    self.player1.weapon,
                    self.player2
                )
                and self.player1.weapon.can_hit()
            ):
                damage = self.player1.weapon.get_hit_damage()

                self.player2.take_damage(damage)

                lifesteal = self.player1.weapon.get_lifesteal()

                if lifesteal > 0:
                    self.player1.heal(damage * lifesteal)

                self.player1.weapon.trigger_beyblade()


                vortex_force = self.player1.weapon.get_vortex_force()

                if vortex_force > 0:
                    direction = (
                        self.player1.position
                        - self.player2.position
                    )

                    self.player2.apply_force(
                        direction,
                        vortex_force,
                        0.15
                    )

                self.player1.weapon.hit()
        if isinstance(self.player2.weapon, Sword):
            if (
                check_sword_player_collision(
                    self.player2.weapon,
                    self.player1
                )
                and self.player2.weapon.can_hit()
            ):
                damage = self.player2.weapon.get_hit_damage()

                self.player1.take_damage(damage)

                lifesteal = self.player2.weapon.get_lifesteal()

                if lifesteal > 0:
                    self.player2.heal(damage * lifesteal)

                self.player2.weapon.trigger_beyblade()


                vortex_force = self.player2.weapon.get_vortex_force()

                if vortex_force > 0:
                    direction = (
                        self.player2.position
                        - self.player1.position
                    )

                    self.player1.apply_force(
                        direction,
                        vortex_force,
                        0.15
                    )

                self.player2.weapon.hit()
        if check_circle_collision(
            self.player1,
            self.player2
        ):
            resolve_circle_collision(
                self.player1,
                self.player2
            )
        if self.round_manager.check_round_end():
            self.round_manager.start_upgrade_selection()
    def draw(self):
        self.screen.fill("white")
        if self.round_manager.state == "fighting":
            self.player1.draw(self.screen)
            self.player2.draw(self.screen)
            for bullet in self.projectiles:
                bullet.draw(self.screen)
        elif self.round_manager.state == "upgrade_selection":
            self.draw_upgrade_selection()
        pygame.display.flip()
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.dt = self.clock.tick(60) / 1000
        pygame.quit()
    def select_upgrade(self, index):
        upgrade = self.round_manager.upgrade_choices[index]

        loser = self.round_manager.loser

        loser.weapon.add_upgrade(upgrade)

        print(
            loser.color,
            "selected",
            upgrade.name
        )
        print(
            loser.color,
            loser.weapon.upgrades[-1].name,
            "max health:",
            loser.get_max_health()
        )

        self.projectiles.clear()

        self.round_manager.reset_round()
        self.round_manager.state = "fighting"
    def draw_upgrade_selection(self):
        font = pygame.font.Font(None, 40)
        small_font = pygame.font.Font(None, 30)
        title = font.render(
            "Choose an Upgrade",
            True,
            "black"
        )
        self.screen.blit(
            title,
            (
                self.screen.get_width() // 2 - title.get_width() // 2,
                80
            )
        )
        for i, upgrade in enumerate(
            self.round_manager.upgrade_choices
        ):
            y = 180 + i * 140

            number = font.render(
                f"[{i + 1}] {upgrade.name}",
                True,
                "black"
            )
            description = small_font.render(
                upgrade.description,
                True,
                "black"
            )
            self.screen.blit(
                number,
                (100, y)
            )
            self.screen.blit(
                description,
                (120, y + 40)
            )
        loser_text = font.render(
            f"{self.round_manager.loser.color} player: choose an upgrade",
            True,
            "black"
        )
        self.screen.blit(
            loser_text,
            (
                self.screen.get_width() // 2 - loser_text.get_width() // 2,
                30
            )
        )
    def apply_step_in(self, player, opponent):
        force = player.weapon.get_step_force()

        if force <= 0:
            return

        direction = opponent.position - player.position

        player.apply_force(
            direction,
            force,
            0.15
        )