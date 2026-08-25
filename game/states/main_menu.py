import pygame

from game.states.state import State
from ui.button import Button


class MainMenuState(State):

    OPTIONS = [
        "Netplay",
        "Local Multiplayer",
        "Game Cards",
        "Settings",
    ]

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

        self.title_font = pygame.font.Font(
            None,
            80
        )

        self.buttons = []

        start_y = 250

        for i, option in enumerate(
            self.OPTIONS
        ):
            self.buttons.append(
                Button(
                    option,
                    (
                        210,
                        start_y + i * 75,
                        300,
                        55
                    ),
                    font_size=32,
                    audio=self.game.audio
                )
            )

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.QUIT:
                self.game.running = False

            for i, button in enumerate(
                self.buttons
            ):
                if button.clicked(event):
                    self.select_option(i)

    def select_option(
        self,
        index
    ):
        option = self.OPTIONS[index]

        if option == "Netplay":
            self.game.start_host_list()

        elif option == "Local Multiplayer":
            self.game.start_weapon_select()

        elif option == "Game Cards":
            self.game.start_card_gallery()

        elif option == "Settings":
            self.game.start_settings()

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        for button in self.buttons:
            button.update(
                mouse_position
            )

    def draw(
        self,
        screen
    ):
        screen.fill(
            "white"
        )

        title = self.title_font.render(
            "ROUNDCLACKS",
            True,
            "black"
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2
                - title.get_width() // 2,
                100
            )
        )

        for button in self.buttons:
            button.draw(
                screen
            )