import pygame

from entities.player import Player

from game.match import Match
from game.states.state import State
from game.states.round import RoundState
from game.states.netplay_winner import NetplayWinnerState
from game.states.opponent_left import OpponentLeftState
from game.states.upgrade_select import UpgradeSelectState

from network.input import FrameInput
from network.snapshot import GameSnapshot


class NetplayMatchState(State):

    SNAPSHOT_HISTORY = 120

    def __init__(
        self,
        game,
        player1_weapon,
        player2_weapon,
        seed,
        player1_info,
        player2_info,
        client,
        server=None
    ):
        super().__init__(
            game
        )

        self.is_simulation_state = False

        self.client = client

        self.server = server

        self.game.audio.play_music(
            "match"
        )

        # -------------------------------------------------
        # Network identity
        # -------------------------------------------------

        self.local_player_number = (
            self.client.player_number
        )

        # -------------------------------------------------
        # Server-provided network identities
        # -------------------------------------------------

        player1_info = (
            player1_info
            if isinstance(
                player1_info,
                dict
            )
            else {}
        )

        player2_info = (
            player2_info
            if isinstance(
                player2_info,
                dict
            )
            else {}
        )

        player1_name = player1_info.get(
            "name",
            "Player 1"
        )

        player1_color = tuple(
            player1_info.get(
                "color",
                (255, 0, 0)
            )
        )

        player2_name = player2_info.get(
            "name",
            "Player 1"
        )

        player2_color = tuple(
            player2_info.get(
                "color",
                (255, 0, 0)
            )
        )

        # -------------------------------------------------
        # Players
        # -------------------------------------------------

        self.player1 = Player(
            self.game,
            150,
            360,
            40,
            player1_color,
            375,
            player1_weapon,
            pygame.K_SPACE,
            player1_name
        )

        self.player2 = Player(
            self.game,
            570,
            360,
            40,
            player2_color,
            375,
            player2_weapon,
            pygame.K_SPACE,
            player2_name
        )

        self.player1.player_number = 1
        self.player2.player_number = 2

        self.player1.opponent = (
            self.player2
        )

        self.player2.opponent = (
            self.player1
        )

        # -------------------------------------------------
        # Match
        # -------------------------------------------------

        self.match = Match(
            self.player1,
            self.player2,
            seed=seed
        )

        self.player1.match = (
            self.match
        )

        self.player2.match = (
            self.match
        )

        self.match.set_round(
            1
        )

        self.player1.simulation_frame = 0
        self.player2.simulation_frame = 0

        # -------------------------------------------------
        # Score
        # -------------------------------------------------

        self.player1_wins = 0
        self.player2_wins = 0
        self.round_number = 1

        # -------------------------------------------------
        # Current state
        # -------------------------------------------------

        self.current_state = None

        # -------------------------------------------------
        # Upgrade
        # -------------------------------------------------

        self.upgrade_phase_active = True
        self.upgrade_selector = 1
        self.upgrade_selected_sent = False

        # -------------------------------------------------
        # Local input
        # -------------------------------------------------

        self.local_attack_held = False
        self.local_inputs = {}

        # -------------------------------------------------
        # Prediction
        # -------------------------------------------------

        self.predicted_remote_inputs = {}

        self.last_known_remote_input = (
            FrameInput(
                0,
                False
            )
        )

        # -------------------------------------------------
        # Snapshots
        # -------------------------------------------------

        self.snapshots = {}

        # -------------------------------------------------
        # Rollback
        # -------------------------------------------------

        self.is_rollback_replaying = False

        # -------------------------------------------------
        # Round transition
        # -------------------------------------------------

        self.round_result_sent = False
        self.waiting_for_round_result = False

        # -------------------------------------------------
        # Match over
        # -------------------------------------------------

        self.match_over = False

        # -------------------------------------------------
        # Initial upgrade
        # -------------------------------------------------

        self.start_upgrade_selection(
            1
        )

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_events(
        self,
        events
    ):
        if self.match_over:

            if self.current_state is not None:

                self.current_state.handle_events(
                    events
                )

            return

        if self.upgrade_phase_active:

            if self.current_state is not None:

                self.current_state.handle_events(
                    events
                )

            return

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.close()

                    return

                if event.key == pygame.K_SPACE:

                    self.local_attack_held = True

            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_SPACE:

                    self.local_attack_held = False

    # -------------------------------------------------
    # LOCAL INPUT
    # -------------------------------------------------

    def get_local_input(
        self,
        frame
    ):
        existing = (
            self.local_inputs.get(
                frame
            )
        )

        if existing is not None:

            return existing

        frame_input = FrameInput(
            frame,
            self.local_attack_held
        )

        self.local_inputs[
            frame
        ] = frame_input

        return frame_input

    # -------------------------------------------------
    # REMOTE PLAYER
    # -------------------------------------------------

    def get_remote_player_number(
        self
    ):
        return (
            2
            if self.local_player_number == 1
            else 1
        )

    # -------------------------------------------------
    # UPGRADE
    # -------------------------------------------------

    def start_upgrade_selection(
        self,
        player_number,
        previous_upgrade=None
    ):
        self.upgrade_phase_active = True
        self.is_simulation_state = False

        self.upgrade_selector = (
            player_number
        )

        self.upgrade_selected_sent = False

        selecting = (
            player_number
            == self.local_player_number
        )

        player = (
            self.player1
            if player_number == 1
            else self.player2
        )

        self.current_state = (
            UpgradeSelectState(
                self,
                player,
                interactive=selecting,
                previous_upgrade=previous_upgrade
            )
        )

    def upgrade_selected(
        self,
        upgrade
    ):
        if not self.upgrade_phase_active:
            return

        if self.upgrade_selected_sent:
            return

        if self.upgrade_selector != (
            self.local_player_number
        ):
            return

        self.upgrade_selected_sent = True

        self.client.send(
            {
                "type": "upgrade_select",
                "round": self.round_number,
                "upgrade": upgrade.name
            }
        )

    def apply_upgrade(
        self,
        player_number,
        upgrade_name
    ):
        player = (
            self.player1
            if player_number == 1
            else self.player2
        )

        for upgrade in (
            player.weapon.upgrade_pool
        ):

            if upgrade.name == upgrade_name:

                player.weapon.add_upgrade(
                    upgrade
                )

                return

    def handle_upgrade_reveal(
        self,
        message
    ):
        if message.get(
            "type"
        ) != "upgrade_reveal":
            return

        if message.get(
            "round"
        ) != self.round_number:
            return

        player_number = message.get(
            "player"
        )

        upgrade_name = message.get(
            "upgrade"
        )

        if player_number not in (
            1,
            2
        ):
            return

        if not isinstance(
            upgrade_name,
            str
        ):
            return

        self.apply_upgrade(
            player_number,
            upgrade_name
        )

        if (
            self.current_state is not None
            and isinstance(
                self.current_state,
                UpgradeSelectState
            )
            and self.upgrade_selector
            == player_number
        ):

            self.current_state.reveal_upgrade(
                upgrade_name
            )

    # -------------------------------------------------
    # START ROUND
    # -------------------------------------------------

    def handle_start_round(
        self,
        message
    ):
        if message.get(
            "type"
        ) != "start_round":
            return

        round_number = message.get(
            "round"
        )

        if round_number != self.round_number:
            return

        self.begin_round()

    def begin_round(
        self
    ):
        self.upgrade_phase_active = False
        self.upgrade_selector = None
        self.upgrade_selected_sent = False

        self.is_simulation_state = True

        self.match.set_round(
            self.round_number
        )

        self.local_inputs.clear()
        self.predicted_remote_inputs.clear()

        self.last_known_remote_input = (
            FrameInput(
                0,
                False
            )
        )

        self.snapshots.clear()

        self.round_result_sent = False
        self.waiting_for_round_result = False

        self.local_attack_held = False

        self.client.reset_input_sequence()

        self.current_state = RoundState(
            self
        )

        self.save_snapshot()

    # -------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------

    def save_snapshot(
        self
    ):
        if not self.is_simulation_state:
            return

        frame = (
            self.current_state.simulation_frame
        )

        self.snapshots[
            frame
        ] = GameSnapshot(
            self.current_state
        )

        oldest_frame = max(
            0,
            frame - self.SNAPSHOT_HISTORY
        )

        self.snapshots = {
            snapshot_frame: snapshot
            for (
                snapshot_frame,
                snapshot
            ) in self.snapshots.items()
            if snapshot_frame >= oldest_frame
        }

    # -------------------------------------------------
    # REMOTE INPUT
    # -------------------------------------------------

    def get_remote_input(
        self,
        frame
    ):
        remote_player = (
            self.get_remote_player_number()
        )

        actual_input = (
            self.client.get_input(
                remote_player,
                frame
            )
        )

        if actual_input is not None:

            self.last_known_remote_input = (
                actual_input
            )

            return actual_input

        predicted = FrameInput(
            frame,
            self.last_known_remote_input.attack
        )

        self.predicted_remote_inputs[
            frame
        ] = predicted

        return predicted

    # -------------------------------------------------
    # ROLLBACK SEARCH
    # -------------------------------------------------

    def find_rollback_frame(
        self
    ):
        remote_player = (
            self.get_remote_player_number()
        )

        current_frame = (
            self.current_state.simulation_frame
        )

        earliest_frame = None

        for (
            frame,
            predicted
        ) in list(
            self.predicted_remote_inputs.items()
        ):

            if frame > current_frame:
                continue

            actual = (
                self.client.get_input(
                    remote_player,
                    frame
                )
            )

            if actual is None:
                continue

            if actual.attack != predicted.attack:

                if (
                    earliest_frame is None
                    or frame < earliest_frame
                ):

                    earliest_frame = frame

            else:

                del self.predicted_remote_inputs[
                    frame
                ]

                self.last_known_remote_input = (
                    actual
                )

        return earliest_frame

    # -------------------------------------------------
    # ROLLBACK
    # -------------------------------------------------

    def rollback(
        self,
        rollback_frame
    ):
        current_frame = (
            self.current_state.simulation_frame
        )

        restore_frame = (
            rollback_frame - 1
        )

        snapshot = (
            self.snapshots.get(
                restore_frame
            )
        )

        if snapshot is None:

            print(
                "ROLLBACK FAILED:",
                "missing snapshot for frame",
                restore_frame
            )

            return

        print(
            "ROLLBACK:",
            rollback_frame,
            "->",
            current_frame
        )

        self.is_rollback_replaying = True

        try:

            snapshot.restore(
                self.current_state
            )

            for frame in range(
                rollback_frame,
                current_frame + 1
            ):

                local_input = (
                    self.get_local_input(
                        frame
                    )
                )

                remote_player = (
                    self.get_remote_player_number()
                )

                actual_remote = (
                    self.client.get_input(
                        remote_player,
                        frame
                    )
                )

                if actual_remote is not None:

                    remote_input = (
                        actual_remote
                    )

                    self.last_known_remote_input = (
                        actual_remote
                    )

                    self.predicted_remote_inputs.pop(
                        frame,
                        None
                    )

                else:

                    remote_input = (
                        self.predicted_remote_inputs.get(
                            frame
                        )
                    )

                    if remote_input is None:

                        remote_input = FrameInput(
                            frame,
                            self.last_known_remote_input.attack
                        )

                        self.predicted_remote_inputs[
                            frame
                        ] = remote_input

                if self.local_player_number == 1:

                    player1_input = local_input
                    player2_input = remote_input

                else:

                    player1_input = remote_input
                    player2_input = local_input

                self.current_state.simulate_frame(
                    player1_input,
                    player2_input,
                    self.game.simulation_dt
                )

                self.save_snapshot()

        finally:

            self.is_rollback_replaying = False

    # -------------------------------------------------
    # UPDATE
    # -------------------------------------------------

    def update(
        self,
        dt
    ):
        if self.match_over:

            if self.current_state is not None:

                self.current_state.update(
                    dt
                )

            return

        messages = (
            self.client.update()
        )

        for message in messages:

            message_type = message.get(
                "type"
            )

            # -------------------------------------------------
            # Opponent left.
            # -------------------------------------------------

            if message_type == "opponent_left":

                opponent = (
                    self.player2
                    if self.local_player_number == 1
                    else self.player1
                )

                is_host = (
                    self.local_player_number == 1
                )

                if not is_host:

                    self.client.close()

                self.current_state = (
                    OpponentLeftState(
                        self.game,
                        opponent.name,
                        opponent.color,
                        client=(
                            self.client
                            if is_host
                            else None
                        ),
                        is_host=is_host,
                        server=self.server
                    )
                )

                self.upgrade_phase_active = False
                self.is_simulation_state = False
                self.match_over = True

                return

            if message_type == "start_upgrade_select":

                round_number = message.get(
                    "round"
                )

                player_number = message.get(
                    "player"
                )

                if round_number != self.round_number:
                    continue

                if player_number not in (
                    1,
                    2
                ):
                    continue

                self.start_upgrade_selection(
                    player_number
                )

            elif message_type == "upgrade_reveal":

                self.handle_upgrade_reveal(
                    message
                )

            elif message_type == "start_round":

                self.handle_start_round(
                    message
                )

            elif message_type == "round_result":

                self.handle_round_result(
                    message
                )

        if self.upgrade_phase_active:

            if self.current_state is not None:

                self.current_state.update(
                    dt
                )

            return

        if not self.is_simulation_state:

            if self.current_state is not None:

                self.current_state.update(
                    dt
                )

            return

        rollback_frame = (
            self.find_rollback_frame()
        )

        if rollback_frame is not None:

            self.rollback(
                rollback_frame
            )

        frame = (
            self.current_state.simulation_frame
            + 1
        )

        local_input = (
            self.get_local_input(
                frame
            )
        )

        self.client.send_input(
            local_input
        )

        remote_input = (
            self.get_remote_input(
                frame
            )
        )

        if self.local_player_number == 1:

            player1_input = local_input
            player2_input = remote_input

        else:

            player1_input = remote_input
            player2_input = local_input

        self.save_snapshot()

        self.current_state.simulate_frame(
            player1_input,
            player2_input,
            self.game.simulation_dt
        )

        oldest_frame = max(
            1,
            self.current_state.simulation_frame
            - self.SNAPSHOT_HISTORY
        )

        self.local_inputs = {
            frame_number: input_value
            for (
                frame_number,
                input_value
            ) in self.local_inputs.items()
            if frame_number >= oldest_frame
        }

        self.predicted_remote_inputs = {
            frame_number: input_value
            for (
                frame_number,
                input_value
            ) in self.predicted_remote_inputs.items()
            if frame_number >= oldest_frame
        }

        self.client.remove_inputs_before(
            oldest_frame
        )

    # -------------------------------------------------
    # ROUND RESULT
    # -------------------------------------------------

    def handle_round_result(
        self,
        message
    ):
        if message.get(
            "type"
        ) != "round_result":
            return

        completed_round = message.get(
            "round"
        )

        if completed_round != self.round_number:
            return

        self.player1_wins = message.get(
            "player1_wins",
            self.player1_wins
        )

        self.player2_wins = message.get(
            "player2_wins",
            self.player2_wins
        )

        self.match.player1_wins = (
            self.player1_wins
        )

        self.match.player2_wins = (
            self.player2_wins
        )

        match_over = message.get(
            "match_over",
            False
        )

        if match_over:

            winner_number = message.get(
                "winner"
            )

            winner = (
                self.player1
                if winner_number == 1
                else self.player2
            )

            self.match_over = True

            self.upgrade_phase_active = False
            self.is_simulation_state = False
            self.waiting_for_round_result = False

            self.current_state = (
                NetplayWinnerState(
                    self,
                    winner
                )
            )

            return

        self.round_number += 1

        self.match.set_round(
            self.round_number
        )

        self.upgrade_phase_active = True
        self.is_simulation_state = False

        self.current_state = None

        self.local_inputs.clear()
        self.predicted_remote_inputs.clear()

        self.last_known_remote_input = (
            FrameInput(
                0,
                False
            )
        )

        self.snapshots.clear()

        self.round_result_sent = False
        self.waiting_for_round_result = False
        self.upgrade_selected_sent = False

        self.local_attack_held = False

        self.client.reset_input_sequence()

    # -------------------------------------------------
    # ROUND FINISHED
    # -------------------------------------------------

    def round_finished(
        self,
        winner,
        loser
    ):
        if self.is_rollback_replaying:
            return

        if self.round_result_sent:
            return

        winner_number = (
            1
            if winner == self.player1
            else 2
        )

        self.round_result_sent = True
        self.waiting_for_round_result = True

        self.client.send(
            {
                "type": "round_finished",
                "round": self.round_number,
                "winner": winner_number
            }
        )

    # -------------------------------------------------
    # CLOSE
    # -------------------------------------------------

    def close(
        self
    ):
        is_host = (
            self.local_player_number
            == 1
        )

        if self.client is not None:

            self.client.leave_room()

            self.client = None

        if is_host:

            server = (
                self.server
                if self.server is not None
                else getattr(
                    self.game,
                    "netplay_server",
                    None
                )
            )

            if server is not None:

                server.stop()

            self.server = None
            self.game.netplay_server = None

        self.game.return_to_main_menu()

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(
        self,
        screen
    ):
        if self.current_state is None:
            return

        self.current_state.draw(
            screen
        )

        if not self.is_simulation_state:
            return

        local_player = (
            self.player1
            if self.local_player_number == 1
            else self.player2
        )

        font = pygame.font.Font(
            None,
            28
        )

        text = font.render(
            "YOU",
            True,
            local_player.color
        )

        outline = font.render(
            "YOU",
            True,
            (0, 0, 0)
        )

        rect = text.get_rect(
            center=(
                local_player.position.x,
                local_player.position.y
                - local_player.get_hitbox_radius()
                - 47
            )
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
                        rect.x + dx,
                        rect.y + dy
                    )
                )

        screen.blit(
            text,
            rect
        )