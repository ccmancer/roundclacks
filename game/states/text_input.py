import pygame

from game.states.state import State
from ui.button import Button


class TextInputState(State):

    def __init__(
        self,
        parent_state,
        title,
        initial_text="",
        input_type="text",
        on_confirm=None
    ):
        super().__init__(
            parent_state.game
        )

        self.parent_state = parent_state
        self.title = title
        self.text = str(initial_text)
        self.input_type = input_type
        self.on_confirm = on_confirm

        self.font = pygame.font.Font(
            None,
            40
        )

        self.small_font = pygame.font.Font(
            None,
            28
        )

        self.error_font = pygame.font.Font(
            None,
            22
        )

        screen_width = (
            self.game.screen.get_width()
        )

        input_width = 500
        input_height = 65

        input_x = (
            screen_width
            - input_width
        ) // 2

        input_y = 220

        self.input_rect = pygame.Rect(
            input_x,
            input_y,
            input_width,
            input_height
        )

        button_width = 200
        button_height = 55

        button_x = (
            screen_width
            - button_width
        ) // 2

        self.confirm_button = Button(
            "Confirm",
            (
                button_x,
                500,
                button_width,
                button_height
            ),
            font_size=28,
            audio=self.game.audio
        )

        back_width = 120
        back_height = 45

        self.back_button = Button(
            "Back",
            (
                (
                    screen_width
                    - back_width
                ) // 2,
                580,
                back_width,
                back_height
            ),
            font_size=25,
            audio=self.game.audio
        )

        self.error = ""

        pygame.key.start_text_input()

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.TEXTINPUT:

                self.text += event.text

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                elif event.key == pygame.K_RETURN:
                    self.confirm()

                elif event.key == pygame.K_ESCAPE:
                    self.close()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                if self.confirm_button.clicked(event):
                    self.confirm()

                elif self.back_button.clicked(event):
                    self.close()

    # -------------------------------------------------
    # CONFIRM
    # -------------------------------------------------

    def confirm(self):

        if self.input_type == "rgb":

            if not self.validate_rgb():
                return

        elif self.input_type == "text":

            if not self.text.strip():
                self.error = (
                    "Name cannot be empty."
                )
                return

        pygame.key.stop_text_input()

        if self.on_confirm is not None:
            self.on_confirm(
                self.text
            )

        self.parent_state.current_state = (
            self.parent_state
        )

    # -------------------------------------------------
    # RGB VALIDATION
    # -------------------------------------------------

    def validate_rgb(self):

        parts = [
            part.strip()
            for part in self.text.split(",")
        ]

        if len(parts) != 3:

            self.error = (
                "Enter RGB as: 255, 100, 50"
            )

            return False

        try:

            values = [
                int(part)
                for part in parts
            ]

        except ValueError:

            self.error = (
                "RGB values must be numbers."
            )

            return False

        if any(
            value < 0 or value > 255
            for value in values
        ):

            self.error = (
                "RGB values must be 0-255."
            )

            return False

        self.error = ""

        return True

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        self.confirm_button.update(
            mouse_position
        )

        self.back_button.update(
            mouse_position
        )

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------

    def close(self):

        pygame.key.stop_text_input()

        self.parent_state.current_state = (
            self.parent_state
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

        title = self.font.render(
            self.title,
            True,
            "black"
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

        pygame.draw.rect(
            screen,
            (235, 235, 235),
            self.input_rect
        )

        pygame.draw.rect(
            screen,
            "black",
            self.input_rect,
            2
        )

        text_surface = self.small_font.render(
            self.text,
            True,
            "black"
        )

        text_rect = text_surface.get_rect(
            midleft=(
                self.input_rect.x + 10,
                self.input_rect.centery
            )
        )

        screen.blit(
            text_surface,
            text_rect
        )

        if self.input_type == "rgb":

            hint = self.error_font.render(
                "Example: 255, 100, 50",
                True,
                (100, 100, 100)
            )

            hint_rect = hint.get_rect(
                center=(
                    screen_width // 2,
                    self.input_rect.bottom + 25
                )
            )

            screen.blit(
                hint,
                hint_rect
            )

        if self.error:

            error_surface = self.error_font.render(
                self.error,
                True,
                "red"
            )

            error_rect = error_surface.get_rect(
                center=(
                    screen_width // 2,
                    400
                )
            )

            screen.blit(
                error_surface,
                error_rect
            )

        self.confirm_button.draw(
            screen
        )

        self.back_button.draw(
            screen
        )