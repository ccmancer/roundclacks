import random

from upgrades.upgrade import Upgrade


RARITY_WEIGHTS = {
    "common": 9,
    "rare": 3,
    "super rare": 1
}


def get_random_upgrade(
    upgrades,
    random_source=None,
    frame=0,
    player=0,
    index=0
):
    weights = [
        RARITY_WEIGHTS[
            upgrade.rarity
        ]
        for upgrade in upgrades
    ]

    # -------------------------------------------------
    # Local fallback
    # -------------------------------------------------

    if random_source is None:

        return random.choices(
            upgrades,
            weights=weights,
            k=1
        )[0]

    # -------------------------------------------------
    # Deterministic selection
    # -------------------------------------------------

    return random_source.weighted_choice(
        frame,
        player,
        "upgrade_choice",
        upgrades,
        weights,
        index=index
    )


def generate_upgrade_choices(
    upgrades,
    amount=3,
    random_source=None,
    frame=0,
    player=0
):
    choices = []

    available_upgrades = upgrades.copy()

    while (
        len(choices) < amount
        and available_upgrades
    ):

        upgrade = get_random_upgrade(
            available_upgrades,
            random_source,
            frame,
            player,
            index=len(choices)
        )

        choices.append(
            Upgrade(
                upgrade.name,
                upgrade.rarity,
                upgrade.description
            )
        )

        available_upgrades.remove(
            upgrade
        )

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
        "Sword orbits 50% faster"
    ),

    Upgrade(
        "Armor",
        "common",
        "25% more health"
    ),

    Upgrade(
        "Step-in",
        "common",
        "Step towards opponent when attacking"
    ),

    # Rare

    Upgrade(
        "Vortex",
        "rare",
        "Dealing damage pulls opponent towards you"
    ),

    Upgrade(
        "Double Spin",
        "rare",
        "Sword spins twice on attack, +50% attack speed"
    ),

    Upgrade(
        "Greatsword",
        "rare",
        "+50% sword size, +50% damage, -25% orbit"
    ),

    Upgrade(
        "Light Armor",
        "rare",
        "+10% health, +25% speed"
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
        "Increase speed and damage as health decreases"
    ),

    Upgrade(
        "Dual Wielder",
        "super rare",
        "+1 blade"
    ),

    Upgrade(
        "Beyblade",
        "super rare",
        "0 spin cooldown, temporary +25% spin speed for 5 seconds each hit"
    ),

    Upgrade(
        "Hero",
        "super rare",
        "Attacking also shoots a magic slash in the sword's direction, +50% damage, -50% cooldown"
    )
]


BOW_UPGRADES = [

    # Common

    Upgrade(
        "Aerodynamic",
        "common",
        "+50% projectile speed"
    ),

    Upgrade(
        "Lightweight",
        "common",
        "75% player size, attack now has recoil"
    ),

    Upgrade(
        "Pointiness",
        "common",
        "+25% damage"
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
        "+100% damage, +100% cooldown, +50% arrow size"
    ),

    Upgrade(
        "Heavy Arrows",
        "rare",
        "+50% damage, -25% arrow speed, +50% arrow size, knockback"
    ),

    Upgrade(
        "Sniper",
        "rare",
        "+50% damage, +50% cooldown, +50% arrow speed, -25% orbit speed"
    ),

    Upgrade(
        "Pincushion",
        "rare",
        "Arrows stick to opponent for 5 seconds and lower their speed by 25%"
    ),

    Upgrade(
        "Bear Trap",
        "rare",
        "Attacking leaves behind a bear trap that lasts 5 seconds"
    ),

    # Super Rare

    Upgrade(
        "Shotgun",
        "super rare",
        "-50% damage, +5 projectiles"
    ),

    Upgrade(
        "Machinegun",
        "super rare",
        "-50% damage, -99% cooldown, +spread"
    ),

    Upgrade(
        "Homing",
        "super rare",
        "Bullets home in on nearby opponents"
    ),

    Upgrade(
        "Ricochet",
        "super rare",
        "+5 bullet bounces"
    ),

    Upgrade(
        "MLG",
        "super rare",
        "+200% orbit speed, +400$ damage, +100% arrow speed"
    )
]

