import pygame
from pathlib import Path

from game.states.state import State
from game.states.opponent_left import OpponentLeftState

from weapons.sword import Sword
from weapons.bow import Bow
from weapons.bomb import Bomb
from weapons.grimoire import Grimoire
from weapons.unarmed import Unarmed

from ui.button import Button
from ui.weapon_icon import WeaponIcon


SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent.parent
    / "assets"
    / "audio"
    / "ui"
)


class NetplayWeaponSelectState(State):

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
        game,
        client,
        is_host=False,
        server=None
    ):
        super().__init__(
            game
        )

        self.client = client
        self.is_host = is_host
        self.server = server

        self.game.audio.play_music(
            "character_select"
        )

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.character_select_sound = (
            self.game.audio.load_ui_sound(
                SOUND_FOLDER
                / "character_select.mp3"
            )
        )

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
        # Network player number
        #
        # This determines the gameplay side only.
        # It does NOT determine which local settings
        # profile is used.
        # -------------------------------------------------

        self.player_number = (
            self.client.player_number
        )

        # -------------------------------------------------
        # Selection
        # -------------------------------------------------

        self.my_weapon = None
        self.opponent_weapon = None

        self.my_ready = False
        self.opponent_ready = False

        self.started = False

        # -------------------------------------------------
        # Opponent identity
        # -------------------------------------------------

        self.opponent_name = "Opponent"

        self.opponent_color = (
            100,
            100,
            100
        )

        # -------------------------------------------------
        # Match
        # -------------------------------------------------

        self.match_seed = None

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
        # Send this machine's player1 settings.
        #
        # Both network players use their OWN local
        # player1 profile.
        # -------------------------------------------------

        self.send_player_info()

    # -------------------------------------------------
    # LOCAL NETPLAY IDENTITY
    # -------------------------------------------------

    def get_local_name(
        self
    ):
        return (
            self.game.settings.player1_name
        )

    def get_local_color(
        self
    ):
        return tuple(
            self.game.settings.player1_color
        )

    # -------------------------------------------------
    # PLAYER INFO
    # -------------------------------------------------

    def send_player_info(
        self
    ):
        if self.client is None:
            return

        self.client.send(
            {
                "type": "player_info",
                "name": self.get_local_name(),
                "color": list(
                    self.get_local_color()
                )
            }
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
            # Window close
            # -------------------------------------------------

            if event.type == pygame.QUIT:

                self.client.close()

                if (
                    self.is_host
                    and self.server is not None
                ):

                    self.server.stop()

                    self.server = None

                self.game.running = False

                return

            # -------------------------------------------------
            # Back
            # -------------------------------------------------

            if self.back_button.clicked(
                event
            ):

                self.client.close()

                if (
                    self.is_host
                    and self.server is not None
                ):

                    self.server.stop()

                    self.server = None

                self.game.return_to_main_menu()

                return

            if self.started:
                continue

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
                self.my_weapon is not None
                and not self.my_ready
                and self.ready_button.clicked(
                    event
                )
            ):

                self.my_ready = True

                self.client.send(
                    {
                        "type": "ready"
                    }
                )

    # -------------------------------------------------
    # SELECT WEAPON
    # -------------------------------------------------

    def select_weapon(
        self,
        index
    ):
        if self.my_ready:
            return

        if (
            index < 0
            or index >= len(self.WEAPONS)
        ):
            return

        weapon = self.WEAPONS[
            index
        ]

        self.my_weapon = weapon

        self.character_select_sound.play()

        self.client.send(
            {
                "type": "weapon_select",
                "weapon": weapon.__name__
            }
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

        messages = (
            self.client.update()
        )

        for message in messages:

            if not isinstance(
                message,
                dict
            ):
                continue

            message_type = message.get(
                "type"
            )

            # -------------------------------------------------
            # Opponent left
            # -------------------------------------------------

            if message_type == "opponent_left":

                self.client.close()

                self.game.state = (
                    OpponentLeftState(
                        self.game,
                        self.opponent_name,
                        self.opponent_color
                    )
                )

                self.game.simulation_accumulator = 0

                return

            # -------------------------------------------------
            # Player information
            # -------------------------------------------------

            elif message_type == "player_info":

                player = message.get(
                    "player"
                )

                remote_player = (
                    2
                    if self.player_number == 1
                    else 1
                )

                if player != remote_player:
                    continue

                name = message.get(
                    "name"
                )

                color = message.get(
                    "color"
                )

                if isinstance(
                    name,
                    str
                ):

                    self.opponent_name = name

                if (
                    isinstance(
                        color,
                        list
                    )
                    and len(color) == 3
                    and all(
                        isinstance(
                            value,
                            int
                        )
                        and 0 <= value <= 255
                        for value in color
                    )
                ):

                    self.opponent_color = tuple(
                        color
                    )

            # -------------------------------------------------
            # Opponent weapon
            # -------------------------------------------------

            elif message_type == "weapon_state":

                player = message.get(
                    "player"
                )

                if player == self.player_number:
                    continue

                self.opponent_weapon = (
                    self.get_weapon_class(
                        message.get(
                            "weapon"
                        )
                    )
                )

            # -------------------------------------------------
            # Ready state
            # -------------------------------------------------

            elif message_type == "ready_state":

                player = message.get(
                    "player"
                )

                if player == self.player_number:
                    continue

                self.opponent_ready = (
                    message.get(
                        "ready",
                        False
                    )
                )

            # -------------------------------------------------
            # Start match
            # -------------------------------------------------

            elif message_type == "start_match":

                if self.started:
                    continue

                self.started = True

                self.match_seed = (
                    message.get(
                        "seed"
                    )
                )

                player1_weapon = (
                    self.get_weapon_class(
                        message.get(
                            "player1_weapon"
                        )
                    )
                )

                player2_weapon = (
                    self.get_weapon_class(
                        message.get(
                            "player2_weapon"
                        )
                    )
                )

                player1_info = (
                    message.get(
                        "player1_info"
                    )
                )

                player2_info = (
                    message.get(
                        "player2_info"
                    )
                )

                self.game.start_netplay_match(
                    player1_weapon,
                    player2_weapon,
                    self.match_seed,
                    player1_info,
                    player2_info,
                    self.client,
                    self.server
                )

                return

    # -------------------------------------------------
    # WEAPON HELPERS
    # -------------------------------------------------

    def get_weapon_class(
        self,
        name
    ):
        weapon_classes = {
            "Sword": Sword,
            "Bow": Bow,
            "Bomb": Bomb,
            "Grimoire": Grimoire,
            "Unarmed": Unarmed
        }

        return weapon_classes.get(
            name
        )

    # -------------------------------------------------
    # OUTLINED TEXT
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
    # DRAW SELECTED WEAPON
    # -------------------------------------------------

    def draw_selected_weapon(
        self,
        screen,
        weapon_class,
        center_x,
        center_y,
        color
    ):
        player = (
            1
            if center_x < screen.get_width() // 2
            else 2
        )

        rect = self.get_selected_weapon_rect(
            player
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
                if icon.weapon_class
                is weapon_class
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

        my_color = (
            self.get_local_color()
        )

        my_name = (
            self.get_local_name()
        )

        opponent_color = (
            self.opponent_color
        )

        # -------------------------------------------------
        # TITLE
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
        # LOCAL PLAYER
        # -------------------------------------------------

        current_text = (
            "READY"
            if self.my_ready
            else "CHOOSE"
        )

        self.draw_outlined_text(
            screen,
            f"{my_name} - {current_text}",
            self.small_font,
            (
                screen_width // 2,
                230
            ),
            my_color
        )

        # -------------------------------------------------
        # WEAPON ICONS
        # -------------------------------------------------

        for icon in self.weapon_icons:

            rect = icon.get_rect()

            my_selected = (
                self.my_weapon
                is icon.weapon_class
            )

            opponent_selected = (
                self.opponent_weapon
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

            if my_selected:

                pygame.draw.rect(
                    screen,
                    my_color,
                    rect,
                    4
                )

            if opponent_selected:

                pygame.draw.rect(
                    screen,
                    opponent_color,
                    rect,
                    4
                )

            if (
                my_selected
                and opponent_selected
            ):

                pygame.draw.rect(
                    screen,
                    my_color,
                    rect,
                    6
                )

                pygame.draw.rect(
                    screen,
                    opponent_color,
                    rect,
                    3
                )

        # -------------------------------------------------
        # SELECTED WEAPONS
        # -------------------------------------------------

        if self.player_number == 1:

            my_x = 150

            opponent_x = (
                screen_width - 150
            )

        else:

            my_x = (
                screen_width - 150
            )

            opponent_x = 150

        self.draw_selected_weapon(
            screen,
            self.my_weapon,
            my_x,
            500,
            my_color
        )

        self.draw_selected_weapon(
            screen,
            self.opponent_weapon,
            opponent_x,
            500,
            opponent_color
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        my_status = (
            "READY"
            if self.my_ready
            else "NOT READY"
        )

        opponent_status = (
            "READY"
            if self.opponent_ready
            else "WAITING"
        )

        my_text = self.small_font.render(
            my_status,
            True,
            my_color
        )

        opponent_text = self.small_font.render(
            opponent_status,
            True,
            opponent_color
        )

        screen.blit(
            my_text,
            my_text.get_rect(
                center=(
                    my_x,
                    430
                )
            )
        )

        screen.blit(
            opponent_text,
            opponent_text.get_rect(
                center=(
                    opponent_x,
                    430
                )
            )
        )

        # -------------------------------------------------
        # OPPONENT NAME
        # -------------------------------------------------

        opponent_name_text = (
            self.small_font.render(
                self.opponent_name,
                True,
                opponent_color
            )
        )

        screen.blit(
            opponent_name_text,
            opponent_name_text.get_rect(
                center=(
                    opponent_x,
                    230
                )
            )
        )

        # -------------------------------------------------
        # READY BUTTON
        # -------------------------------------------------

        if (
            self.my_weapon is not None
            and not self.my_ready
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
        # BACK
        # -------------------------------------------------

        self.back_button.draw(
            screen
        )

        # -------------------------------------------------
        # HINT
        # -------------------------------------------------

        if (
            self.my_weapon is not None
            and not self.my_ready
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