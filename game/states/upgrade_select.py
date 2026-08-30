import pygame
import re

from game.asset_helper import load_image
from game.states.state import State
from upgrades.upgrade_pool import generate_upgrade_choices


class UpgradeSelectState(State):

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
    # Netplay timer
    # -------------------------------------------------

    PICK_TIME_LIMIT = 30.0

    RARITY_COLORS = {
        "common": (255, 255, 255),
        "rare": (80, 190, 255),
        "super rare": (255, 210, 70)
    }

    def __init__(
        self,
        match_state,
        player,
        interactive=True,
        previous_upgrade=None
    ):
        super().__init__(
            match_state.game
        )

        self.match_state = match_state

        # -------------------------------------------------
        # Player whose cards are being shown
        # -------------------------------------------------

        self.player = player

        # -------------------------------------------------
        # Local MatchState compatibility
        # -------------------------------------------------

        self.loser = player

        # -------------------------------------------------
        # Only this client can actually select
        # -------------------------------------------------

        self.interactive = interactive

        self.player_number = (
            1
            if player is match_state.player1
            else 2
        )

        # -------------------------------------------------
        # Detect netplay
        # -------------------------------------------------

        self.is_netplay = (
            match_state.__class__.__name__
            == "NetplayMatchState"
        )

        # -------------------------------------------------
        # Previously revealed choice
        # -------------------------------------------------

        self.previous_upgrade = (
            previous_upgrade
        )

        # -------------------------------------------------
        # Upgrade choices
        # -------------------------------------------------

        self.upgrade_choices = (
            generate_upgrade_choices(
                player.weapon.upgrade_pool,
                random_source=(
                    self.match_state.match.random
                ),
                frame=(
                    self.match_state.match.round_number
                ),
                player=self.player_number
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

        self.small_font = pygame.font.Font(
            None,
            22
        )

        # -------------------------------------------------
        # Sounds
        # -------------------------------------------------

        self.card_present_sound = (
            self.game.audio.load_ui_sound(
                "card_present.mp3"
            )
        )

        self.card_select_sound = (
            self.game.audio.load_ui_sound(
                "card_select.mp3"
            )
        )

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

            self.card_sprites[rarity] = load_image(
                "sprites",
                "upgrade",
                filename
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
        # Animation
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

        self.selected_index = None
        self.selection_timer = 0
        self.selection_complete = False

        # -------------------------------------------------
        # Netplay timer
        # -------------------------------------------------

        self.pick_elapsed = 0.0

        # -------------------------------------------------
        # Sound flags
        # -------------------------------------------------

        self.card_present_played = False
        self.card_select_played = False

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

        return (
            filename.strip("_")
            + ".png"
        )

    def load_upgrade_sprite(
        self,
        name
    ):
        try:

            return load_image(
                "sprites",
                "upgrade",
                self.get_upgrade_filename(
                    name
                )
            )

        except (
            FileNotFoundError,
            pygame.error,
            OSError
        ):

            return None

    # -------------------------------------------------
    # INPUT
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            # -------------------------------------------------
            # Window close
            # -------------------------------------------------

            if event.type == pygame.QUIT:

                if self.is_netplay:

                    self.match_state.close()

                else:

                    self.game.running = False

                return

            # -------------------------------------------------
            # Spectator
            # -------------------------------------------------

            if not self.interactive:

                continue

            # -------------------------------------------------
            # Escape
            # -------------------------------------------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if self.is_netplay:

                        self.match_state.close()

                    else:

                        self.game.running = False

                    return

            # -------------------------------------------------
            # Mouse selection
            # -------------------------------------------------

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
                        False
                    )

                    if rect.collidepoint(
                        mouse_position
                    ):

                        self.select_upgrade(
                            i
                        )

                        return

    # -------------------------------------------------
    # SELECT
    # -------------------------------------------------

    def select_upgrade(
        self,
        index
    ):
        if not self.interactive:

            return

        if self.selected_index is not None:

            return

        if not (
            0 <= index
            < len(self.upgrade_choices)
        ):

            return

        self.selected_index = index
        self.selection_timer = 0
        self.selection_complete = False

        # -------------------------------------------------
        # Cards fly back up.
        # -------------------------------------------------

        if not self.card_select_played:

            self.card_select_sound.play()

            self.card_select_played = True

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        # -------------------------------------------------
        # Waiting for selection
        # -------------------------------------------------

        if self.selected_index is None:

            self.elapsed += dt

            # -------------------------------------------------
            # Play presentation sound once when the cards
            # begin entering the screen.
            # -------------------------------------------------

            if (
                not self.card_present_played
                and self.elapsed >= 0
            ):

                self.card_present_sound.play()

                self.card_present_played = True

            # -------------------------------------------------
            # Netplay timer
            # -------------------------------------------------

            if (
                self.is_netplay
                and self.interactive
            ):

                self.pick_elapsed += dt

            # -------------------------------------------------
            # Card animation
            # -------------------------------------------------

            self.cards_finished = True

            for start_time in self.card_times:

                if (
                    self.elapsed
                    < start_time
                    + self.CARD_SLIDE_DURATION
                ):

                    self.cards_finished = False

                    break

            # -------------------------------------------------
            # Netplay timeout
            # -------------------------------------------------

            if (
                self.is_netplay
                and self.interactive
                and self.cards_finished
                and self.pick_elapsed
                >= self.PICK_TIME_LIMIT
            ):

                random_index = (
                    self.match_state.match.random.randint(
                        self.player_number,
                        "upgrade_timeout",
                        0,
                        len(
                            self.upgrade_choices
                        ) - 1
                    )
                )

                self.select_upgrade(
                    random_index
                )

            return

        # -------------------------------------------------
        # Spectators
        # -------------------------------------------------

        if not self.interactive:

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
    # EXTERNAL REVEAL
    # -------------------------------------------------

    def reveal_upgrade(
        self,
        upgrade_name
    ):
        for i, upgrade in enumerate(
            self.upgrade_choices
        ):

            if upgrade.name == upgrade_name:

                self.selected_index = i

                self.selection_timer = (
                    self.CARD_SELECT_DURATION
                )

                self.selection_complete = True

                return

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
            and self.interactive
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

        if self.interactive:

            title_text = (
                "CHOOSE AN UPGRADE"
            )

        else:

            title_text = (
                "OPPONENT'S UPGRADE"
            )

        title = self.title_font.render(
            title_text,
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

        player_text = self.title_font.render(
            self.player.name,
            True,
            self.player.color
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
        # Previous choice
        # -------------------------------------------------

        if self.previous_upgrade is not None:

            previous_text = (
                f"Opponent chose: "
                f"{self.previous_upgrade}"
            )

            rendered = self.small_font.render(
                previous_text,
                True,
                (255, 210, 70)
            )

            rect = rendered.get_rect(
                center=(
                    screen.get_width() // 2,
                    135
                )
            )

            screen.blit(
                rendered,
                rect
            )

        # -------------------------------------------------
        # Timer
        # -------------------------------------------------

        if (
            self.is_netplay
            and self.interactive
        ):

            remaining = max(
                0,
                int(
                    self.PICK_TIME_LIMIT
                    - self.pick_elapsed
                    + 0.999
                )
            )

            if self.selected_index is not None:

                timer_text = "SELECTED"

                timer_color = (
                    120,
                    220,
                    120
                )

            else:

                timer_text = (
                    f"{remaining}s"
                )

                if remaining <= 10:

                    timer_color = (
                        255,
                        80,
                        80
                    )

                else:

                    timer_color = (
                        255,
                        255,
                        255
                    )

            timer = self.small_font.render(
                timer_text,
                True,
                timer_color
            )

            timer_rect = timer.get_rect(
                center=(
                    screen.get_width() // 2,
                    165
                )
            )

            screen.blit(
                timer,
                timer_rect
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
                False
            )

            hovered = (
                self.interactive
                and self.cards_finished
                and self.selected_index is None
                and normal_rect.collidepoint(
                    mouse_position
                )
            )

            rect = self.get_card_rect(
                i,
                hovered
            )

            self.draw_card(
                screen,
                i,
                upgrade,
                rect,
                hovered
            )

        # -------------------------------------------------
        # Spectator message
        # -------------------------------------------------

        if not self.interactive:

            text = self.small_font.render(
                "WATCHING",
                True,
                (180, 180, 180)
            )

            rect = text.get_rect(
                center=(
                    screen.get_width() // 2,
                    195
                )
            )

            screen.blit(
                text,
                rect
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

        card_sprite = pygame.transform.smoothscale(
            self.card_sprites[rarity],
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
        # Selected outline
        # -------------------------------------------------

        if (
            self.selected_index == index
        ):

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                rect,
                4
            )

        elif hovered:

            pygame.draw.rect(
                screen,
                (255, 255, 255),
                rect,
                2
            )

        rarity_color = (
            self.RARITY_COLORS.get(
                rarity,
                (255, 255, 255)
            )
        )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name = self.name_font.render(
            upgrade.name,
            True,
            rarity_color
            if rarity == "super rare"
            else (255, 255, 255)
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
        # Upgrade sprite
        # -------------------------------------------------

        upgrade_sprite = (
            self.upgrade_sprites[index]
        )

        if upgrade_sprite is not None:

            image = pygame.transform.smoothscale(
                upgrade_sprite,
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