import pygame

from entities.player import Player
from physics.collision import (
    check_circle_collision,
    resolve_circle_collision,
    check_bullet_player_collision
)
from game.round import RoundManager


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
        self.bullets = []
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
            bullet = self.player1.weapon.attack()
            if bullet is not None:
                self.bullets.append(bullet)
        if keys[pygame.K_RETURN]:
            bullet = self.player2.weapon.attack()
            if bullet is not None:
                self.bullets.append(bullet)
        for bullet in self.bullets[:]:
            bullet.update(self.dt)
            if bullet.is_out_of_bounds(
                self.screen.get_width(),
                self.screen.get_height()
            ):
                self.bullets.remove(bullet)
                continue
            if check_bullet_player_collision(
                bullet,
                self.player1
            ):
                self.player1.take_damage(bullet.damage)
                self.bullets.remove(bullet)
                print(self.player1.health)
                continue
            if check_bullet_player_collision(
                bullet,
                self.player2
            ):
                self.player2.take_damage(bullet.damage)
                self.bullets.remove(bullet)
                print(self.player2.health)
                continue
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
            for bullet in self.bullets:
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

        loser.weapon.upgrades.append(upgrade)

        print(
            loser.color,
            "selected",
            upgrade.name
        )

        self.bullets.clear()

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