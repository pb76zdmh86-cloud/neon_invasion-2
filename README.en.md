# Neon Invasion

[Русский](README.md) | [English](README.en.md)

A neon 2D arcade shooter inspired by the Alien Invasion project in Eric Matthes’ *Python Crash Course*. What started as a learning exercise grew into a personal project about object-oriented programming, colorful visuals, and relaxed arcade play.

Zen mode lets you play without losing lives or reaching Game Over. Zen runs do not qualify for high scores or leaderboards, even if you disable Zen mode during the same run.

## Requirements and launch

Developed on macOS with Python **3.14** and **pygame-ce 2.5.7**.

```sh
python3.14 -m pip install pygame-ce==2.5.7
python3.14 alien_invasion.py
```

In VS Code, use the **Python: Neon Invasion** launch configuration with F5. Avoid Code Runner: it may launch a temporary file instead of the game entry point.

## Controls

| Key / input | Action |
| --- | --- |
| Left / Right or A / D | Move the ship |
| Hold Space | Fire; a charged super bullet fires automatically |
| Esc or Q during play | Pause / resume |
| Up / Down, Enter | Select and activate menu items |
| Left / Right in Settings | Adjust the selected setting |
| Mouse | Select buttons and change settings |
| F11 | Toggle fullscreen; default window size is 1200 × 800 |
| Esc or Q in Settings | Save and return to the previous screen |
| Esc or Enter in Records | Return to the menu |
| Esc or Q in the main menu | Quit |

On first launch, enter a player name (up to 10 letters or digits). Enter confirms the name; Backspace deletes a character. A blank name becomes `PLAYER`.

## Features

- Separate menu, gameplay, pause, settings, Game Over, name entry, and Hall of Fame states.
- Three visual themes: **NEON**, **RETRO**, and **LAVA**.
- Music and sound effect volume controls, saved between launches.
- Random alien groups, three alien tiers, and increasing level difficulty.
- Combo score multipliers and increased bullet capacity.
- A piercing super bullet charged by a chain of 20 kills, with up to three seconds between kills.
- Collectible shield and triple shot bonuses. Triple shot duration is configured in `settings.py` and freezes while paused.
- Three lives per standard run; unlimited survival in Zen mode.
- Top-five all-time and daily leaderboards with player names.
- Neon HUD, parallax stars, particles, engine trails, and screen shake.

## Project structure

| File | Purpose |
| --- | --- |
| `alien_invasion.py` | Entry point, game loop, state transitions, collisions, and spawning |
| `settings.py` | Gameplay constants, themes, volume, Zen mode, and saved settings |
| `menu.py`, `pause_menu.py`, `game_over.py` | Main menu, pause, and Game Over screens |
| `Settings_screen.py`, `records_screen.py` | Settings and Hall of Fame |
| `button.py`, `ui_style.py`, `scoreboard.py` | Buttons, shared UI drawing, and HUD |
| `ship.py`, `bullet.py`, `alien.py` | Ship, normal / piercing bullets, and aliens |
| `shield_bonus.py`, `triple_shot_bonus.py` | Falling power-ups |
| `game_stat.py` | Lives, score, levels, and combo tracking |
| `leader_board.py`, `profile_player.py` | Leaderboards and player profile |
| `sound.py`, `particles.py`, `starfield.py` | Audio and visual effects |
| `images/`, `sounds/`, `logo.png`, `*.ttf` | Sprites, audio, logo, and fonts |
| `tests/test_game.py` | Headless gameplay and regression checks |

Local JSON files beside the source store settings (`settings.json`), the best score (`highscore.json`), leaderboards (`leaderboard.json`), and the player name (`player_profile.json`). Leaderboard entries are saved when a standard run reaches Game Over. The best score and settings are also saved on normal exit.

## Development checks

```sh
python3.14 -m unittest discover -s tests -v
```

Tests use SDL’s dummy video/audio drivers. They check state transitions, life count, bonuses, Zen eligibility, name limits, mouse selection, fullscreen surface updates, top-five storage, and a scripted 30-second gameplay run. They do not replace manual display and audio testing.

## Roadmap

- [x] Shield and triple shot power-ups
- [x] Named top-five leaderboards for all time and today
- [x] Hall of Fame accessible from the main menu
- [ ] A boss encounter every few levels

See [the review report](REVIEW.md) for the current plan comparison and verification limits. The full Russian version is available in [README.md](README.md).

## Development story

In July of this year, I bought Eric Matthes’ *Python Crash Course*. One of the practical projects in the book was the 2D game Alien Invasion. Building on its principles and ideas, I decided to explore object-oriented programming in more depth. Over several months of designing, writing, and rewriting, the learning exercise grew into Neon Invasion, my own relaxing neon arcade game.

This project taught me inheritance and polymorphism through practical examples, pygame’s event model, file and JSON handling, debugging tracebacks, resource caching, game timers, and, above all, how to finish a project instead of abandoning it halfway through.
