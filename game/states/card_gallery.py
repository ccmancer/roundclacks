import pygame

from game.states.state import State

from ui.button import Button
from ui.weapon_icon import WeaponIcon
from ui.upgrade_card import UpgradeCard

from upgrades.upgrade_pool import (
    SWORD_UPGRADES,
    BOW_UPGRADES,
    BOMB_UPGRADES,
    GRIMOIRE_UPGRADES,
    UNARMED_UPGRADES
)


class CardGalleryState(State):

    CARD_GAP = 20
    CARDS_PER_PAGE = 3

    WEAPONS = [
        ("Sword", SWORD_UPGRADES),
        ("Bow", BOW_UPGRADES),
        ("Bomb", BOMB_UPGRADES),
        ("Grimoire", GRIMOIRE_UPGRADES),
        ("Unarmed", UNARMED_UPGRADES)
    ]

    WEAPON_GAP = 15

    RARITY_COLORS = {
        "common": (255, 255, 255),
        "rare": (80, 190, 255),
        "super rare": (255, 210, 70)
    }

    def __init__(
        self,
        game
    ):
        super().__init__(
            game
        )

        self.game.audio.play_music(
            "card_gallery"
        )

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.title_font = pygame.font.Font(
            None,
            45
        )

        self.small_font = pygame.font.Font(
            None,
            20
        )

        self.odds_font = pygame.font.Font(
            None,
            18
        )

        # -------------------------------------------------
        # Weapon selection
        # -------------------------------------------------

        self.selected_weapon = 0

        self.weapon_icons = []

        total_width = (
            len(self.WEAPONS)
            * WeaponIcon.SIZE
            + (
                len(self.WEAPONS) - 1
            )
            * self.WEAPON_GAP
        )

        start_x = (
            self.game.screen.get_width()
            - total_width
        ) // 2

        for i, (
            weapon_name,
            upgrade_pool
        ) in enumerate(
            self.WEAPONS
        ):
            weapon_class = (
                self.get_weapon_class(
                    weapon_name
                )
            )

            self.weapon_icons.append(
                WeaponIcon(
                    weapon_class,
                    (
                        start_x
                        + i * (
                            WeaponIcon.SIZE
                            + self.WEAPON_GAP
                        ),
                        100
                    )
                )
            )

        # -------------------------------------------------
        # Page
        # -------------------------------------------------

        self.page = 0

        # -------------------------------------------------
        # Navigation
        # -------------------------------------------------

        self.previous_button = Button(
            "<",
            (
                30,
                650,
                60,
                50
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.next_button = Button(
            ">",
            (
                630,
                650,
                60,
                50
            ),
            font_size=30,
            audio=self.game.audio
        )

        self.back_button = Button(
            "Back",
            (
                280,
                650,
                160,
                50
            ),
            font_size=25,
            audio=self.game.audio
        )

        # -------------------------------------------------
        # Cards
        # -------------------------------------------------

        self.cards = []

        self.create_cards()

    # -------------------------------------------------
    # WEAPON HELPERS
    # -------------------------------------------------

    def get_weapon_class(
        self,
        weapon_name
    ):
        from weapons.sword import Sword
        from weapons.bow import Bow
        from weapons.bomb import Bomb
        from weapons.grimoire import Grimoire
        from weapons.unarmed import Unarmed

        weapon_classes = {
            "Sword": Sword,
            "Bow": Bow,
            "Bomb": Bomb,
            "Grimoire": Grimoire,
            "Unarmed": Unarmed
        }

        return weapon_classes[
            weapon_name
        ]

    def get_selected_upgrades(
        self
    ):
        return self.WEAPONS[
            self.selected_weapon
        ][1]

    # -------------------------------------------------
    # RARITY ODDS
    # -------------------------------------------------

    def get_rarity_odds(
        self
    ):
        rarity_weights = {
            "common": 9,
            "rare": 3,
            "super rare": 1
        }

        total_weight = sum(
            rarity_weights.values()
        )

        return {
            rarity: (
                weight
                / total_weight
                * 100
            )
            for rarity, weight
            in rarity_weights.items()
        }

    # -------------------------------------------------
    # CARD CREATION
    # -------------------------------------------------

    def create_cards(
        self
    ):
        upgrades = (
            self.get_selected_upgrades()
        )

        start = (
            self.page
            * self.CARDS_PER_PAGE
        )

        end = min(
            start + self.CARDS_PER_PAGE,
            len(upgrades)
        )

        visible = upgrades[
            start:end
        ]

        total_width = (
            len(visible)
            * UpgradeCard.WIDTH
            + (
                len(visible) - 1
            )
            * self.CARD_GAP
        )

        start_x = (
            self.game.screen.get_width()
            - total_width
        ) // 2

        card_y = 250

        self.cards = []

        for i, upgrade in enumerate(
            visible
        ):
            x = (
                start_x
                + i
                * (
                    UpgradeCard.WIDTH
                    + self.CARD_GAP
                )
            )

            card = UpgradeCard(
                upgrade,
                (
                    x,
                    card_y
                ),
                expand_direction="right"
            )

            # Use the exact same full card appearance
            # shown during a match.
            card.set_display_mode(
                "full"
            )

            card.set_hovered(
                False
            )

            self.cards.append(
                card
            )

    # -------------------------------------------------
    # PAGE
    # -------------------------------------------------

    def get_max_page(
        self
    ):
        upgrades = (
            self.get_selected_upgrades()
        )

        return max(
            0,
            (
                len(upgrades) - 1
            )
            // self.CARDS_PER_PAGE
        )

    def change_page(
        self,
        page
    ):
        max_page = (
            self.get_max_page()
        )

        self.page = max(
            0,
            min(
                page,
                max_page
            )
        )

        self.create_cards()

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        for event in events:

            # -------------------------------------------------
            # Weapon icons
            # -------------------------------------------------

            for i, icon in enumerate(
                self.weapon_icons
            ):
                if icon.clicked(
                    event
                ):
                    self.selected_weapon = i
                    self.page = 0
                    self.create_cards()
                    return

            # -------------------------------------------------
            # Previous page
            # -------------------------------------------------

            if self.previous_button.clicked(
                event
            ):
                self.change_page(
                    self.page - 1
                )
                return

            # -------------------------------------------------
            # Next page
            # -------------------------------------------------

            if self.next_button.clicked(
                event
            ):
                self.change_page(
                    self.page + 1
                )
                return

            # -------------------------------------------------
            # Back
            # -------------------------------------------------

            if self.back_button.clicked(
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
        mouse_position = (
            pygame.mouse.get_pos()
        )

        for i, icon in enumerate(
            self.weapon_icons
        ):
            icon.update(
                mouse_position
            )

            icon.selected = (
                i == self.selected_weapon
            )

        self.previous_button.update(
            mouse_position
        )

        self.next_button.update(
            mouse_position
        )

        self.back_button.update(
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
            (20, 20, 20)
        )

        screen_width = (
            screen.get_width()
        )

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = self.title_font.render(
            "GAME CARDS",
            True,
            (255, 255, 255)
        )

        title_rect = title.get_rect(
            center=(
                screen_width // 2,
                45
            )
        )

        screen.blit(
            title,
            title_rect
        )

        # -------------------------------------------------
        # Weapon icons
        # -------------------------------------------------

        for i, icon in enumerate(
            self.weapon_icons
        ):
            icon.selected = (
                i == self.selected_weapon
            )

            icon.draw(
                screen,
                outline_color=(
                    255,
                    255,
                    255
                ),
                outline_width=3
            )

            name = self.WEAPONS[
                i
            ][0]

            name_text = self.small_font.render(
                name,
                True,
                (255, 255, 255)
            )

            name_rect = name_text.get_rect(
                center=(
                    icon.get_rect().centerx,
                    icon.get_rect().bottom + 15
                )
            )

            screen.blit(
                name_text,
                name_rect
            )

        # -------------------------------------------------
        # Cards
        # -------------------------------------------------

        for card in self.cards:
            card.draw(
                screen
            )

        # -------------------------------------------------
        # Rarity odds
        # -------------------------------------------------

        odds = self.get_rarity_odds()

        rarity_order = (
            "common",
            "rare",
            "super rare"
        )

        odds_surfaces = []

        for rarity in rarity_order:

            text = self.odds_font.render(
                (
                    f"{rarity.title()}: "
                    f"{odds[rarity]:.1f}%"
                ),
                True,
                self.RARITY_COLORS[
                    rarity
                ]
            )

            odds_surfaces.append(
                text
            )

        odds_gap = 30

        total_width = (
            sum(
                text.get_width()
                for text in odds_surfaces
            )
            + odds_gap
            * (
                len(odds_surfaces)
                - 1
            )
        )

        start_x = (
            screen_width
            - total_width
        ) // 2

        odds_y = 575

        x = start_x

        for text in odds_surfaces:

            rect = text.get_rect(
                midleft=(
                    x,
                    odds_y
                )
            )

            screen.blit(
                text,
                rect
            )

            x = (
                rect.right
                + odds_gap
            )

        # -------------------------------------------------
        # Page indicator
        # -------------------------------------------------

        page_text = self.small_font.render(
            (
                f"{self.page + 1}"
                f" / "
                f"{self.get_max_page() + 1}"
            ),
            True,
            (255, 255, 255)
        )

        page_rect = page_text.get_rect(
            center=(
                screen_width // 2,
                625
            )
        )

        screen.blit(
            page_text,
            page_rect
        )

        # -------------------------------------------------
        # Navigation
        # -------------------------------------------------

        self.previous_button.draw(
            screen
        )

        self.next_button.draw(
            screen
        )

        self.back_button.draw(
            screen
        )