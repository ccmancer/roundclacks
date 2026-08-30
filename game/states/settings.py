import pygame

from game.states.state import State
from ui.button import Button
from game.states.text_input import TextInputState


class SettingsState(State):

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

        self.game.audio.play_music(
            "settings"
        )

        self.font = pygame.font.Font(
            None,
            40
        )

        self.small_font = pygame.font.Font(
            None,
            25
        )

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------

        self.master_down = Button(
            "-",
            (
                250,
                130,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.master_up = Button(
            "+",
            (
                425,
                130,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.game_down = Button(
            "-",
            (
                250,
                190,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.game_up = Button(
            "+",
            (
                425,
                190,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.ui_down = Button(
            "-",
            (
                250,
                250,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.ui_up = Button(
            "+",
            (
                425,
                250,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.music_down = Button(
            "-",
            (
                250,
                310,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.music_up = Button(
            "+",
            (
                425,
                310,
                45,
                45
            ),
            font_size=30,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Player settings
        # -------------------------------------------------

        self.p1_color = Button(
            "P1 Colour",
            (
                180,
                400,
                160,
                50
            ),
            font_size=24,
            audio=self.game.audio
        )

        self.p2_color = Button(
            "P2 Colour",
            (
                380,
                400,
                160,
                50
            ),
            font_size=24,
            audio=self.game.audio
        )

        self.p1_name = Button(
            "P1 Name",
            (
                180,
                500,
                160,
                50
            ),
            font_size=24,
            audio=self.game.audio
        )

        self.p2_name = Button(
            "P2 Name",
            (
                380,
                500,
                160,
                50
            ),
            font_size=24,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Reset / Back
        # -------------------------------------------------

        self.reset_button = Button(
            "Reset",
            (
                300,
                600,
                120,
                45
            ),
            font_size=25,
            audio=self.game.audio
        )

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

        self.buttons = [
            self.master_down,
            self.master_up,
            self.game_down,
            self.game_up,
            self.ui_down,
            self.ui_up,
            self.music_down,
            self.music_up,
            self.p1_color,
            self.p2_color,
            self.p1_name,
            self.p2_name,
            self.reset_button,
            self.back_button
        ]

        self.current_state = self

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        if self.current_state is not self:
            self.current_state.handle_events(
                events
            )
            return

        for event in events:

            if self.back_button.clicked(event):
                self.game.return_to_main_menu()
                continue

            if self.reset_button.clicked(event):
                self.game.settings.reset()
                self.game.audio.update()
                continue

            if self.master_down.clicked(event):
                self.game.settings.set_master_volume(
                    self.game.settings.master_volume - 0.1
                )

            elif self.master_up.clicked(event):
                self.game.settings.set_master_volume(
                    self.game.settings.master_volume + 0.1
                )

            elif self.game_down.clicked(event):
                self.game.settings.set_game_volume(
                    self.game.settings.game_volume - 0.1
                )

            elif self.game_up.clicked(event):
                self.game.settings.set_game_volume(
                    self.game.settings.game_volume + 0.1
                )

            elif self.ui_down.clicked(event):
                self.game.settings.set_ui_volume(
                    self.game.settings.ui_volume - 0.1
                )

            elif self.ui_up.clicked(event):
                self.game.settings.set_ui_volume(
                    self.game.settings.ui_volume + 0.1
                )

            elif self.music_down.clicked(event):
                self.game.settings.set_music_volume(
                    self.game.settings.music_volume - 0.1
                )

            elif self.music_up.clicked(event):
                self.game.settings.set_music_volume(
                    self.game.settings.music_volume + 0.1
                )

            elif self.p1_color.clicked(event):
                self.open_rgb_input(1)

            elif self.p2_color.clicked(event):
                self.open_rgb_input(2)

            elif self.p1_name.clicked(event):
                self.open_name_input(1)

            elif self.p2_name.clicked(event):
                self.open_name_input(2)

    # -------------------------------------------------
    # RGB
    # -------------------------------------------------

    def open_rgb_input(
        self,
        player
    ):
        if player == 1:
            current = self.game.settings.player1_color
            title = "PLAYER 1 COLOUR"

            def save(value):
                self.set_color(
                    1,
                    value
                )

        else:
            current = self.game.settings.player2_color
            title = "PLAYER 2 COLOUR"

            def save(value):
                self.set_color(
                    2,
                    value
                )

        initial_text = ",".join(
            str(value)
            for value in current
        )

        self.current_state = TextInputState(
            self,
            title,
            initial_text,
            "rgb",
            save
        )

    def set_color(
        self,
        player,
        text
    ):
        values = tuple(
            int(value.strip())
            for value in text.split(",")
        )

        if player == 1:
            self.game.settings.player1_color = values
        else:
            self.game.settings.player2_color = values

        self.game.settings.save()

    # -------------------------------------------------
    # NAME
    # -------------------------------------------------

    def open_name_input(
        self,
        player
    ):
        if player == 1:
            current = self.game.settings.player1_name
            title = "PLAYER 1 NAME"

            def save(value):
                self.game.settings.player1_name = (
                    value.strip()
                )
                self.game.settings.save()

        else:
            current = self.game.settings.player2_name
            title = "PLAYER 2 NAME"

            def save(value):
                self.game.settings.player2_name = (
                    value.strip()
                )
                self.game.settings.save()

        self.current_state = TextInputState(
            self,
            title,
            current,
            "text",
            save
        )

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        if self.current_state is not self:
            self.current_state.update(dt)
            return

        mouse_position = pygame.mouse.get_pos()

        for button in self.buttons:
            button.update(
                mouse_position
            )

    # -------------------------------------------------
    # DRAW HELPERS
    # -------------------------------------------------

    def draw_volume(
        self,
        screen,
        name,
        value,
        y
    ):
        text = self.small_font.render(
            f"{name}: {int(value * 100)}%",
            True,
            "black"
        )

        screen.blit(
            text,
            (
                100,
                y + 10
            )
        )

    def format_rgb(
        self,
        color
    ):
        return (
            f"RGB: "
            f"{color[0]}, "
            f"{color[1]}, "
            f"{color[2]}"
        )

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        if self.current_state is not self:
            self.current_state.draw(screen)
            return

        screen.fill(
            "white"
        )

        title = self.font.render(
            "SETTINGS",
            True,
            "black"
        )

        title_rect = title.get_rect(
            center=(
                screen.get_width() // 2,
                40
            )
        )

        screen.blit(
            title,
            title_rect
        )

        settings = self.game.settings

        self.draw_volume(
            screen,
            "Master",
            settings.master_volume,
            130
        )

        self.draw_volume(
            screen,
            "Game SFX",
            settings.game_volume,
            190
        )

        self.draw_volume(
            screen,
            "UI SFX",
            settings.ui_volume,
            250
        )

        self.draw_volume(
            screen,
            "Music",
            settings.music_volume,
            310
        )

        for button in self.buttons:
            button.draw(screen)

        p1_color = self.small_font.render(
            self.format_rgb(
                settings.player1_color
            ),
            True,
            settings.player1_color
        )

        p2_color = self.small_font.render(
            self.format_rgb(
                settings.player2_color
            ),
            True,
            settings.player2_color
        )

        screen.blit(
            p1_color,
            (180, 455)
        )

        screen.blit(
            p2_color,
            (380, 455)
        )

        name1 = self.small_font.render(
            settings.player1_name,
            True,
            "black"
        )

        name2 = self.small_font.render(
            settings.player2_name,
            True,
            "black"
        )

        screen.blit(
            name1,
            (180, 555)
        )

        screen.blit(
            name2,
            (380, 555)
        )