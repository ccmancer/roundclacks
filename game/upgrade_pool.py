import random


RARITY_WEIGHTS = {
    "common": 9,
    "rare": 3,
    "super rare": 1
}


def get_random_upgrade(upgrades):
    return random.choices(
        upgrades,
        weights=[
            RARITY_WEIGHTS[upgrade.rarity]
            for upgrade in upgrades
        ],
        k=1
    )[0]


def generate_upgrade_choices(upgrades, amount=3):
    choices = []

    available_upgrades = upgrades.copy()

    while len(choices) < amount and available_upgrades:
        upgrade = get_random_upgrade(available_upgrades)

        choices.append(upgrade)
        available_upgrades.remove(upgrade)

    return choices