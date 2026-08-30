import random
import hashlib


class MatchRandom:
    """
    Deterministic random source for gameplay.

    Every random result is derived from:

        match seed
        round number
        operation
        supplied metadata

    This makes random gameplay deterministic across clients
    and across rollback while allowing different results each
    round.
    """

    def __init__(
        self,
        seed,
        match=None
    ):
        self.seed = int(
            seed
        )

        self.match = match

    # -------------------------------------------------
    # ROUND
    # -------------------------------------------------

    def set_round(
        self,
        round_number
    ):
        """
        Change the deterministic random namespace for the
        current round.
        """
        self.round_number = int(
            round_number
        )

    # -------------------------------------------------
    # INTERNAL
    # -------------------------------------------------

    def _make_random(
        self,
        operation,
        *values,
        **kwargs
    ):
        round_number = getattr(
            self,
            "round_number",
            1
        )

        metadata = [
            self.seed,
            round_number,
            operation,
            *values
        ]

        for key in sorted(
            kwargs
        ):

            metadata.append(
                key
            )

            metadata.append(
                kwargs[key]
            )

        data = "|".join(
            str(value)
            for value in metadata
        )

        digest = hashlib.sha256(
            data.encode(
                "utf-8"
            )
        ).digest()

        derived_seed = int.from_bytes(
            digest[:8],
            "big"
        )

        return random.Random(
            derived_seed
        )

    # -------------------------------------------------
    # RANDOM
    # -------------------------------------------------

    def random(
        self,
        *args,
        **kwargs
    ):
        rng = self._make_random(
            "random",
            *args,
            **kwargs
        )

        return rng.random()

    # -------------------------------------------------
    # UNIFORM
    # -------------------------------------------------

    def uniform(
        self,
        *args,
        **kwargs
    ):
        if len(args) < 2:
            raise TypeError(
                "uniform() requires at least "
                "two positional arguments."
            )

        a = args[-2]
        b = args[-1]

        metadata = args[:-2]

        return self._make_random(
            "uniform",
            *metadata,
            **kwargs
        ).uniform(
            a,
            b
        )

    # -------------------------------------------------
    # RANDINT
    # -------------------------------------------------

    def randint(
        self,
        *args,
        **kwargs
    ):
        if len(args) < 2:
            raise TypeError(
                "randint() requires at least "
                "two positional arguments."
            )

        a = args[-2]
        b = args[-1]

        metadata = args[:-2]

        return self._make_random(
            "randint",
            *metadata,
            **kwargs
        ).randint(
            a,
            b
        )

    # -------------------------------------------------
    # CHOICE
    # -------------------------------------------------

    def choice(
        self,
        *args,
        **kwargs
    ):
        if not args:
            raise TypeError(
                "choice() requires a sequence."
            )

        sequence = args[-1]

        if not sequence:
            raise IndexError(
                "Cannot choose from an empty sequence."
            )

        metadata = args[:-1]

        return self._make_random(
            "choice",
            *metadata,
            **kwargs
        ).choice(
            sequence
        )

    # -------------------------------------------------
    # WEIGHTED CHOICE
    # -------------------------------------------------

    def weighted_choice(
        self,
        *args,
        **kwargs
    ):
        choices = (
            kwargs.get("choices")
            or kwargs.get("items")
            or kwargs.get("options")
            or kwargs.get("upgrades")
        )

        weights = kwargs.get(
            "weights"
        )

        positional_sequences = []

        for value in args:

            if isinstance(
                value,
                (list, tuple)
            ):

                positional_sequences.append(
                    value
                )

        # -------------------------------------------------
        # Find choices
        # -------------------------------------------------

        if choices is None:

            for sequence in (
                positional_sequences
            ):

                if not sequence:
                    continue

                if not all(
                    isinstance(
                        item,
                        (int, float)
                    )
                    for item in sequence
                ):

                    choices = sequence

                    break

        # -------------------------------------------------
        # Find weights
        # -------------------------------------------------

        if weights is None:

            for sequence in (
                positional_sequences
            ):

                if not sequence:
                    continue

                if all(
                    isinstance(
                        item,
                        (int, float)
                    )
                    for item in sequence
                ):

                    weights = sequence

                    break

        if choices is None:
            raise TypeError(
                "weighted_choice() could not "
                "determine choices."
            )

        if weights is None:
            raise TypeError(
                "weighted_choice() could not "
                "determine weights."
            )

        if len(choices) != len(weights):

            raise ValueError(
                "Choices and weights must have "
                "the same length."
            )

        index = kwargs.get(
            "index",
            0
        )

        metadata = []

        for value in args:

            if value is choices:
                break

            if value is weights:
                break

            if not isinstance(
                value,
                (list, tuple)
            ):

                metadata.append(
                    value
                )

        return self._make_random(
            "weighted_choice",
            *metadata,
            index=index
        ).choices(
            choices,
            weights=weights,
            k=1
        )[0]

    # -------------------------------------------------
    # SHUFFLE
    # -------------------------------------------------

    def shuffle(
        self,
        sequence,
        *args,
        **kwargs
    ):
        self._make_random(
            "shuffle",
            *args,
            **kwargs
        ).shuffle(
            sequence
        )

    # -------------------------------------------------
    # STATE COMPATIBILITY
    # -------------------------------------------------

    def getstate(
        self
    ):
        return (
            self.seed,
            getattr(
                self,
                "round_number",
                1
            )
        )

    def setstate(
        self,
        state
    ):
        self.seed = int(
            state[0]
        )

        self.round_number = int(
            state[1]
        )


