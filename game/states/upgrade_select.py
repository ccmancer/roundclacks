# game/states/upgrade_select.py

import pygame

from game.states.state import State
from upgrades.upgrade_pool import generate_upgrade_choices


class UpgradeSelectState(State):
    def __init__(self, match_state, loser):
        super().__init__(match_state.game)

        self.match_state = match_state
        self.loser = loser

        self.upgrade_choices = generate_upgrade_choices(
            loser.weapon.upgrade_pool
        )

        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 28)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_1:
                self.select_upgrade(0)

            elif event.key == pygame.K_2:
                self.select_upgrade(1)

            elif event.key == pygame.K_3:
                self.select_upgrade(2)

            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def select_upgrade(self, index):
        if index >= len(self.upgrade_choices):
            return

        upgrade = self.upgrade_choices[index]

        self.match_state.upgrade_selected(upgrade)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill("white")

        title = self.font.render(
            "Choose an Upgrade",
            True,
            "black"
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2 - title.get_width() // 2,
                80
            )
        )

        player_text = self.font.render(
            f"{self.loser.color} player",
            True,
            self.loser.color
        )

        screen.blit(
            player_text,
            (
                screen.get_width() // 2 - player_text.get_width() // 2,
                130
            )
        )

        for i, upgrade in enumerate(self.upgrade_choices):
            y = 220 + i * 130

            rarity = self.font.render(
                f"[{i + 1}] {upgrade.name} ({upgrade.rarity})",
                True,
                "black"
            )

            description = self.small_font.render(
                upgrade.description,
                True,
                "black"
            )

            screen.blit(
                rarity,
                (80, y)
            )

            screen.blit(
                description,
                (100, y + 40)
            )