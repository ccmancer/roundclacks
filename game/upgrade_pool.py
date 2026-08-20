import random
from game.upgrade import Upgrade


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

        choices.append(
            Upgrade(
                upgrade.name,
                upgrade.rarity,
                upgrade.description
            )
        )

        available_upgrades.remove(upgrade)

    return choices

SWORD_UPGRADES = [

    # Common

    Upgrade(
        "Sharpness",
        "common",
        "Deal 25% more damage"
    ),

    Upgrade(
        "Longsword",
        "common",
        "Sword is 50% longer"
    ),

    Upgrade(
        "Trained",
        "common",
        "Sword spins 50% faster, both normally and with attack input"
    ),

    Upgrade(
        "Armor",
        "common",
        "25% more health"
    ),

    Upgrade(
        "Step-in",
        "common",
        "Step towards opponent when attacking, distance increases with stacking"
    ),

    # Rare

    Upgrade(
        "Vortex",
        "rare",
        "Sword spin pulls opponent towards you, distance increases with stacking"
    ),

    Upgrade(
        "Double Spin",
        "rare",
        "Sword spins twice on attack, sword spins 2x faster with attack input, 1 extra spin per stack"
    ),

    Upgrade(
        "Greatsword",
        "rare",
        "+50% sword size, +50% sword damage, -25% sword spin"
    ),

    Upgrade(
        "Critical",
        "rare",
        "+20% chance to do 3x damage"
    ),

    Upgrade(
        "Bloodlust",
        "rare",
        "+50% lifesteal"
    ),

    # Super Rare

    Upgrade(
        "Juggernaut",
        "super rare",
        "+50% player size, +100% health, +50% sword size"
    ),

    Upgrade(
        "Rage",
        "super rare",
        "Sword spin and player speed increase inversely with player health"
    ),

    Upgrade(
        "Dual Wielder",
        "super rare",
        "+1 blade"
    ),

    Upgrade(
        "Beyblade",
        "super rare",
        "Dealing damage refreshes spin cooldown, temporary +10% spin speed for 5 seconds each hit"
    ),

    Upgrade(
        "Hero",
        "super rare",
        "Attacking also shoots a magic slash in the sword's direction, +50% damage, -50% cooldown, +1 extra projectile per stack"
    )
]


BOW_UPGRADES = [

    # Common

    Upgrade(
        "Aerodynamic",
        "common",
        "+100% projectile speed"
    ),

    Upgrade(
        "Lightweight",
        "common",
        "75% player size, attack now has recoil, stacking reduces size and adds recoil"
    ),

    Upgrade(
        "Poison Tips",
        "common",
        "+50% poison damage, damage dealt 1 per half-second"
    ),

    Upgrade(
        "Aim Sensitivity",
        "common",
        "+50% orbit speed"
    ),

    Upgrade(
        "Quickdraw",
        "common",
        "-50% cooldown time"
    ),

    # Rare

    Upgrade(
        "Greatbow",
        "rare",
        "+100% damage, +100% cooldown, +50% projectile size"
    ),

    Upgrade(
        "Heavy Arrows",
        "rare",
        "+50% damage, -25% projectile speed, +50% projectile size, knockback, stacking increases knockback"
    ),

    Upgrade(
        "Deadeye",
        "rare",
        "+50% damage, stacks per hit, lose stacks on miss"
    ),

    Upgrade(
        "Pincushion",
        "rare",
        "Arrows stick to opponent for 5 seconds and lower their speed by 25%, stacking increases sticking duration"
    ),

    Upgrade(
        "Bear Trap",
        "rare",
        "Attacking leaves behind a bear trap that deals the same damage as the attack and lasts 5 seconds, stacking increases duration"
    ),

    # Super Rare

    Upgrade(
        "Shotgun",
        "super rare",
        "-50% damage, +5 projectiles, +5 degrees spread"
    ),

    Upgrade(
        "Machinegun",
        "super rare",
        "-75% damage, -90% cooldown"
    ),

    Upgrade(
        "Homing",
        "super rare",
        "Bullets get a force that pushes them towards nearby opponents, force and range increases with stacking"
    ),

    Upgrade(
        "Ricochet",
        "super rare",
        "+5 bullet bounces"
    ),

    Upgrade(
        "Explosives",
        "super rare",
        "Bullets explode and deal knockback upon landing for +100% extra damage, explosions can also hit the user. Stacks increase explosion radius, damage, and knockback"
    )
]