class Match:

    WINNING_SCORE = 5

    def __init__(
        self,
        player1,
        player2,
        seed=None
    ):
        self.player1 = player1
        self.player2 = player2

        self.player1_wins = 0
        self.player2_wins = 0

        self.round_number = 1

        # -------------------------------------------------
        # Seed
        # -------------------------------------------------

        self.seed = seed

        if self.seed is None:

            self.seed = random.randrange(
                0,
                2**63
            )

        # -------------------------------------------------
        # Deterministic random source
        # -------------------------------------------------

        self.random = MatchRandom(
            self.seed,
            self
        )

        self.random.set_round(
            self.round_number
        )

        self.rng = self.random

    # -------------------------------------------------
    # ROUND
    # -------------------------------------------------

    def set_round(
        self,
        round_number
    ):
        self.round_number = int(
            round_number
        )

        self.random.set_round(
            self.round_number
        )

    # -------------------------------------------------
    # SCORE
    # -------------------------------------------------

    def record_win(
        self,
        winner
    ):
        if winner == self.player1:

            self.player1_wins += 1

        elif winner == self.player2:

            self.player2_wins += 1

    def is_over(
        self
    ):
        return (
            self.player1_wins
            >= self.WINNING_SCORE
            or
            self.player2_wins
            >= self.WINNING_SCORE
        )

    def get_winner(
        self
    ):
        if (
            self.player1_wins
            >= self.WINNING_SCORE
        ):

            return self.player1

        if (
            self.player2_wins
            >= self.WINNING_SCORE
        ):

            return self.player2

        return None

    # -------------------------------------------------
    # RESET
    # -------------------------------------------------

    def reset(
        self
    ):
        self.player1_wins = 0
        self.player2_wins = 0
        self.round_number = 1

        # Reset deterministic random source to
        # match seed + round 1.
        self.random = MatchRandom(
            self.seed,
            self
        )

        self.random.set_round(
            self.round_number
        )

        self.rng = self.random

        # -------------------------------------------------
        # Remove upgrades
        # -------------------------------------------------

        self.player1.weapon.upgrades.clear()
        self.player2.weapon.upgrades.clear()

        # -------------------------------------------------
        # Reset weapons
        # -------------------------------------------------

        self.player1.weapon.reset()
        self.player2.weapon.reset()

        # -------------------------------------------------
        # Reset players
        # -------------------------------------------------

        self.player1.reset(
            (150, 360)
        )

        self.player2.reset(
            (570, 360)
        )