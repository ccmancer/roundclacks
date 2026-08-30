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
        # Victory music
        # -------------------------------------------------

        self.game.audio.play_music(
            "victory"
        )

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.title_font = pygame.font.Font(
            None,
            55
        )

        self.info_font = pygame.font.Font(
            None,
            28
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.rematch_button = Button(
            "Rematch",
            (
                210,
                500,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.menu_button = Button(
            "Return to Menu",
            (
                210,
                570,
                300,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.QUIT:

                self.game.running = False

                return

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.game.return_to_main_menu()

                    return

            if self.rematch_button.clicked(
                event
            ):

                self.game.start_weapon_select()

                return

            if self.menu_button.clicked(
                event
            ):

                self.game.return_to_main_menu()

                return

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.rematch_button.update(
            mouse_position
        )

        self.menu_button.update(
            mouse_position
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

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = self.title_font.render(
            "WINNER!",
            True,
            self.winner.color
        )

        title_rect = title.get_rect(
            center=(
                screen_width // 2,
                100
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # Winner
        # -------------------------------------------------

        winner_name = self.info_font.render(
            self.winner.name,
            True,
            self.winner.color
        )

        winner_name_rect = (
            winner_name.get_rect(
                center=(
                    screen_width // 2,
                    180
                )
            )
        )

        screen.blit(
            winner_name,
            winner_name_rect
        )

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

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

        score = self.info_font.render(
            (
                f"{player1_score}"
                f" - "
                f"{player2_score}"
            ),
            True,
            "black"
        )

        score_rect = score.get_rect(
            center=(
                screen_width // 2,
                250
            )
        )

        screen.blit(
            score,
            score_rect
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.rematch_button.draw(
            screen
        )

        self.menu_button.draw(
            screen
        )