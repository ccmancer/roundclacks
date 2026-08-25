import pygame
import re
from pathlib import Path


UPGRADE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "upgrade"
)


class UpgradeCard:
    # -------------------------------------------------
    # Full card
    # -------------------------------------------------

    WIDTH = 200
    HEIGHT = 280

    # -------------------------------------------------
    # Mini card
    # -------------------------------------------------

    MINI_SIZE = 42
    MINI_GAP = 6

    # -------------------------------------------------
    # Colors
    # -------------------------------------------------

    RARITY_COLORS = {
        "common": (255, 255, 255),
        "rare": (80, 190, 255),
        "super rare": (255, 210, 70)
    }

    # -------------------------------------------------
    # Init
    # -------------------------------------------------

    def __init__(
        self,
        upgrade,
        position=(0, 0),
        expand_direction="right"
    ):
        self.upgrade = upgrade

        self.position = pygame.Vector2(
            position
        )

        self.expand_direction = (
            expand_direction
        )

        self.hovered = False
        self.display_mode = "mini"

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.name_font = pygame.font.Font(
            None,
            27
        )

        self.description_font = pygame.font.Font(
            None,
            17
        )

        self.stack_font = pygame.font.Font(
            None,
            16
        )

        # -------------------------------------------------
        # Card sprite
        # -------------------------------------------------

        self.card_sprite = (
            self.load_card_sprite()
        )

        # -------------------------------------------------
        # Upgrade sprite
        # -------------------------------------------------

        self.upgrade_sprite = (
            self.load_upgrade_sprite()
        )

    # -------------------------------------------------
    # ASSET HELPERS
    # -------------------------------------------------

    def get_upgrade_filename(self):
        filename = (
            self.upgrade.name.lower()
        )

        filename = re.sub(
            r"[^a-z0-9]+",
            "_",
            filename
        )

        filename = filename.strip("_")

        return (
            filename
            + ".png"
        )

    def load_card_sprite(self):
        rarity = (
            self.upgrade.rarity.lower()
        )

        filename = (
            rarity.replace(
                " ",
                "_"
            )
            + "_card.png"
        )

        path = (
            UPGRADE_FOLDER
            / filename
        )

        return pygame.image.load(
            path
        ).convert_alpha()

    def load_upgrade_sprite(self):
        path = (
            UPGRADE_FOLDER
            / self.get_upgrade_filename()
        )

        try:
            return pygame.image.load(
                path
            ).convert_alpha()

        except pygame.error:
            return None

    # -------------------------------------------------
    # POSITION
    # -------------------------------------------------

    def set_position(
        self,
        position
    ):
        self.position = pygame.Vector2(
            position
        )

    # -------------------------------------------------
    # EXPANSION
    # -------------------------------------------------

    def set_expand_direction(
        self,
        direction
    ):
        self.expand_direction = direction

    # -------------------------------------------------
    # HOVER
    # -------------------------------------------------

    def set_hovered(
        self,
        hovered
    ):
        self.hovered = hovered

    # -------------------------------------------------
    # MODE
    # -------------------------------------------------

    def set_display_mode(
        self,
        mode
    ):
        self.display_mode = mode

    # -------------------------------------------------
    # RECT
    # -------------------------------------------------

    def get_mini_rect(self):
        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.MINI_SIZE,
            self.MINI_SIZE
        )

    def get_full_rect(
        self,
        screen
    ):
        rect = pygame.Rect(
            0,
            0,
            self.WIDTH,
            self.HEIGHT
        )

        if self.expand_direction == "right":
            rect.topleft = (
                int(self.position.x),
                int(self.position.y)
            )

        elif self.expand_direction == "left":
            rect.topright = (
                int(
                    self.position.x
                    + self.MINI_SIZE
                ),
                int(self.position.y)
            )

        else:
            rect.topleft = (
                int(self.position.x),
                int(self.position.y)
            )

        return rect

    def get_rect(
        self,
        screen
    ):
        if (
            self.display_mode == "mini"
            and not self.hovered
        ):
            return self.get_mini_rect()

        if self.display_mode == "mini":
            return self.get_full_rect(
                screen
            )

        return pygame.Rect(
            int(self.position.x),
            int(self.position.y),
            self.WIDTH,
            self.HEIGHT
        )

    def contains_point(
        self,
        position,
        screen
    ):
        if (
            self.display_mode == "mini"
            and not self.hovered
        ):
            return self.get_mini_rect().collidepoint(
                position
            )

        return self.get_rect(
            screen
        ).collidepoint(
            position
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        if (
            self.display_mode == "mini"
            and not self.hovered
        ):
            self.draw_mini(
                screen
            )
        else:
            self.draw_full(
                screen
            )

    # -------------------------------------------------
    # MINI
    # -------------------------------------------------

    def draw_mini(
        self,
        screen
    ):
        rect = self.get_mini_rect()

        rarity = (
            self.upgrade.rarity.lower()
        )

        rarity_color = (
            self.RARITY_COLORS.get(
                rarity,
                (255, 255, 255)
            )
        )

        card_sprite = pygame.transform.smoothscale(
            self.card_sprite,
            (
                self.MINI_SIZE,
                self.MINI_SIZE
            )
        )

        screen.blit(
            card_sprite,
            rect
        )

        if self.upgrade_sprite is not None:
            icon = pygame.transform.smoothscale(
                self.upgrade_sprite,
                (
                    self.MINI_SIZE - 8,
                    self.MINI_SIZE - 8
                )
            )

            icon_rect = icon.get_rect(
                center=rect.center
            )

            screen.blit(
                icon,
                icon_rect
            )

        pygame.draw.rect(
            screen,
            rarity_color,
            rect,
            1
        )

        # -------------------------------------------------
        # Stack count
        # -------------------------------------------------

        if self.upgrade.stacks > 1:
            stack_text = self.stack_font.render(
                f"x{self.upgrade.stacks}",
                True,
                (255, 255, 255)
            )

            stack_rect = stack_text.get_rect(
                bottomright=(
                    rect.right - 2,
                    rect.bottom - 2
                )
            )

            background_rect = stack_rect.inflate(
                4,
                2
            )

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                background_rect
            )

            screen.blit(
                stack_text,
                stack_rect
            )

    # -------------------------------------------------
    # FULL
    # -------------------------------------------------

    def draw_full(
        self,
        screen
    ):
        rect = self.get_full_rect(
            screen
        )

        card_sprite = pygame.transform.smoothscale(
            self.card_sprite,
            (
                self.WIDTH,
                self.HEIGHT
            )
        )

        screen.blit(
            card_sprite,
            rect
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            rect,
            2
        )

        rarity = (
            self.upgrade.rarity.lower()
        )

        rarity_color = (
            self.RARITY_COLORS.get(
                rarity,
                (255, 255, 255)
            )
        )

        if rarity == "super rare":
            name_color = rarity_color
        else:
            name_color = (
                255,
                255,
                255
            )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name = self.name_font.render(
            self.upgrade.name,
            True,
            name_color
        )

        name_rect = name.get_rect(
            center=(
                rect.centerx,
                rect.y + 35
            )
        )

        screen.blit(
            name,
            name_rect
        )

        # -------------------------------------------------
        # Stack count
        # -------------------------------------------------

        if self.upgrade.stacks > 1:
            stack_text = self.stack_font.render(
                f"x{self.upgrade.stacks}",
                True,
                rarity_color
            )

            stack_rect = stack_text.get_rect(
                center=(
                    rect.centerx,
                    rect.y + 60
                )
            )

            screen.blit(
                stack_text,
                stack_rect
            )

        # -------------------------------------------------
        # Upgrade image
        # -------------------------------------------------

        if self.upgrade_sprite is not None:
            image = pygame.transform.smoothscale(
                self.upgrade_sprite,
                (
                    75,
                    75
                )
            )

            image_rect = image.get_rect(
                center=(
                    rect.centerx,
                    rect.y + 105
                )
            )

            screen.blit(
                image,
                image_rect
            )

        # -------------------------------------------------
        # Description
        # -------------------------------------------------

        self.draw_wrapped_text(
            screen,
            self.upgrade.description,
            self.description_font,
            rarity_color,
            pygame.Rect(
                rect.x + 15,
                rect.y + 150,
                self.WIDTH - 30,
                110
            )
        )

    # -------------------------------------------------
    # TEXT
    # -------------------------------------------------

    def draw_wrapped_text(
        self,
        screen,
        text,
        font,
        color,
        rect
    ):
        words = text.split()

        lines = []
        current_line = ""

        for word in words:
            test_line = (
                word
                if not current_line
                else current_line
                + " "
                + word
            )

            if font.size(
                test_line
            )[0] <= rect.width:
                current_line = test_line

            else:
                if current_line:
                    lines.append(
                        current_line
                    )

                current_line = word

        if current_line:
            lines.append(
                current_line
            )

        line_height = (
            font.get_linesize()
        )

        total_height = (
            len(lines)
            * line_height
        )

        y = (
            rect.y
            + (
                rect.height
                - total_height
            ) / 2
        )

        for line in lines:
            rendered = font.render(
                line,
                True,
                color
            )

            rendered_rect = rendered.get_rect(
                centerx=rect.centerx,
                y=int(y)
            )

            screen.blit(
                rendered,
                rendered_rect
            )

            y += line_height