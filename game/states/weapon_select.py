import pygame

from game.states.state import State

from weapons.sword import Sword
from weapons.bow import Bow
from weapons.bomb import Bomb
from weapons.grimoire import Grimoire
from weapons.unarmed import Unarmed

from ui.button import Button
from ui.weapon_icon import WeaponIcon


class WeaponSelectState(State):

    WEAPONS = [
        Sword,
        Bow,
        Bomb,
        Grimoire,
        Unarmed
    ]

    ICON_SIZE = 100
    ICON_GAP = 20

    SELECTED_ICON_SIZE = 110

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

        self.game.audio.play_music(
            "character_select"
        )

        # -------------------------------------------------
        # Selection
        # -------------------------------------------------

        self.player_number = 1

        self.player1_weapon = None
        self.player2_weapon = None

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.font = pygame.font.Font(
            None,
            50
        )

        self.small_font = pygame.font.Font(
            None,
            28
        )

        # -------------------------------------------------
        # Sounds
        # -------------------------------------------------

        self.character_select_sound = (
            self.game.audio.load_ui_sound(
                "character_select.mp3"
            )
        )

        # -------------------------------------------------
        # Weapon icons
        # -------------------------------------------------

        total_width = (
            len(self.WEAPONS)
            * self.ICON_SIZE
            + (
                len(self.WEAPONS) - 1
            )
            * self.ICON_GAP
        )

        start_x = (
            self.game.screen.get_width()
            - total_width
        ) // 2

        self.weapon_icons = []

        for i, weapon in enumerate(
            self.WEAPONS
        ):
            x = (
                start_x
                + i
                * (
                    self.ICON_SIZE
                    + self.ICON_GAP
                )
            )

            self.weapon_icons.append(
                WeaponIcon(
                    weapon,
                    (
                        x,
                        300
                    )
                )
            )

        # -------------------------------------------------
        # Ready
        # -------------------------------------------------

        self.ready_button = Button(
            "READY",
            (
                260,
                500,
                200,
                60
            ),
            font_size=30,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Back
        # -------------------------------------------------

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

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            # -------------------------------------------------
            # Back
            # -------------------------------------------------

            if self.back_button.clicked(
                event
            ):
                from game.states.main_menu import (
                    MainMenuState
                )

                self.game.state = MainMenuState(
                    self.game
                )

                return

            # -------------------------------------------------
            # Change Player 1 selection
            # -------------------------------------------------

            if (
                self.player1_weapon is not None
                and self.get_selected_weapon_rect(
                    1
                ).collidepoint(
                    pygame.mouse.get_pos()
                )
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.player1_weapon = None
                self.player_number = 1

                return

            # -------------------------------------------------
            # Change Player 2 selection
            # -------------------------------------------------

            if (
                self.player2_weapon is not None
                and self.get_selected_weapon_rect(
                    2
                ).collidepoint(
                    pygame.mouse.get_pos()
                )
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.player2_weapon = None
                self.player_number = 2

                return

            # -------------------------------------------------
            # Weapon selection
            # -------------------------------------------------

            for i, icon in enumerate(
                self.weapon_icons
            ):

                if icon.clicked(
                    event
                ):
                    self.select_weapon(
                        i
                    )

                    return

            # -------------------------------------------------
            # Ready
            # -------------------------------------------------

            if (
                self.player1_weapon is not None
                and self.player2_weapon is not None
                and self.ready_button.clicked(
                    event
                )
            ):
                self.game.start_local_match(
                    self.player1_weapon,
                    self.player2_weapon
                )

    # -------------------------------------------------
    # SELECT WEAPON
    # -------------------------------------------------

    def select_weapon(
        self,
        index
    ):
        weapon = self.WEAPONS[index]

        # -------------------------------------------------
        # Player 1
        # -------------------------------------------------

        if self.player_number == 1:

            self.player1_weapon = weapon
            self.player_number = 2

            self.character_select_sound.play()

            return

        # -------------------------------------------------
        # Player 2
        # -------------------------------------------------

        self.player2_weapon = weapon

        self.character_select_sound.play()

    # -------------------------------------------------
    # SELECTED WEAPON RECT
    # -------------------------------------------------

    def get_selected_weapon_rect(
        self,
        player
    ):
        screen_width = (
            self.game.screen.get_width()
        )

        if player == 1:
            center_x = 150
        else:
            center_x = (
                screen_width - 150
            )

        center_y = 500

        return pygame.Rect(
            int(
                center_x
                - self.SELECTED_ICON_SIZE / 2
            ),
            int(
                center_y
                - self.SELECTED_ICON_SIZE / 2
            ),
            self.SELECTED_ICON_SIZE,
            self.SELECTED_ICON_SIZE
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        mouse_position = pygame.mouse.get_pos()

        for icon in self.weapon_icons:
            icon.update(
                mouse_position
            )

        self.ready_button.update(
            mouse_position
        )

        self.back_button.update(
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
        color
    ):
        outline = font.render(
            text,
            True,
            (0, 0, 0)
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
            -2,
            3
        ):

            for dy in range(
                -2,
                3
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

        p1_color = (
            self.game.settings.player1_color
        )

        p2_color = (
            self.game.settings.player2_color
        )

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = self.font.render(
            "CHOOSE YOUR WEAPON",
            True,
            "black"
        )

        title_rect = title.get_rect(
            center=(
                screen_width // 2,
                70
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # Determine current player
        # -------------------------------------------------

        if (
            self.player1_weapon is None
            and self.player2_weapon is not None
        ):
            self.player_number = 1

        if (
            self.player2_weapon is None
            and self.player1_weapon is not None
        ):
            self.player_number = 2

        if self.player_number == 1:

            current_name = (
                self.game.settings.player1_name
            )

            current_color = p1_color

        else:

            current_name = (
                self.game.settings.player2_name
            )

            current_color = p2_color

        self.draw_outlined_text(
            screen,
            f"{current_name} - CHOOSE",
            self.small_font,
            (
                screen_width // 2,
                230
            ),
            current_color
        )

        # -------------------------------------------------
        # Weapon icons
        # -------------------------------------------------

        for icon in self.weapon_icons:

            rect = icon.get_rect()

            p1_selected = (
                self.player1_weapon
                is icon.weapon_class
            )

            p2_selected = (
                self.player2_weapon
                is icon.weapon_class
            )

            icon.draw(
                screen,
                (
                    255,
                    255,
                    255
                ),
                3
            )

            if p1_selected:

                pygame.draw.rect(
                    screen,
                    p1_color,
                    rect,
                    4
                )

            if p2_selected:

                pygame.draw.rect(
                    screen,
                    p2_color,
                    rect,
                    4
                )

            if (
                p1_selected
                and p2_selected
            ):

                pygame.draw.rect(
                    screen,
                    p1_color,
                    rect,
                    6
                )

                pygame.draw.rect(
                    screen,
                    p2_color,
                    rect,
                    3
                )

        # -------------------------------------------------
        # Selected weapons
        # -------------------------------------------------

        self.draw_selected_weapon(
            screen,
            self.player1_weapon,
            150,
            500,
            p1_color
        )

        self.draw_selected_weapon(
            screen,
            self.player2_weapon,
            screen_width - 150,
            500,
            p2_color
        )

        # -------------------------------------------------
        # Ready
        # -------------------------------------------------

        if (
            self.player1_weapon is not None
            and self.player2_weapon is not None
        ):

            self.ready_button.draw(
                screen
            )

        else:

            locked_rect = pygame.Rect(
                260,
                500,
                200,
                60
            )

            pygame.draw.rect(
                screen,
                (180, 180, 180),
                locked_rect
            )

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                locked_rect,
                2
            )

            locked_text = self.small_font.render(
                "READY",
                True,
                (100, 100, 100)
            )

            screen.blit(
                locked_text,
                locked_text.get_rect(
                    center=locked_rect.center
                )
            )

        # -------------------------------------------------
        # Back
        # -------------------------------------------------

        self.back_button.draw(
            screen
        )

        # -------------------------------------------------
        # Hint
        # -------------------------------------------------

        if (
            self.player1_weapon is not None
            or self.player2_weapon is not None
        ):

            hint = self.small_font.render(
                "Click your selected weapon to change it",
                True,
                (90, 90, 90)
            )

            hint_rect = hint.get_rect(
                center=(
                    screen_width // 2,
                    620
                )
            )

            screen.blit(
                hint,
                hint_rect
            )

    # -------------------------------------------------
    # SELECTED WEAPON
    # -------------------------------------------------

    def draw_selected_weapon(
        self,
        screen,
        weapon_class,
        center_x,
        center_y,
        color
    ):
        rect = self.get_selected_weapon_rect(
            1
            if center_x < screen.get_width() // 2
            else 2
        )

        if weapon_class is None:

            pygame.draw.rect(
                screen,
                (210, 210, 210),
                rect
            )

            pygame.draw.rect(
                screen,
                (120, 120, 120),
                rect,
                2
            )

            return

        icon = next(
            (
                icon
                for icon in self.weapon_icons
                if icon.weapon_class is weapon_class
            ),
            None
        )

        if icon is None:
            return

        if icon.sprite is None:
            return

        sprite = pygame.transform.smoothscale(
            icon.sprite,
            (
                90,
                90
            )
        )

        sprite_rect = sprite.get_rect(
            center=(
                center_x,
                center_y
            )
        )

        screen.blit(
            sprite,
            sprite_rect
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            4
        )

        name = self.small_font.render(
            weapon_class.__name__,
            True,
            color
        )

        name_rect = name.get_rect(
            center=(
                center_x,
                center_y + 70
            )
        )

        screen.blit(
            name,
            name_rect
        )