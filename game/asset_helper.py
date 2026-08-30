from pathlib import Path
import sys

import pygame


def get_base_path():
    """
    Return the base directory containing bundled assets.

    Normal Python execution:

        roundclacks/
            game/
            assets/

    PyInstaller execution:

        sys._MEIPASS/
            assets/
            ...
    """

    if getattr(
        sys,
        "frozen",
        False
    ):

        return Path(
            sys._MEIPASS
        ).resolve()

    return Path(
        __file__
    ).resolve().parent.parent


BASE_PATH = get_base_path()

ASSET_PATH = (
    BASE_PATH
    / "assets"
)


def get_asset_path(
    *parts
):
    """
    Return the path to an asset.

    Example:

        get_asset_path(
            "sprites",
            "game",
            "player.png"
        )

    Returns:

        assets/sprites/game/player.png
    """

    return ASSET_PATH.joinpath(
        *parts
    )


def load_image(
    *parts
):
    """
    Load an image asset and return a pygame Surface
    with alpha support.
    """

    path = get_asset_path(
        *parts
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Image asset not found: {path}"
        )

    try:

        return pygame.image.load(
            path
        ).convert_alpha()

    except pygame.error as error:

        raise pygame.error(
            f"Could not load image asset: {path}\n"
            f"{error}"
        ) from error


def load_sound(
    *parts
):
    """
    Load a sound asset and return a pygame Sound object.
    """

    path = get_asset_path(
        *parts
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Sound asset not found: {path}"
        )

    try:

        return pygame.mixer.Sound(
            path
        )

    except pygame.error as error:

        raise pygame.error(
            f"Could not load sound asset: {path}\n"
            f"{error}"
        ) from error


def get_music_path(
    name
):
    """
    Return the path to a music track.
    """

    return get_asset_path(
        "audio",
        "music",
        f"{name}.mp3"
    )


def load_music(
    name
):
    """
    Load a music track directly through pygame.
    """

    path = get_music_path(
        name
    )

    if not path.exists():

        raise FileNotFoundError(
            f"Music asset not found: {path}"
        )

    try:

        pygame.mixer.music.load(
            path
        )

    except pygame.error as error:

        raise pygame.error(
            f"Could not load music asset: {path}\n"
            f"{error}"
        ) from error