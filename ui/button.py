import pygame
from pathlib import Path


SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "audio"
    / "ui"
)


class Button:
    def __init__(
        self,
        text,
        rect,
        font_size=32,
        audio=None
    ):
        self.text = text
        self.rect = pygame.Rect(rect)

        self.font = pygame.font.Font(
            None,
            font_size
        )

        self.hovered = False

        # -------------------------------------------------
        # Audio
        # -------------------------------------------------

        self.select_sound = None

        if audio is not None:
            self.select_sound = (
                audio.load_ui_sound(
                    SOUND_FOLDER / "select.mp3"
                )
            )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        mouse_position
    ):
        self.hovered = (
            self.rect.collidepoint(
                mouse_position
            )
        )

    # -------------------------------------------------
    # CLICK
    # -------------------------------------------------

    def clicked(
        self,
        event
    ):
        clicked = (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(
                event.pos
            )
        )

        if clicked and self.select_sound is not None:
            self.select_sound.play()

        return clicked

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            self.rect
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            self.rect,
            2
        )

        text = self.font.render(
            self.text,
            True,
            (255, 255, 255)
        )

        text_rect = text.get_rect(
            center=self.rect.center
        )

        screen.blit(
            text,
            text_rect
        )