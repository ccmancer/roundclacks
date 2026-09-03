




# Roundclacks

A 2D local and networked multiplayer combat game built from scratch in Python and Pygame, with deterministic simulation and rollback netcode.

## Screenshots

### Gameplay
<img width="897" height="937" alt="gameplay" src="https://github.com/user-attachments/assets/ae3a08ab-4d38-4818-b551-b2360613b722" />

### Weapon / upgrade selection
<img width="902" height="935" alt="loadout" src="https://github.com/user-attachments/assets/f294eb86-aba3-4c85-9f07-93fc6e0a7f09" />

### Netplay lobby / match
<img width="902" height="935" alt="netplay" src="https://github.com/user-attachments/assets/67c2d943-9020-425c-bc95-3ccf9f9e23cf" />

## Features

- 2D real-time player-versus-player combat
- Local multiplayer
- TCP-based network multiplayer
- Host/join lobby flow
- Fixed-step 60 FPS simulation
- Client input buffering
- Deterministic random number generation
- State snapshots for rollback and re-simulation
- Multiple weapons with distinct mechanics
- Weapon-specific upgrade pools
- Round-based matches with scores and rematches
- Settings and card gallery UI
- Sprite, audio, and asset management
- PyInstaller build configuration for a standalone Windows executable

## Weapons

The current build includes five weapon choices:

- Unarmed
- Sword
- Bow
- Grimoire
- Bomb

Each weapon has its own behavior and upgrade pool, allowing the same base combat system to support substantially different play styles.

## Networking

The most technically significant part of Roundclacks is its deterministic multiplayer simulation.

### High-level flow

Player input
     │
     ▼
Input buffering ──► TCP messages ──► Remote input
     │                                   │
     └──────────────┬────────────────────┘
                    ▼
          Fixed-step simulation
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Snapshot            New inputs arrive
          │                   │
          └─────────┬─────────┘
                    ▼
            Rollback / replay

The game keeps the simulation deterministic by deriving random outcomes from a match seed, round number, operation, and other metadata rather than relying on uncontrolled random state. Rollback snapshots exclude rendering and audio resources and reconstruct gameplay state when restoring a frame.

The project uses TCP for transport and implements its own newline-delimited JSON message protocol, input buffering, snapshots, and match-state synchronization.

## Tech stack

- Python
- Pygame
- TCP sockets (`socket`)
- JSON messaging
- Multithreading for network I/O
- PyInstaller for Windows builds

## Architecture

roundclacks/
├── entities/          # Players, projectiles, explosions, traps, etc.
├── weapons/           # Weapon implementations
├── upgrades/          # Upgrade definitions and pools
├── network/            # Client, server, protocol, input, snapshots
├── physics/            # Collision detection
├── game/               # Main loop, states, audio, assets, settings
├── ui/                 # Reusable UI components
├── assets/             # Sprites, audio, fonts, icon
├── save/               # Local settings
├── main.py
└── Roundclacks.spec    # PyInstaller build configuration

## Running locally

Install Python and Pygame, then run:

python main.py

For multiplayer, one player hosts a game and the other joins using the host address and port shown by the lobby.

## Building a Windows executable

The project includes a PyInstaller specification that packages the game assets and uses the Roundclacks icon.

A typical build command is:

pyinstaller Roundclacks.spec

The generated Windows application can then be distributed as a standalone build without requiring the user to install Python separately.

## Engineering highlights

### Deterministic simulation

Gameplay runs on a fixed simulation step rather than tying the simulation directly to rendering frame rate. This provides a stable basis for synchronized multiplayer and rollback.

### Rollback snapshots

`GameSnapshot` captures gameplay state while explicitly excluding resources such as Pygame surfaces and sound objects. A restored snapshot can then be used as the basis for re-simulating frames after late input arrives.

### Modular game architecture

Weapons, upgrades, entities, networking, physics, UI, and game states are separated into focused modules. This makes the combat system extensible without putting all game logic into a single loop.

## Why I built it

I wanted to build a game that was interesting technically rather than only visually. The project evolved from a local Pygame combat prototype into a networked multiplayer system, which pushed me to work through deterministic simulation, synchronization, input buffering, rollback, state restoration, and modular game architecture.

## Project status

Playable local and networked multiplayer project with a Windows build configuration.
