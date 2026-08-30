import hashlib
import random


class DeterministicRandom:
    """
    Generates deterministic random values from a match seed.

    Random values are identified by:
        seed
        frame
        player
        event
        index

    This means one random event cannot shift the results
    of another event just because an extra random call
    happened somewhere else.
    """

    def __init__(
        self,
        seed
    ):
        self.seed = int(seed)

    # -------------------------------------------------
    # INTERNAL RNG
    # -------------------------------------------------

    def _get_rng(
        self,
        frame,
        player,
        event,
        index=0
    ):
        key = (
            f"{self.seed}:"
            f"{frame}:"
            f"{player}:"
            f"{event}:"
            f"{index}"
        )

        digest = hashlib.sha256(
            key.encode("utf-8")
        ).digest()

        seed = int.from_bytes(
            digest[:8],
            "big"
        )

        return random.Random(
            seed
        )

    # -------------------------------------------------
    # FLOAT
    # -------------------------------------------------

    def uniform(
        self,
        frame,
        player,
        event,
        minimum,
        maximum,
        index=0
    ):
        rng = self._get_rng(
            frame,
            player,
            event,
            index
        )

        return rng.uniform(
            minimum,
            maximum
        )

    # -------------------------------------------------
    # INTEGER
    # -------------------------------------------------

    def randint(
        self,
        frame,
        player,
        event,
        minimum,
        maximum,
        index=0
    ):
        rng = self._get_rng(
            frame,
            player,
            event,
            index
        )

        return rng.randint(
            minimum,
            maximum
        )

    # -------------------------------------------------
    # CHOICE
    # -------------------------------------------------

    def choice(
        self,
        frame,
        player,
        event,
        values,
        index=0
    ):
        if not values:
            raise ValueError(
                "Cannot choose from an empty sequence."
            )

        rng = self._get_rng(
            frame,
            player,
            event,
            index
        )

        return rng.choice(
            values
        )

    # -------------------------------------------------
    # WEIGHTED CHOICE
    # -------------------------------------------------

    def weighted_choice(
        self,
        frame,
        player,
        event,
        values,
        weights,
        index=0
    ):
        if not values:
            raise ValueError(
                "Cannot choose from an empty sequence."
            )

        if len(values) != len(weights):
            raise ValueError(
                "Values and weights must have "
                "the same length."
            )

        rng = self._get_rng(
            frame,
            player,
            event,
            index
        )

        return rng.choices(
            values,
            weights=weights,
            k=1
        )[0]