# Neon Invasion

Неоновая 2D-аркада в духе классического Alien Invasion. Цель проекта — антистресс:
спокойный геймплей, яркая неоновая графика, без наказания за ошибки (есть zen-режим).

## Технологии

- Python 3.14, pygame-ce 2.5.7
- macOS, VS Code
- Запуск: `python3.14 alien_invasion.py` (команды `python` в системе нет;
  Code Runner не использовать — он запускает tempCodeRunnerFile.py;
  интерпретатор для VS Code задан в `.vscode/settings.json`;
  в `.vscode/launch.json` есть конфигурация «Python: Neon Invasion» —
  запуск через F5 только с ней, не с «C/C++: clang»)

## Архитектура

Точка входа — `alien_invasion.py`, класс `AlienInvasion`. Игра построена на
машине состояний `GameState`: MENU / PLAYING / PAUSED / GAME_OVER / SETTINGS.
Экраны не «открываются» и «закрываются» — они либо рисуются, либо нет;
переход между экранами = одно присваивание состояния.

Единый интерфейс экранов: `update(dt, mouse_pos)`, `handle_key(key)`,
`handle_click(mouse_pos)`, `draw()`. Каждый экран подключается в пяти местах:
импорт, создание в `__init__`, update в `run_game`, draw в `_update_screen`,
клики и клавиши в `_check_events`.

## Файлы

- `settings.py` — единственный источник правды: все константы, палитра,
  темы (NEON / RETRO / LAVA, применяются через `apply_theme`), громкость,
  флаг `zen_mode`. Сохранение/загрузка настроек в JSON (`save`, `_load_saved`).
- `sound.py` — `SoundManager`: эффекты через `pygame.mixer.Sound`,
  музыка через `pygame.mixer.music` (streaming, `play(-1)` — бесконечный цикл).
  Флаг `enable`, воспроизведение через `play(name)` + `getattr`.
- `button.py` — неоновая кнопка с пульсирующим свечением; адаптеры
  `@property label/center` для полиморфизма.
- `menu.py`, `pause_menu.py`, `game_over.py`, `Settings_screen.py` — экраны.
- `Settings_screen.py` — полиморфный список строк: `SettingsRow` (громкость
  с ромбовидной шкалой), `ThemeRow` (темы), `ToggleRow` (zen-режим), `Button`.
  Общий интерфейс строк: `label`, `center`, `change(direction)`, `draw(...)`.
- `ship.py`, `bullet.py` (`Bullet`, `SuperBullet` с пробитием), `alien.py`,
  `game_stat.py` — игровые объекты и статистика (комбо-счётчик, рекорды).

## Соглашения

- Комментарии и сообщения — на русском.
- Приглушённый цвет: `tuple(int(c * 0.6) for c in color)`.
- Навигация на всех экранах: стрелки + Enter + мышь, выбор по модулю
  `(selected ± 1) % len(список)`; при наведении мыши «мышь побеждает».
- Zen-режим: игрок не проигрывает; проверки `settings.zen_mode` в `_ship_hit`
  и `_check_alien_bottom`; в zen-режиме рекорды не сохраняются.

## Планы

Power-ups (щит, тройной выстрел), таблица рекордов top-5 с именами,
босс каждые N уровней.

## Стиль работы

Разработчик — начинающий, учится. Объясняй изменения словами по-русски,
давай код небольшими порциями, объясняй, что делает каждая новая строка.
