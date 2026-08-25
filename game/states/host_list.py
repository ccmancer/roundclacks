import pygame

from game.states.state import State
from ui.button import Button


class HostListState(State):

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

        self.title_font = pygame.font.Font(
            None,
            55
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

        self.hosts = []

        self.back_button = Button(
            "Back",
            (
                20,
                650,
                120,
                45
            ),
            font_size=25,
            audio=self.game.audio
        )

        self.host_button = Button(
            "Host Game",
            (
                210,
                500,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

    def handle_events(
        self,
        events
    ):
        for event in events:

            if self.back_button.clicked(event):
                self.game.return_to_main_menu()

            elif self.host_button.clicked(event):
                self.host_game()

    def host_game(self):
        print(
            "Netplay hosting not implemented yet"
        )

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.back_button.update(
            mouse_position
        )

        self.host_button.update(
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
            "NETPLAY",
            True,
            "black"
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2
                - title.get_width() // 2,
                80
            )
        )

        info = self.info_font.render(
            "Available Games",
            True,
            "black"
        )

        screen.blit(
            info,
            (
                screen.get_width() // 2
                - info.get_width() // 2,
                170
            )
        )

        if not self.hosts:

            empty = self.info_font.render(
                "No games available",
                True,
                (100, 100, 100)
            )

            screen.blit(
                empty,
                (
                    screen.get_width() // 2
                    - empty.get_width() // 2,
                    250
                )
            )

        self.host_button.draw(
            screen
        )

        self.back_button.draw(
            screen
        )