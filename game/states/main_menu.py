# game/states/main_menu.py

import pygame

from game.states.state import State


class MainMenuState(State):
    OPTIONS = [
        "Netplay",
        "Local Multiplayer",
        "Sandbox",
        "Settings",
    ]

    def __init__(self, game):
        super().__init__(game)

        self.selected = 0

        self.title_font = pygame.font.Font(None, 80)
        self.option_font = pygame.font.Font(None, 50)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    self.selected = (
                        self.selected - 1
                    ) % len(self.OPTIONS)

                elif event.key == pygame.K_DOWN:
                    self.selected = (
                        self.selected + 1
                    ) % len(self.OPTIONS)

                elif event.key == pygame.K_RETURN:
                    self.select_option()

                elif event.key == pygame.K_ESCAPE:
                    self.game.running = False

    def select_option(self):
        option = self.OPTIONS[self.selected]

        if option == "Local Multiplayer":
            if option == "Local Multiplayer":
                self.game.start_weapon_select()

        elif option == "Netplay":
            print("Netplay not implemented yet")

        elif option == "Sandbox":
            print("Sandbox not implemented yet")

        elif option == "Settings":
            print("Settings not implemented yet")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill("white")

        # Title
        title = self.title_font.render(
            "ROUNDCLACKS",
            True,
            "black"
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2 - title.get_width() // 2,
                100
            )
        )

        # Menu options
        for i, option in enumerate(self.OPTIONS):
            selected = i == self.selected

            color = "red" if selected else "black"

            text = self.option_font.render(
                option,
                True,
                color
            )

            screen.blit(
                text,
                (
                    screen.get_width() // 2 - text.get_width() // 2,
                    250 + i * 70
                )
            )