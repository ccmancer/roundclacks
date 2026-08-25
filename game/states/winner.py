import pygame

from game.states.state import State
from ui.button import Button


class WinnerState(State):

    def __init__(
        self,
        match_state,
        winner
    ):
        super().__init__(
            match_state.game
        )

        self.match_state = match_state
        self.winner = winner

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.title_font = pygame.font.Font(
            None,
            60
        )

        self.score_font = pygame.font.Font(
            None,
            45
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        screen_width = (
            self.game.screen.get_width()
        )

        button_width = 200
        button_height = 60
        button_gap = 20

        total_width = (
            button_width * 2
            + button_gap
        )

        start_x = (
            screen_width
            - total_width
        ) // 2

        self.rematch_button = Button(
            "REMATCH",
            (
                start_x,
                400,
                button_width,
                button_height
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.menu_button = Button(
            "MENU",
            (
                start_x
                + button_width
                + button_gap,
                400,
                button_width,
                button_height
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.buttons = [
            self.rematch_button,
            self.menu_button
        ]

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.game.return_to_main_menu()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                if self.rematch_button.clicked(
                    event
                ):
                    self.rematch()

                elif self.menu_button.clicked(
                    event
                ):
                    self.game.return_to_main_menu()

    # -------------------------------------------------
    # REMATCH
    # -------------------------------------------------

    def rematch(self):
        from game.states.weapon_select import (
            WeaponSelectState
        )

        self.game.state = WeaponSelectState(
            self.game
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        for button in self.buttons:
            button.update(
                mouse_position
            )

    # -------------------------------------------------
    # TEXT
    # -------------------------------------------------

    def draw_outlined_text(
        self,
        screen,
        text,
        font,
        center,
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

        outline_rect = outline.get_rect(
            center=center
        )

        foreground_rect = foreground.get_rect(
            center=center
        )

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
                        outline_rect.x + dx,
                        outline_rect.y + dy
                    )
                )

        screen.blit(
            foreground,
            foreground_rect
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        screen.fill(
            "white"
        )

        screen_width = (
            screen.get_width()
        )

        self.draw_outlined_text(
            screen,
            f"{self.winner.name} WINS!",
            self.title_font,
            (
                screen_width // 2,
                180
            ),
            self.winner.color
        )

        score = self.score_font.render(
            (
                f"{self.match_state.match.player1_wins}"
                f" - "
                f"{self.match_state.match.player2_wins}"
            ),
            True,
            "black"
        )

        score_rect = score.get_rect(
            center=(
                screen_width // 2,
                270
            )
        )

        screen.blit(
            score,
            score_rect
        )

        for button in self.buttons:
            button.draw(
                screen
            )