BOMB_UPGRADES = [

    # Common

    Upgrade(
        "Fastball",
        "common",
        "+100% initial momentum"
    ),

    Upgrade(
        "Lethality",
        "common",
        "+50% damage"
    ),

    Upgrade(
        "Gunpowder",
        "common",
        "+50% blast radius"
    ),

    Upgrade(
        "Extra Force",
        "common",
        "+50% blast knockback"
    ),

    Upgrade(
        "Professional",
        "common",
        "-50% self damage"
    ),

    # Rare

    Upgrade(
        "Madness",
        "rare",
        "-90% cooldown, +50% self damage, +spread"
    ),

    Upgrade(
        "Shellshock",
        "rare",
        "Blasts slow players by 50% for 5 seconds"
    ),

    Upgrade(
        "Fuse",
        "rare",
        "+75% blast radius, damage, and knockback, +0.5 second blast startup"
    ),

    Upgrade(
        "Mine",
        "rare",
        "Bombs stick to the border and explode when the opponent comes near or after 5 seconds"
    ),

    Upgrade(
        "Direct Hit",
        "rare",
        "-75% blast radius, +100% damage"
    ),

    # Super Rare

    Upgrade(
        "Cluster Bomb",
        "super rare",
        "Bombs also explode into 8 smaller bombs"
    ),

    Upgrade(
        "Nuke",
        "super rare",
        "+100% cooldown, +100% blast radius, +100% damage, blasts leave behind nuclear waste"
    ),

    Upgrade(
        "Earthlight Ray",
        "super rare",
        "Explosions shoot laser projectiles toward enemies"
    ),

    Upgrade(
        "Pyromaniac",
        "super rare",
        "Explosions heal the user for 50% of damage dealt"
    ),

    Upgrade(
        "Chaos Bomb",
        "super rare",
        "Explosions create a Devilknife attack"
    )
]


GRIMOIRE_UPGRADES = [

    # Common

    Upgrade(
        "Mana Reserves",
        "common",
        "+50% beam duration"
    ),

    Upgrade(
        "Hotter Beam",
        "common",
        "+50% beam tick rate"
    ),

    Upgrade(
        "Spell Proficiency",
        "common",
        "+50% beam width"
    ),

    Upgrade(
        "Fast Reader",
        "common",
        "-50% cooldown"
    ),

    Upgrade(
        "Faster Current",
        "common",
        "+knockback"
    ),

    # Rare

    Upgrade(
        "Fire Enchantment",
        "rare",
        "-50% beam duration, +200% beam tick rate"
    ),

    Upgrade(
        "Earth Enchantment",
        "rare",
        "-25% beam tick rate, beam ticks deal 1 more damage"
    ),

    Upgrade(
        "Metal Enchantment",
        "rare",
        "+50% health, -25% movement speed"
    ),

    Upgrade(
        "Wood Enchantment",
        "rare",
        "+50% lifesteal"
    ),

    Upgrade(
        "Water Enchantment",
        "rare",
        "+100% beam width, -25% orbit speed"
    ),

    # Super Rare

    Upgrade(
        "Master Spark",
        "super rare",
        "+200% beam duration, width, tick rate, and cooldown"
    ),

    Upgrade(
        "Dark Ritual",
        "super rare",
        "Gain rapid health regeneration"
    ),

    Upgrade(
        "Tribeam",
        "super rare",
        "Beam deals 4x tick damage and costs 1 health per tick while firing"
    ),

    Upgrade(
        "Double Spark",
        "super rare",
        "+1 beam"
    ),

    Upgrade(
        "Magic Barrier",
        "super rare",
        "Take 90% less damage while firing"
    )
]


UNARMED_UPGRADES = [

    # Common

    Upgrade(
        "Footwork",
        "common",
        "+50% speed"
    ),

    Upgrade(
        "Slugger",
        "common",
        "+50% damage"
    ),

    Upgrade(
        "Hyperactive",
        "common",
        "-50% attack cooldown"
    ),

    Upgrade(
        "Endurance",
        "common",
        "+50% attack duration"
    ),

    Upgrade(
        "Sprinter",
        "common",
        "+100% speed during attack"
    ),

    # Rare

    Upgrade(
        "Superarmor",
        "rare",
        "Take 50% damage while attacking"
    ),

    Upgrade(
        "Cannonball",
        "rare",
        "+100% damage, -25% speed"
    ),

    Upgrade(
        "Brute",
        "rare",
        "+25% size, +50% health"
    ),

    Upgrade(
        "Momentum",
        "rare",
        "Deal extra percentage damage based on your percentage speed above base"
    ),

    Upgrade(
        "Marathon Runner",
        "rare",
        "+200% attack duration, -25% speed"
    ),

    # Super Rare

    Upgrade(
        "PAC-MAN",
        "super rare",
        "While attacking, pass through borders and appear on the opposite side, with a +50% speed boost"
    ),

    Upgrade(
        "Blazing Fast",
        "super rare",
        "Your attack creates a damaging fire trail"
    ),

    Upgrade(
        "Raging Demon",
        "super rare",
        "+100% speed, +100% attack duration, +50% cooldown, landing a hit recharges charge duration"
    ),

    Upgrade(
        "Tunnel Effect",
        "super rare",
        "Phase through enemies during the attack and gain a +50% speed boost"
    ),

    Upgrade(
        "Instant Transmission",
        "super rare",
        "+50% attacking speed, teleport towards your enemy before attacking"
    )
]