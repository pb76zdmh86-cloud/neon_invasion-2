"""Проверки сохранений работают только во временной папке."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from save_paths import get_save_path, read_json, write_json
from settings import Settings
from profile_player import PlayerProfile
from leader_board import Leaderboard
from game_stat import Game_state


class SaveTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.saved = Path(folder.name) / 'new'
        for name, value in (('SAVE_DIR', self.saved),):
            replacement = patch('save_paths.' + name, value)
            replacement.start()
            self.addCleanup(replacement.stop)

    def put(self, filename, value):
        self.saved.mkdir(exist_ok=True)
        path = self.saved / filename
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def test_paths_do_not_copy_old_saves(self):
        with patch.object(Path, 'read_bytes') as read_old:
            for name in ('settings.json', 'highscore.json', 'player_profile.json', 'leaderboard.json'):
                path = get_save_path(name)
                self.assertEqual(path, self.saved / name)
                self.assertFalse(path.exists())
            read_old.assert_not_called()
        self.assertFalse(self.saved.exists())

    def test_new_saves_start_with_default_values(self):
        settings = Settings()
        profile = PlayerProfile()
        board = Leaderboard()
        stats = Game_state(SimpleNamespace(settings=settings))
        self.assertEqual(settings.music_volume, 3)
        self.assertEqual(settings.theme_name, 'NEON')
        self.assertEqual(profile.name, '')
        self.assertEqual(stats.high_score, 0)
        self.assertEqual(board.top_all_time(), [])
        self.assertEqual(board.top_daily(), [])
        for obj in (settings, profile, board):
            self.assertTrue(obj.save())
        self.assertTrue(stats.save_high_score())
        self.assertEqual(read_json(self.saved / 'player_profile.json'), {'name': ''})
        self.assertEqual(read_json(self.saved / 'highscore.json'), {'high_score': 0})
        self.assertEqual(read_json(self.saved / 'leaderboard.json'), {'all_time': [], 'daily': []})

    def test_invalid_json_and_wrong_root_types(self):
        for contents in ('[', '[]', 'null', '123', '"text"', '{}'):
            with self.subTest(contents=contents):
                self.saved.mkdir(exist_ok=True)
                for name in ('settings.json', 'highscore.json', 'player_profile.json', 'leaderboard.json'):
                    (self.saved / name).write_text(contents)
                settings = Settings()
                self.assertEqual(settings.music_volume, 3)
                self.assertEqual(PlayerProfile().name, '')
                self.assertEqual(Leaderboard().top_all_time(), [])
                self.assertEqual(Game_state(SimpleNamespace(settings=settings)).high_score, 0)

    def test_invalid_values_and_volume_bounds(self):
        self.put('settings.json', {'music_volume': 'loud', 'effects_volume': 500,
                                  'zen_mode': 'false', 'theme_name': []})
        settings = Settings()
        self.assertEqual(settings.music_volume, 3)
        self.assertEqual(settings.effects_volume, 10)
        self.assertFalse(settings.zen_mode)
        self.put('player_profile.json', {'name': None})
        self.assertEqual(PlayerProfile().name, '')
        for score in (None, [], 'abc', -1, True):
            self.put('highscore.json', {'high_score': score})
            self.assertEqual(Game_state(SimpleNamespace(settings=settings)).high_score, 0)

    def test_bad_leaderboard_rows_are_skipped(self):
        record = {'name': 'TEST', 'score': 50, 'date': date.today().isoformat()}
        self.put('leaderboard.json', {'all_time': [None, {}, record,
                  {**record, 'score': 'abc'}, {**record, 'date': 'yesterday'}], 'daily': None})
        board = Leaderboard()
        self.assertEqual(board.top_all_time(), [record])
        self.assertEqual(board.top_daily(), [])

    def test_failed_write_preserves_previous_save(self):
        path = self.put('settings.json', {'music_volume': 3})
        for method in ('write_text', 'replace'):
            with self.subTest(method=method), patch.object(Path, method, side_effect=OSError('Нет места')), patch('builtins.print'):
                self.assertFalse(write_json(path, {'music_volume': 10}))
            self.assertEqual(read_json(path), {'music_volume': 3})
            self.assertFalse(path.with_name(path.name + '.tmp').exists())

    def test_loaders_handle_read_errors_and_saves_handle_write_errors(self):
        with patch.object(Path, 'read_text', side_effect=PermissionError('Нет доступа')):
            self.assertEqual(PlayerProfile().name, '')
            self.assertEqual(Leaderboard().top_all_time(), [])
        settings = Settings()
        profile = PlayerProfile()
        board = Leaderboard()
        stats = Game_state(SimpleNamespace(settings=settings))
        with patch.object(Path, 'write_text', side_effect=OSError('Нет места')), patch('builtins.print'):
            for obj in (settings, profile, board):
                self.assertFalse(obj.save())
            self.assertFalse(stats.save_high_score())
