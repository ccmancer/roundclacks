from copy import deepcopy
from pathlib import Path

import pygame


SPRITE_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "sprites"
    / "game"
)

SOUND_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "audio"
    / "game"
)


class GameSnapshot:
    """
    Stores deterministic simulation state for rollback.

    Rendering/audio resources are excluded from snapshots and
    rebuilt when entities are restored.

    Supported entity types:

        Projectile
        Arrow
        Beam
        BearTrap
        BombProjectile
        ChaosBlade
        EarthlightRay
        Explosion
        FirePatch
        MagicSlash
        NukePool
    """

    # -------------------------------------------------
    # WEAPON FIELDS
    # -------------------------------------------------

    IGNORED_WEAPON_FIELDS = {
        "player",
        "sprite",
        "attack_sprite",
        "primed_sprite",
        "missing_sprite",
        "beam_sound",
        "beam_sound_channel",
        "dash_sound",
        "teleport_sound",
        "swing_sound",
        "shoot_sound",
        "throw_sound",
        "afterimages"
    }

    # -------------------------------------------------
    # ENTITY RENDERING / AUDIO FIELDS
    # -------------------------------------------------

    IGNORED_ENTITY_FIELDS = {
        "sprite",
        "explosion_sprite",
        "warning_sprite",
        "explosion_sound",
        "sound",
        "channel"
    }

    # -------------------------------------------------
    # INIT
    # -------------------------------------------------

    def __init__(
        self,
        round_state
    ):
        self.frame = (
            round_state.simulation_frame
        )

        self.background_time = (
            round_state.background_time
        )

        self.player1 = (
            self.capture_player(
                round_state.player1,
                round_state
            )
        )

        self.player2 = (
            self.capture_player(
                round_state.player2,
                round_state
            )
        )

        self.projectiles = []

        for projectile in (
            round_state.projectiles
        ):
            self.projectiles.append(
                self.capture_entity(
                    projectile,
                    round_state
                )
            )

        # -------------------------------------------------
        # Match seed
        # -------------------------------------------------

        match = self.get_match(
            round_state
        )

        if match is not None:

            self.match_seed = (
                getattr(
                    match,
                    "seed",
                    None
                )
            )

        else:

            self.match_seed = None

    # -------------------------------------------------
    # MATCH
    # -------------------------------------------------

    @staticmethod
    def get_match(
        round_state
    ):
        match_state = getattr(
            round_state,
            "match_state",
            None
        )

        if match_state is not None:

            return getattr(
                match_state,
                "match",
                None
            )

        return getattr(
            round_state,
            "match",
            None
        )

    # -------------------------------------------------
    # REFERENCE ENCODING
    # -------------------------------------------------

    @staticmethod
    def encode_reference(
        value,
        round_state
    ):
        # -------------------------------------------------
        # Player
        # -------------------------------------------------

        if value is round_state.player1:

            return (
                "PLAYER",
                1
            )

        if value is round_state.player2:

            return (
                "PLAYER",
                2
            )

        # -------------------------------------------------
        # Weapon
        # -------------------------------------------------

        if value is round_state.player1.weapon:

            return (
                "WEAPON",
                1
            )

        if value is round_state.player2.weapon:

            return (
                "WEAPON",
                2
            )

        # -------------------------------------------------
        # Entity
        # -------------------------------------------------

        for index, entity in enumerate(
            round_state.projectiles
        ):

            if value is entity:

                return (
                    "ENTITY",
                    index
                )

        return None

    # -------------------------------------------------
    # VALUE ENCODING
    # -------------------------------------------------

    @staticmethod
    def encode_value(
        value,
        round_state
    ):
        reference = (
            GameSnapshot.encode_reference(
                value,
                round_state
            )
        )

        if reference is not None:

            return reference

        # -------------------------------------------------
        # List
        # -------------------------------------------------

        if isinstance(
            value,
            list
        ):

            return (
                "LIST",
                [
                    GameSnapshot.encode_value(
                        item,
                        round_state
                    )
                    for item in value
                ]
            )

        # -------------------------------------------------
        # Tuple
        # -------------------------------------------------

        if isinstance(
            value,
            tuple
        ):

            return (
                "TUPLE",
                [
                    GameSnapshot.encode_value(
                        item,
                        round_state
                    )
                    for item in value
                ]
            )

        # -------------------------------------------------
        # Set
        # -------------------------------------------------

        if isinstance(
            value,
            set
        ):

            return (
                "SET",
                [
                    GameSnapshot.encode_value(
                        item,
                        round_state
                    )
                    for item in value
                ]
            )

        # -------------------------------------------------
        # Dictionary
        # -------------------------------------------------

        if isinstance(
            value,
            dict
        ):

            return (
                "DICT",
                [
                    (
                        GameSnapshot.encode_value(
                            key,
                            round_state
                        ),
                        GameSnapshot.encode_value(
                            item,
                            round_state
                        )
                    )
                    for key, item in value.items()
                ]
            )

        # -------------------------------------------------
        # Normal value
        # -------------------------------------------------

        try:

            return deepcopy(
                value
            )

        except Exception:

            return None

    # -------------------------------------------------
    # PLAYER
    # -------------------------------------------------

    @staticmethod
    def capture_player(
        player,
        round_state
    ):
        return {
            "position": (
                player.position.copy()
            ),

            "velocity": (
                player.velocity.copy()
            ),

            "external_velocity": (
                player.external_velocity.copy()
            ),

            "external_velocity_timer": (
                player.external_velocity_timer
            ),

            "health": (
                player.health
            ),

            "max_health": (
                player.max_health
            ),

            "shellshock_timer": (
                player.shellshock_timer
            ),

            "damage_flash_timer": (
                player.damage_flash_timer
            ),

            "hurt_sound_timer": (
                player.hurt_sound_timer
            ),

            # -------------------------------------------------
            # Important for rollback.
            #
            # Player.get_speed() uses pinned_arrows, and
            # Unarmed movement depends on Player.get_speed().
            # Preserve the actual Arrow references.
            # -------------------------------------------------

            "pinned_arrows": (
                GameSnapshot.encode_value(
                    player.pinned_arrows,
                    round_state
                )
            ),

            "weapon": (
                GameSnapshot.capture_weapon(
                    player.weapon,
                    round_state
                )
            )
        }

    # -------------------------------------------------
    # WEAPON
    # -------------------------------------------------

    @staticmethod
    def capture_weapon(
        weapon,
        round_state
    ):
        state = {}

        for key, value in (
            weapon.__dict__.items()
        ):

            if key in (
                GameSnapshot.IGNORED_WEAPON_FIELDS
            ):
                continue

            state[key] = (
                GameSnapshot.encode_value(
                    value,
                    round_state
                )
            )

        return state

    # -------------------------------------------------
    # ENTITY
    # -------------------------------------------------

    @staticmethod
    def capture_entity(
        entity,
        round_state
    ):
        state = {
            "class": type(entity),
            "attributes": {}
        }

        for key, value in (
            entity.__dict__.items()
        ):

            if key in (
                GameSnapshot.IGNORED_ENTITY_FIELDS
            ):
                continue

            state["attributes"][
                key
            ] = GameSnapshot.encode_value(
                value,
                round_state
            )

        return state

    # -------------------------------------------------
    # RESTORE
    # -------------------------------------------------

    def restore(
        self,
        round_state
    ):
        round_state.simulation_frame = (
            self.frame
        )

        round_state.background_time = (
            self.background_time
        )

        # -------------------------------------------------
        # Players
        # -------------------------------------------------

        self.restore_player(
            round_state.player1,
            self.player1,
            round_state
        )

        self.restore_player(
            round_state.player2,
            self.player2,
            round_state
        )

        round_state.player1.opponent = (
            round_state.player2
        )

        round_state.player2.opponent = (
            round_state.player1
        )

        # -------------------------------------------------
        # Match
        # -------------------------------------------------

        match = (
            self.get_match(
                round_state
            )
        )

        if match is not None:

            round_state.player1.match = (
                match
            )

            round_state.player2.match = (
                match
            )

            if self.match_seed is not None:

                match.seed = (
                    self.match_seed
                )

                if hasattr(
                    match,
                    "random"
                ):

                    match.random.seed = (
                        self.match_seed
                    )

                    match.rng = (
                        match.random
                    )

        round_state.player1.simulation_frame = (
            self.frame
        )

        round_state.player2.simulation_frame = (
            self.frame
        )

        # -------------------------------------------------
        # Create entity shells first
        # -------------------------------------------------

        restored_entities = []

        for saved_entity in (
            self.projectiles
        ):

            entity_class = (
                saved_entity[
                    "class"
                ]
            )

            try:

                entity = (
                    entity_class.__new__(
                        entity_class
                    )
                )

            except Exception:

                continue

            restored_entities.append(
                entity
            )

        round_state.projectiles = (
            restored_entities
        )

        # -------------------------------------------------
        # Restore entity attributes
        # -------------------------------------------------

        for index, saved_entity in enumerate(
            self.projectiles
        ):

            if index >= len(
                restored_entities
            ):
                continue

            entity = (
                restored_entities[index]
            )

            for key, value in (
                saved_entity[
                    "attributes"
                ].items()
            ):

                setattr(
                    entity,
                    key,
                    GameSnapshot.restore_value(
                        value,
                        round_state
                    )
                )

            GameSnapshot.restore_entity_resources(
                entity
            )

        # -------------------------------------------------
        # Rebuild pinned arrows
        # -------------------------------------------------
        #
        # restore_player() restores the references, but the
        # entity list has now been rebuilt, so the restored
        # Arrow references above must point into the newly
        # restored projectile list.
        #
        # Rebuild these explicitly to guarantee identity.
        # -------------------------------------------------

        round_state.player1.pinned_arrows = []
        round_state.player2.pinned_arrows = []

        for entity in (
            round_state.projectiles
        ):

            if (
                entity.__class__.__name__
                != "Arrow"
            ):
                continue

            stuck_to = getattr(
                entity,
                "stuck_to",
                None
            )

            if stuck_to is round_state.player1:

                round_state.player1.pinned_arrows.append(
                    entity
                )

            elif stuck_to is round_state.player2:

                round_state.player2.pinned_arrows.append(
                    entity
                )

    # -------------------------------------------------
    # RESTORE ENTITY RESOURCES
    # -------------------------------------------------

    @staticmethod
    def restore_entity_resources(
        entity
    ):
        """
        Rebuild rendering/audio resources omitted from
        simulation snapshots.
        """

        class_name = (
            entity.__class__.__name__
        )

        # -------------------------------------------------
        # Projectile-derived entities
        # -------------------------------------------------

        sprite_name = getattr(
            entity,
            "sprite_name",
            None
        )

        if sprite_name is not None:

            if hasattr(
                entity,
                "reload_sprite"
            ):

                entity.reload_sprite()

            else:

                try:

                    entity.sprite = (
                        pygame.image.load(
                            SPRITE_FOLDER
                            / sprite_name
                        ).convert_alpha()
                    )

                except (
                    pygame.error,
                    OSError
                ):

                    entity.sprite = None

        # -------------------------------------------------
        # Explosion
        # -------------------------------------------------

        if class_name == "Explosion":

            try:

                entity.explosion_sprite = (
                    pygame.image.load(
                        SPRITE_FOLDER
                        / "explosion.png"
                    ).convert_alpha()
                )

            except (
                pygame.error,
                OSError
            ):

                entity.explosion_sprite = None

            try:

                entity.warning_sprite = (
                    pygame.image.load(
                        SPRITE_FOLDER
                        / "warning.png"
                    ).convert_alpha()
                )

            except (
                pygame.error,
                OSError
            ):

                entity.warning_sprite = None

            owner = getattr(
                entity,
                "owner",
                None
            )

            if owner is not None:

                try:

                    entity.explosion_sound = (
                        owner.game.audio.load_game_sound(
                            SOUND_FOLDER
                            / "bomb_explosion.mp3"
                        )
                    )

                except Exception:

                    entity.explosion_sound = None

        # -------------------------------------------------
        # ChaosBlade
        # -------------------------------------------------

        elif class_name == "ChaosBlade":

            try:

                entity.sprite = (
                    pygame.image.load(
                        SPRITE_FOLDER
                        / "chaos_blade.png"
                    ).convert_alpha()
                )

            except (
                pygame.error,
                OSError
            ):

                entity.sprite = None

        # -------------------------------------------------
        # NukePool
        # -------------------------------------------------

        elif class_name == "NukePool":

            try:

                entity.sprite = (
                    pygame.image.load(
                        SPRITE_FOLDER
                        / "nuke_pool.png"
                    ).convert_alpha()
                )

            except (
                pygame.error,
                OSError
            ):

                entity.sprite = None

        # -------------------------------------------------
        # FirePatch
        # -------------------------------------------------

        elif class_name == "FirePatch":

            try:

                entity.sprite = (
                    pygame.image.load(
                        SPRITE_FOLDER
                        / "fire_patch.png"
                    ).convert_alpha()
                )

            except (
                pygame.error,
                OSError
            ):

                entity.sprite = None

    # -------------------------------------------------
    # VALUE RESTORE
    # -------------------------------------------------

    @staticmethod
    def restore_value(
        value,
        round_state
    ):
        # -------------------------------------------------
        # PLAYER
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "PLAYER"
        ):

            if value[1] == 1:

                return round_state.player1

            if value[1] == 2:

                return round_state.player2

            return None

        # -------------------------------------------------
        # WEAPON
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "WEAPON"
        ):

            if value[1] == 1:

                return round_state.player1.weapon

            if value[1] == 2:

                return round_state.player2.weapon

            return None

        # -------------------------------------------------
        # ENTITY
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "ENTITY"
        ):

            index = value[1]

            if (
                isinstance(
                    index,
                    int
                )
                and 0 <= index < len(
                    round_state.projectiles
                )
            ):

                return (
                    round_state.projectiles[
                        index
                    ]
                )

            return None

        # -------------------------------------------------
        # LIST
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "LIST"
        ):

            return [
                GameSnapshot.restore_value(
                    item,
                    round_state
                )
                for item in value[1]
            ]

        # -------------------------------------------------
        # TUPLE
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "TUPLE"
        ):

            return tuple(
                GameSnapshot.restore_value(
                    item,
                    round_state
                )
                for item in value[1]
            )

        # -------------------------------------------------
        # SET
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "SET"
        ):

            return set(
                GameSnapshot.restore_value(
                    item,
                    round_state
                )
                for item in value[1]
            )

        # -------------------------------------------------
        # DICT
        # -------------------------------------------------

        if (
            isinstance(
                value,
                tuple
            )
            and len(value) == 2
            and value[0] == "DICT"
        ):

            restored = {}

            for key, item in value[1]:

                restored_key = (
                    GameSnapshot.restore_value(
                        key,
                        round_state
                    )
                )

                restored_item = (
                    GameSnapshot.restore_value(
                        item,
                        round_state
                    )
                )

                restored[
                    restored_key
                ] = restored_item

            return restored

        # -------------------------------------------------
        # Normal value
        # -------------------------------------------------

        try:

            return deepcopy(
                value
            )

        except Exception:

            return None

    # -------------------------------------------------
    # PLAYER RESTORE
    # -------------------------------------------------

    @staticmethod
    def restore_player(
        player,
        state,
        round_state
    ):
        player.position = (
            state[
                "position"
            ].copy()
        )

        player.velocity = (
            state[
                "velocity"
            ].copy()
        )

        player.external_velocity = (
            state[
                "external_velocity"
            ].copy()
        )

        player.external_velocity_timer = (
            state[
                "external_velocity_timer"
            ]
        )

        player.health = (
            state[
                "health"
            ]
        )

        player.max_health = (
            state[
                "max_health"
            ]
        )

        player.shellshock_timer = (
            state[
                "shellshock_timer"
            ]
        )

        player.damage_flash_timer = (
            state[
                "damage_flash_timer"
            ]
        )

        player.hurt_sound_timer = (
            state[
                "hurt_sound_timer"
            ]
        )

        # -------------------------------------------------
        # Restore pinned arrows
        # -------------------------------------------------

        player.pinned_arrows = (
            GameSnapshot.restore_value(
                state[
                    "pinned_arrows"
                ],
                round_state
            )
        )

        GameSnapshot.restore_weapon(
            player.weapon,
            state[
                "weapon"
            ],
            round_state
        )

        player.weapon.player = (
            player
        )

    # -------------------------------------------------
    # WEAPON RESTORE
    # -------------------------------------------------

    @staticmethod
    def restore_weapon(
        weapon,
        state,
        round_state
    ):
        for key, value in state.items():

            if key == "player":
                continue

            try:

                setattr(
                    weapon,
                    key,
                    GameSnapshot.restore_value(
                        value,
                        round_state
                    )
                )

            except Exception:

                pass