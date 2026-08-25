import pygame
import re
from pathlib import Path

from game.states.state import State
from upgrades.upgrade_pool import generate_upgrade_choices


UPGRADE_FOLDER = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "sprites"
    / "upgrade"
)

SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "audio"
    / "ui"
)


class UpgradeSelectState(State):
    # -------------------------------------------------
    # Layout
    # -------------------------------------------------

    CARD_WIDTH = 200
    CARD_HEIGHT = 280
    CARD_GAP = 20

    CARD_START_Y = -CARD_HEIGHT - 40
    CARD_TARGET_Y = 220

    CARD_SLIDE_DURATION = 0.45
    CARD_STAGGER = 0.12
    CARD_HOVER_LIFT = 8

    CARD_SELECT_DURATION = 0.4

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
        match_state,
        player
    ):
        super().__init__(
            match_state.game
        )

        self.match_state = match_state
        self.loser = player

        self.upgrade_choices = (
            generate_upgrade_choices(
                player.weapon.upgrade_pool
            )
        )

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.title_font = pygame.font.Font(
            None,
            40
        )

        self.name_font = pygame.font.Font(
            None,
            27
        )

        self.description_font = pygame.font.Font(
            None,
            17
        )

        # -------------------------------------------------
        # Sounds
        # -------------------------------------------------

        self.card_present_sound = (
            self.game.audio.load_ui_sound(
                SOUND_FOLDER / "card_present.mp3"
            )
        )

        self.card_select_sound = (
            self.game.audio.load_ui_sound(
                SOUND_FOLDER / "card_select.mp3"
            )
        )

        # Play once when the upgrade selection appears.
        self.card_present_sound.play()

        # -------------------------------------------------
        # Card sprites
        # -------------------------------------------------

        self.card_sprites = {}

        for rarity in (
            "common",
            "rare",
            "super rare"
        ):
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

            self.card_sprites[rarity] = (
                pygame.image.load(
                    path
                ).convert_alpha()
            )

        # -------------------------------------------------
        # Upgrade sprites
        # -------------------------------------------------

        self.upgrade_sprites = []

        for upgrade in self.upgrade_choices:
            self.upgrade_sprites.append(
                self.load_upgrade_sprite(
                    upgrade.name
                )
            )

        # -------------------------------------------------
        # Card entrance animation
        # -------------------------------------------------

        self.card_times = [
            i * self.CARD_STAGGER
            for i in range(
                len(
                    self.upgrade_choices
                )
            )
        ]

        self.elapsed = 0
        self.cards_finished = False

        # -------------------------------------------------
        # Selection animation
        # -------------------------------------------------

        self.selected_index = None
        self.selection_timer = 0
        self.selection_complete = False

    # -------------------------------------------------
    # ASSET HELPERS
    # -------------------------------------------------

    def get_upgrade_filename(
        self,
        name
    ):
        filename = name.lower()

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

    def load_upgrade_sprite(
        self,
        name
    ):
        path = (
            UPGRADE_FOLDER
            / self.get_upgrade_filename(name)
        )

        try:
            return pygame.image.load(
                path
            ).convert_alpha()

        except pygame.error:
            return None

    # -------------------------------------------------
    # INPUT
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.game.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                if not self.cards_finished:
                    continue

                if self.selected_index is not None:
                    continue

                mouse_position = event.pos

                for i in range(
                    len(
                        self.upgrade_choices
                    )
                ):
                    rect = self.get_card_rect(
                        i,
                        hovered=False
                    )

                    if rect.collidepoint(
                        mouse_position
                    ):
                        self.select_upgrade(i)
                        break

    # -------------------------------------------------
    # SELECT
    # -------------------------------------------------

    def select_upgrade(
        self,
        index
    ):
        if index >= len(
            self.upgrade_choices
        ):
            return

        self.selected_index = index
        self.selection_timer = 0
        self.selection_complete = False

        # Play immediately when a card is picked.
        self.card_select_sound.play()

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        # -------------------------------------------------
        # Card entrance
        # -------------------------------------------------

        if self.selected_index is None:

            self.elapsed += dt

            self.cards_finished = True

            for start_time in self.card_times:

                if (
                    self.elapsed
                    < start_time
                    + self.CARD_SLIDE_DURATION
                ):
                    self.cards_finished = False
                    break

            return

        # -------------------------------------------------
        # Selection animation
        # -------------------------------------------------

        self.selection_timer += dt

        if (
            self.selection_timer
            >= self.CARD_SELECT_DURATION
            and not self.selection_complete
        ):
            self.selection_complete = True

            upgrade = (
                self.upgrade_choices[
                    self.selected_index
                ]
            )

            self.match_state.upgrade_selected(
                upgrade
            )

    # -------------------------------------------------
    # CARD POSITION
    # -------------------------------------------------

    def get_card_y(
        self,
        index
    ):
        start_time = (
            self.card_times[index]
        )

        progress = (
            self.elapsed
            - start_time
        ) / self.CARD_SLIDE_DURATION

        progress = max(
            0,
            min(
                1,
                progress
            )
        )

        progress = (
            1
            - (1 - progress) ** 3
        )

        return (
            self.CARD_START_Y
            + (
                self.CARD_TARGET_Y
                - self.CARD_START_Y
            )
            * progress
        )

    def get_selected_progress(
        self
    ):
        progress = (
            self.selection_timer
            / self.CARD_SELECT_DURATION
        )

        progress = max(
            0,
            min(
                1,
                progress
            )
        )

        return (
            1
            - (1 - progress) ** 3
        )

    def get_card_y_after_selection(
        self,
        index
    ):
        base_y = self.get_card_y(
            index
        )

        if self.selected_index is None:
            return base_y

        progress = (
            self.get_selected_progress()
        )

        if index == self.selected_index:
            return base_y

        target_y = (
            -self.CARD_HEIGHT
            - 40
        )

        return (
            base_y
            + (
                target_y
                - base_y
            )
            * progress
        )

    def get_card_rect(
        self,
        index,
        hovered=False
    ):
        screen_width = (
            self.game.screen.get_width()
        )

        total_width = (
            len(self.upgrade_choices)
            * self.CARD_WIDTH
            + (
                len(self.upgrade_choices) - 1
            )
            * self.CARD_GAP
        )

        start_x = (
            screen_width
            - total_width
        ) / 2

        x = (
            start_x
            + index
            * (
                self.CARD_WIDTH
                + self.CARD_GAP
            )
        )

        y = self.get_card_y_after_selection(
            index
        )

        if (
            hovered
            and self.selected_index is None
        ):
            y -= self.CARD_HOVER_LIFT

        return pygame.Rect(
            int(x),
            int(y),
            self.CARD_WIDTH,
            self.CARD_HEIGHT
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        screen.fill(
            (20, 20, 20)
        )

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        title = self.title_font.render(
            "CHOOSE AN UPGRADE",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(
                screen.get_width() // 2,
                55
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # Player name
        # -------------------------------------------------

        player_name = getattr(
            self.loser,
            "name",
            "PLAYER"
        )

        player_color = getattr(
            self.loser,
            "color",
            (255, 255, 255)
        )

        player_text = self.title_font.render(
            player_name,
            True,
            player_color
        )

        player_rect = player_text.get_rect(
            center=(
                screen.get_width() // 2,
                100
            )
        )

        screen.blit(
            player_text,
            player_rect
        )

        # -------------------------------------------------
        # Cards
        # -------------------------------------------------

        mouse_position = pygame.mouse.get_pos()

        for i, upgrade in enumerate(
            self.upgrade_choices
        ):
            normal_rect = self.get_card_rect(
                i,
                hovered=False
            )

            hovered = (
                self.cards_finished
                and self.selected_index is None
                and normal_rect.collidepoint(
                    mouse_position
                )
            )

            rect = self.get_card_rect(
                i,
                hovered=hovered
            )

            self.draw_card(
                screen,
                i,
                upgrade,
                rect,
                hovered
            )

    # -------------------------------------------------
    # CARD
    # -------------------------------------------------

    def draw_card(
        self,
        screen,
        index,
        upgrade,
        rect,
        hovered
    ):
        rarity = (
            upgrade.rarity.lower()
        )

        # -------------------------------------------------
        # Card base
        # -------------------------------------------------

        card_sprite = (
            self.card_sprites[rarity]
        )

        card_sprite = pygame.transform.smoothscale(
            card_sprite,
            (
                self.CARD_WIDTH,
                self.CARD_HEIGHT
            )
        )

        screen.blit(
            card_sprite,
            rect
        )

        # -------------------------------------------------
        # Hover outline
        # -------------------------------------------------

        if hovered:

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                rect,
                2
            )

        # -------------------------------------------------
        # Text colors
        # -------------------------------------------------

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
        # Upgrade name
        # -------------------------------------------------

        name = self.name_font.render(
            upgrade.name,
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
        # Upgrade image
        # -------------------------------------------------

        upgrade_sprite = (
            self.upgrade_sprites[index]
        )

        if upgrade_sprite is not None:

            image_size = 75

            image = pygame.transform.smoothscale(
                upgrade_sprite,
                (
                    image_size,
                    image_size
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
            upgrade.description,
            self.description_font,
            rarity_color,
            pygame.Rect(
                rect.x + 15,
                rect.y + 150,
                self.CARD_WIDTH - 30,
                110
            )
        )

    # -------------------------------------------------
    # TEXT WRAPPING
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