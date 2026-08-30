import pygame

from game.asset_helper import load_image


class WeaponIcon:
    SIZE = 100

    def __init__(
        self,
        weapon_class,
        position
    ):
        self.weapon_class = weapon_class

        self.name = weapon_class.__name__

        self.position = pygame.Vector2(
            position
        )

        self.hovered = False
        self.selected = False

        self.sprite = self.load_sprite()

    # -------------------------------------------------
    # SPRITE
    # -------------------------------------------------

    def get_filename(self):
        return (
            self.name.lower()
            + ".png"
        )

    def load_sprite(self):
        try:
            return load_image(
                "sprites",
                "ui",
                self.get_filename()
            )

        except (
            FileNotFoundError,
            pygame.error
        ):
            return None

    # -------------------------------------------------
    # RECT
    # -------------------------------------------------

    def get_rect(self):
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.SIZE,
            self.SIZE
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        mouse_position
    ):
        self.hovered = (
            self.get_rect().collidepoint(
                mouse_position
            )
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen,
        outline_color=(255, 255, 255),
        outline_width=3
    ):
        rect = self.get_rect()

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        pygame.draw.rect(
            screen,
            (25, 25, 25),
            rect
        )

        # -------------------------------------------------
        # Sprite
        # -------------------------------------------------

        if self.sprite is not None:

            sprite = pygame.transform.smoothscale(
                self.sprite,
                (
                    self.SIZE - 16,
                    self.SIZE - 16
                )
            )

            sprite_rect = sprite.get_rect(
                center=rect.center
            )

            screen.blit(
                sprite,
                sprite_rect
            )

        # -------------------------------------------------
        # Outline
        # -------------------------------------------------

        if self.selected or self.hovered:

            color = outline_color

            width = (
                outline_width
                if self.selected
                else 2
            )

            pygame.draw.rect(
                screen,
                color,
                rect,
                width
            )

        else:

            pygame.draw.rect(
                screen,
                (100, 100, 100),
                rect,
                1
            )

    # -------------------------------------------------
    # CLICK
    # -------------------------------------------------

    def clicked(
        self,
        event
    ):
        return (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.get_rect().collidepoint(
                event.pos
            )
        )