from pathlib import Path
import json

class Settings:
    """Хранит все настраиваемые параметры игры."""

    def __init__(self):
        # --- Экран ---
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (6, 4, 20)          # тёмно-фиолетовый космос
        self.bg_color_bottom = (14, 8, 40)  # для вертикального градиента

        # --- Неоновая палитра ---
        self.neon_cyan = (0, 255, 242)
        self.neon_magenta = (255, 43, 214)
        self.neon_yellow = (255, 247, 0)
        self.neon_green = (57, 255, 20)
        self.neon_orange = (255, 123, 0)
        self.text_color = (233, 230, 255)
        self.soft_blue_play=(97,180,207)
        self.orange_exit_button=(199,74,4)
        self.violet_settings_button = (123,92,240)
        self.buttons_color=(21,9,33)
        

        self.zen_mode=False
        self.themes = {
    "NEON": {
        "neon_cyan": (0, 255, 242),
        "neon_magenta": (255, 43, 214),
        "neon_yellow": (255, 247, 0),
        "bg_color": (6, 4, 20),
        "bg_color_bottom": (14, 8, 40),
        },
    "RETRO": {   # зелёный терминал
        "neon_cyan": (80, 255, 120),
        "neon_magenta": (200, 255, 100),
        "neon_yellow": (255, 255, 120),
        "bg_color": (2, 12, 4),
        "bg_color_bottom": (4, 25, 8),
        },
    "LAVA": {    # красно-оранжевая
        "neon_cyan": (255, 140, 40),
        "neon_magenta": (255, 60, 60),
        "neon_yellow": (255, 220, 80),
        "bg_color": (20, 4, 4),
        "bg_color_bottom": (40, 10, 6),
        },
    }
        
        self.theme_name = "NEON"

        # Цвета пришельцев по "ярусам" (чем реже цвет, тем больше очков)
        self.alien_tier_colors = [self.neon_orange, self.neon_magenta, self.neon_cyan]
        self.alien_tier_bonus = [30, 15, 0]  # доп. очки за ярус (0 = ближний к кораблю)

        # --- Корабль ---
        self.ship_limit = 3
        self.shield_bonus_speed = 100
        self.shield_drop_chance = 0.05
        self.triple_shot_duration = 3.0
        

        # --- Пуля ---
        self.bullet_width = 4
        self.bullet_height = 18
        self.bullet_color = self.neon_cyan
        self.base_bullets_allowed = 4

        # --- Флот пришельцев ---
        self.fleet_drop_speed = 34

        # --- Волны пришельцев (случайные группы вместо сплошной сетки) ---
        self.group_size_min = 8
        self.group_size_max = 18
        self.spawn_interval_min_ms = 250
        self.spawn_interval_max_ms = 700
        self.max_aliens_on_screen = 42
        self.level_kill_quota_base = 28
        self.level_kill_quota_growth = 12

        # --- Ускорение по уровням ---
        self.speedup_scale = 1.12
        self.aliens_scale = 1.35

        # --- Комбо-система ---
        self.combo_window_ms = 1400   # сколько мс держится комбо между убийствами
        self.combo_step = 0.35        # прирост множителя очков за каждое звено цепочки
        self.combo_cap = 4.0          # максимальный множитель очков

        # Большое комбо: за каждые N подряд убийств лимит снарядов удваивается
        self.big_combo_threshold = 5
        self.max_bullet_multiplier = 4  # не даём улететь в бесконечность

        # --- Партиклы / эффекты ---
        self.music_volume=3
        self.effects_volume=5
        self.particles_per_kill = 16
        self.particles_per_spawn = 6
        self.shake_on_hit = 14

        # --- Шрифты ---
        self.font_file = str(Path(__file__).resolve().parent / "PressStart2P-Regular.ttf")
        self.font_file_digits = str(Path(__file__).resolve().parent / "Orbitron-Bold.ttf")

        self.initialize_dynamic_settings()

        self.settings_file = Path(__file__).parent / "settings.json"
        self._load_saved()

    def initialize_dynamic_settings(self):
        """Значения, которые сбрасываются в начале каждой новой игры."""
        self.ship_speed = 5.0
        self.alien_speed = 1.6
        self.bullet_speed = 7.5

        self.fleet_direction = 1
        self.aliens_points = 50

    def increase_speed(self):
        """Увеличивает темп игры и стоимость пришельцев с каждым уровнем."""
        self.ship_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.aliens_points = int(self.aliens_points * self.aliens_scale)

    def _load_saved(self):
     try:
        data = json.loads(self.settings_file.read_text())
        self.music_volume = data.get("music_volume", self.music_volume)
        self.effects_volume = data.get("effects_volume", self.effects_volume)
        self.zen_mode = data.get("zen_mode",self.zen_mode)
        theme = data.get("theme_name")
        if theme in self.themes:
               self.apply_theme(theme)
     except Exception:
        pass   

    def save(self):
     data = {
        "music_volume": self.music_volume,
        "effects_volume": self.effects_volume,
        "theme_name": self.theme_name,
        "zen_mode":self.zen_mode
    }
     self.settings_file.write_text(json.dumps(data))

    def apply_theme(self, name):
     self.theme_name = name
     for key, value in self.themes[name].items():
        setattr(self, key, value)
    # производные цвета пересчитываем:
     self.bullet_color = self.neon_cyan
     self.alien_tier_colors = [self.neon_orange, self.neon_magenta, self.neon_cyan]
