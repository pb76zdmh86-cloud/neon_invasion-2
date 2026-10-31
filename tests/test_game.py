"""Проверки переходов и механик без окна и записи личных сохранений."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame
from alien_invasion import AlienInvasion, GameState
from leader_board import Leaderboard
from triple_shot_bonus import TripleShotBonus


class GameTests(unittest.TestCase):
    def setUp(self):
        random.seed(7)
        self.game = AlienInvasion()
        self.game.settings.zen_mode = False
        self.game._start_new_game()

    def tearDown(self):
        pygame.quit()

    def key(self, key):
        self.game._check_keydown_events(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=''))

    def test_settings_returns_to_each_origin(self):
        for state, screen in ((GameState.MENU, self.game.menu),
                              (GameState.PAUSED, self.game.pause_menu),
                              (GameState.GAME_OVER, self.game.game_over)):
            for exit_key in (pygame.K_RETURN, pygame.K_ESCAPE):
                self.game.state = state
                screen.selected = 1
                self.key(pygame.K_RETURN)
                self.assertEqual(self.game.state, GameState.SETTINGS)
                self.game.settings_screen.selected = 4
                with patch.object(self.game.settings, 'save'):
                    self.key(exit_key)
                self.assertEqual(self.game.state, state)

    def test_name_limit(self):
        self.game.player_name = 'ABCDEFGHIJ'
        self.game._handle_name_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k, unicode='k'))
        self.assertEqual(self.game.player_name, 'ABCDEFGHIJ')

    def test_exactly_three_lives(self):
        with patch.object(self.game.stats, 'save_high_score'), patch.object(self.game.leaderboard, 'add_score') as save, patch('pygame.time.wait'):
            for left in (2, 1, 0):
                self.game._ship_hit()
                self.assertEqual(self.game.stats.ships_left, left)
            self.assertEqual(self.game.state, GameState.GAME_OVER)
            save.assert_called_once()

    def test_bonuses_and_zen(self):
        g = self.game
        g.bonuses.add(TripleShotBonus(g, g.ship.rect.center))
        g._update_bonuses(0)
        self.assertEqual(g.ship.triple_shot_timer, g.settings.triple_shot_duration)
        g.ship.update(1)
        self.assertAlmostEqual(g.ship.triple_shot_timer, g.settings.triple_shot_duration - 1)
        g.ship.shield_active = True
        g._ship_hit()
        self.assertEqual(g.stats.ships_left, 3)
        self.assertFalse(g.ship.shield_active)
        g.settings.zen_mode = True
        g.settings_screen._apply(g.settings_screen.rows[3])
        g._ship_hit()
        self.assertEqual(g.stats.ships_left, 3)
        g.settings.zen_mode = False
        g.stats.score = g.stats.high_score + 100
        self.assertFalse(g.sb.check_high_score())

    def test_mouse_wins_and_records_resize(self):
        g = self.game
        for screen in (g.menu, g.pause_menu, g.game_over):
            screen.selected = len(screen.buttons) - 1
            screen.update(1 / 60, screen.buttons[0].center)
            self.assertEqual(screen.selected, 0)
        g._toggle_fullscreen()
        self.assertIs(g.records_screen.screen, g.screen)
        g._toggle_fullscreen()
        self.assertIs(g.records_screen.screen, g.screen)

    def test_scripted_play(self):
        g = self.game
        g.settings.zen_mode = True
        g.stats.ranked_run = False
        for frame in range(1800):
            g.ship.moving_right = (frame // 120) % 2 == 0
            g.ship.moving_left = not g.ship.moving_right
            g.ship.update(1 / 60)
            g._fire_bullets()
            g._update_bullets(1 / 60)
            g._update_aliens(1 / 60)
            g._update_bonuses(1 / 60)
            g._update_spawning(1000 / 60)
            g.stats.update_combo_timer(1000 / 60)
            g.particles.update(1 / 60)
            if frame % 60 == 0:
                g._update_screen()
        self.assertGreater(g.stats.score, 0)
        self.assertEqual(g.state, GameState.PLAYING)
        print(f'Прогон: 30 игровых секунд, очки {g.stats.score}, уровень {g.stats.level}')


class LeaderboardTests(unittest.TestCase):
    def test_top_five(self):
        with tempfile.TemporaryDirectory() as folder:
            lb = Leaderboard(Path(folder) / 'scores.json')
            for score in range(8):
                lb.add_score('TEST', score)
            self.assertEqual([r['score'] for r in lb.top_all_time()], [7, 6, 5, 4, 3])
            self.assertEqual(len(lb.top_daily()), 5)
