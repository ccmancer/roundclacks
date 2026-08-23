import pygame

from game.states.state import State
from weapons.sword import Sword
from weapons.bow import Bow
from weapons.bomb import Bomb
from weapons.grimoire import Grimoire
from weapons.unarmed import Unarmed

class WeaponSelectState(State):

    WEAPONS = [
        Sword,
        Bow,
        Bomb,
        Grimoire,
        Unarmed
    ]

    def __init__(self, game):
        super().__init__(game)

        self.player_number = 1
        self.selected = 0

        self.player1_weapon = None
        self.player2_weapon = None

        self.font = pygame.font.Font(None, 50)

    def handle_events(self, events):
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_UP:
                self.selected = (
                    self.selected - 1
                ) % len(self.WEAPONS)

            elif event.key == pygame.K_DOWN:
                self.selected = (
                    self.selected + 1
                ) % len(self.WEAPONS)

            elif event.key == pygame.K_RETURN:
                self.confirm_selection()

            elif event.key == pygame.K_ESCAPE:
                # Go back to main menu
                from game.states.main_menu import MainMenuState

                self.game.state = MainMenuState(self.game)

    def confirm_selection(self):
        weapon = self.WEAPONS[self.selected]

        if self.player_number == 1:
            self.player1_weapon = weapon
            self.player_number = 2
            self.selected = 0

        else:
            self.player2_weapon = weapon

            self.game.start_local_match(
                self.player1_weapon,
                self.player2_weapon
            )

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill("white")

        title = self.font.render(
            f"Player {self.player_number} - Choose Weapon",
            True,
            "black"
        )

        screen.blit(
            title,
            (
                screen.get_width() // 2 - title.get_width() // 2,
                100
            )
        )

        for i, weapon in enumerate(self.WEAPONS):
            selected = i == self.selected

            color = "red" if selected else "black"

            text = self.font.render(
                weapon.__name__,
                True,
                color
            )

            screen.blit(
                text,
                (
                    screen.get_width() // 2 - text.get_width() // 2,
                    250 + i * 70
                )
            )