from save_paths import get_save_path, read_json, write_json


class Game_state:
    """Отслеживает статистику игры, включая рекорд, сохраняемый между запусками."""

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.high_score_file = get_save_path("highscore.json")
        self.high_score = self._load_high_score()
        self.reset_stat()


        # комбо-система
        self.combo_count = 0
        self.combo_timer_ms = 0

    def reset_stat(self):
        self.ships_left = self.settings.ship_limit
        self.ranked_run = not self.settings.zen_mode
        self.score = 0
        self.level = 1
        self.combo_count = 0
        self.combo_timer_ms = 0
        self.high_score_at_start=self.high_score
        self.combo = 0
        self.combo_timer = 0.0
        self.super_ready = False

    def register_kill(self):
        """Вызывается при убийстве пришельца; возвращает текущий множитель очков."""
        if self.combo_timer_ms > 0:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.combo_timer_ms = self.settings.combo_window_ms
        multiplier = 1.0 + (self.combo_count - 1) * self.settings.combo_step
        return min(multiplier, self.settings.combo_cap)

    def combo_tier(self):
        """Сколько раз подряд комбо пересекло порог 'большого комбо'."""
        return self.combo_count // self.settings.big_combo_threshold

    def bullet_multiplier(self):
        """Во сколько раз сейчас увеличен лимит одновременных снарядов."""
        return min(2 ** self.combo_tier(), self.settings.max_bullet_multiplier)

    def update_combo_timer(self, dt_ms):
        if self.combo_timer_ms > 0:
            self.combo_timer_ms -= dt_ms
            if self.combo_timer_ms <= 0:
                self.combo_timer_ms = 0
                self.combo_count = 0

    def _load_high_score(self):
        score = read_json(self.high_score_file).get("high_score", 0)
        return score if type(score) is int and score >= 0 else 0

    def save_high_score(self):
        if self.settings.zen_mode or not self.ranked_run:
            return
        return write_json(self.high_score_file, {"high_score": self.high_score})
