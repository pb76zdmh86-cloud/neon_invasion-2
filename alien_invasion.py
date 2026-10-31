import sys
import random
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stat import Game_state
from button import Button
from scoreboard import Scoreboard
from starfield import Starfield
from particles import ParticleSystem
from sound import SoundManager
from menu import Menu
from pause_menu import PauseMenu
from game_over import GameOver
from bullet import SuperBullet
from Settings_screen import SettingsScreen
from leader_board import Leaderboard
from profile_player import PlayerProfile
from shield_bonus import ShieldBonus
from triple_shot_bonus import TripleShotBonus
from records_screen import RecordsScreen


class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    SETTINGS = "settings"
    ENTER_NAME = "enter_name"
    RECORDS = "records"


class AlienInvasion:
    def __init__(self):
        pygame.init()


        self.profile = PlayerProfile()
        self.player_name = self.profile.name
        if self.player_name == "": 
            self.state = GameState.ENTER_NAME 
        else:
            self.state = GameState.MENU
        self.fullscreen = False
        self.previous_state = GameState.MENU


        self.clock = pygame.time.Clock()

        self.settings = Settings()
        self.display = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        # Запоминаем оконный размер — к нему вернёмся при выходе из полного экрана
        self.base_size = (self.settings.screen_width, self.settings.screen_height)
        # Постоянный офф-скрин буфер: все спрайты и HUD всегда рисуют сюда,
        # независимо от того, трясётся экран в этом кадре или нет.
        self.screen = pygame.Surface(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption("Neon Invasion")

        self.starfield = Starfield(self.settings.screen_width, self.settings.screen_height)
        self.particles = ParticleSystem()
        self.sound = SoundManager(self.settings.music_volume / 10, self.settings.effects_volume / 10)

        self.shake_timer = 0.0

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self.spawn_timer_ms = 0
        self.next_spawn_delay_ms = 0
        self.level_kills = 0
        self.level_quota = self.settings.level_kill_quota_base
        self._spawn_group()
        self._reset_spawn_timer()

        self.stats = Game_state(self)
        self.sb = Scoreboard(self)
        self.play_button = Button(self, "Play",self.screen.get_rect().center,self.settings.buttons_color)
        self.menu = Menu(self)
        self.pause_menu = PauseMenu(self)
        self.game_over=GameOver(self)
        self.settings_screen = SettingsScreen(self)
        self.leaderboard = Leaderboard()
        self.player_name = self.profile.name
        self.records_screen = RecordsScreen(self)
    # ------------------------------------------------------------------ #
    # Main loop
    # ------------------------------------------------------------------ #
    def run_game(self):
        while True:
            dt = self.clock.tick(60) / 1000.0
            dt_ms = dt * 1000.0

            self._check_events()

            if self.state==GameState.PLAYING:
                self.ship.update(dt)
                self._update_bonuses(dt)
                self._update_bullets(dt)
                self._update_aliens(dt)
                self._update_spawning(dt_ms)
                self.stats.update_combo_timer(dt_ms)
                self._maybe_spawn_engine_trail()
                if self.ship.firing:
                    self._fire_bullets()
                if self.settings.zen_mode:
                    self.stats.ranked_run = False
                if self.stats.combo_timer>0:
                    self.stats.combo_timer-=dt
                    if self.stats.combo_timer<=0:
                        self.stats.combo_timer=0
                        self.stats.combo=0   # окно закрылось — цепочка на супер-пулю оборвалась

            self.starfield.update(dt)
            self.particles.update(dt)
            if self.shake_timer > 0:
                self.shake_timer -= dt
            mouse_pos=pygame.mouse.get_pos()
            self.play_button.update(dt, mouse_pos)
            if self.state==GameState.MENU:
                self.menu.update(dt,mouse_pos)
            elif self.state==GameState.PAUSED:
                self.pause_menu.update(dt,mouse_pos)
            elif self.state==GameState.GAME_OVER:
                self.game_over.update(dt,mouse_pos)
            elif self.state==GameState.SETTINGS:
                self.settings_screen.update(dt,mouse_pos)
            elif self.state == GameState.RECORDS:
                self.records_screen.update(dt, mouse_pos)
            self._update_screen()
            


    # ------------------------------------------------------------------ #
    # Input
    # ------------------------------------------------------------------ #
    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos


                if self.state == GameState.MENU:
                    clicked = self.menu.handle_click(mouse_pos)

                    if clicked == "Play":
                        self._start_new_game()
                        self.menu.selected=0

                    elif clicked=="Settings":
                        self.previous_state = self.state
                        self.state=GameState.SETTINGS
                        pygame.mouse.set_visible(True)

                    elif clicked=="Records":
                        self.previous_state=self.state
                        self.state=GameState.RECORDS
                        pygame.mouse.set_visible(True)

                    elif clicked == "Exit":
                        self._quit_game()
                    # "Settings" пока пропускаем
                
                
                elif self.state == GameState.GAME_OVER:
                    clicked = self.game_over.handle_click(mouse_pos)

                    if clicked == "New game":
                        self._start_new_game()
                        pygame.mouse.set_visible(False)

                    elif clicked=="Settings":
                        self.previous_state = self.state
                        self.state=GameState.SETTINGS
                        pygame.mouse.set_visible(True)
                        

                    elif clicked == "Menu":
                        self.state = GameState.MENU
                        pygame.mouse.set_visible(True)


                elif self.state == GameState.PAUSED:
                    clicked=self.pause_menu.handle_click(mouse_pos)

                    if clicked == "Resume":
                        self.state=GameState.PLAYING
                        pygame.mouse.set_visible(False)

                    elif clicked=="Settings":
                        self.previous_state = self.state
                        self.state=GameState.SETTINGS
                        pygame.mouse.set_visible(True)
                        
                    elif clicked == "Menu":
                        self.state=GameState.MENU
                        pygame.mouse.set_visible(True)

                elif self.state == GameState.SETTINGS:
                    clicked=self.settings_screen.handle_click(mouse_pos)
                    if clicked == "Exit":
                        self.settings.save()
                        self.state=self.previous_state

                elif self.state == GameState.RECORDS:
                    if self.records_screen.handle_click(mouse_pos):
                        self.state = GameState.MENU




    def _check_keydown_events(self, event):
        # F11 работает в любом состоянии — проверяем до всех остальных веток
        if event.key == pygame.K_F11:
            self._toggle_fullscreen()
            return
        if self.state == GameState.ENTER_NAME:
            self._handle_name_input(event)
            return
        if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.state == GameState.PLAYING :
            self.ship.moving_right = True

        elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.state == GameState.PLAYING:
            self.ship.moving_left = True

        elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
            self.ship.firing = True

        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:

            if self.state == GameState.PLAYING:
                self.state=GameState.PAUSED
                pygame.mouse.set_visible(True)

            elif self.state == GameState.PAUSED:
                self.state=GameState.PLAYING
                pygame.mouse.set_visible(False)

            elif self.state == GameState.SETTINGS:
                self.settings.save()
                self.state=self.previous_state
                pygame.mouse.set_visible(True)

            elif self.state == GameState.GAME_OVER:
                self.state = GameState.MENU

            elif self.state == GameState.MENU:
                self._quit_game()
            
     ######################################
        if self.state == GameState.MENU:
            chosen = self.menu.handle_key(event.key)

            if chosen == "Play":
                self._start_new_game()

            elif chosen == "Settings":
                self.previous_state = self.state
                self.state=GameState.SETTINGS
                pygame.mouse.set_visible(True)

            elif chosen=="Records":
                self.state=GameState.RECORDS
                pygame.mouse.set_visible(True)

            elif chosen == "Exit":
                self._quit_game()


        elif self.state == GameState.PAUSED:
            chosen = self.pause_menu.handle_key(event.key)

            if chosen == "Resume":
                self.state = GameState.PLAYING
                pygame.mouse.set_visible(False)

            elif chosen == "Settings":
                self.previous_state = self.state
                self.state = GameState.SETTINGS
                pygame.mouse.set_visible(True)

            elif chosen == "Menu":
                self.state = GameState.MENU
                pygame.mouse.set_visible(True)


        elif self.state == GameState.GAME_OVER:
            chosen = self.game_over.handle_key(event.key)

            if chosen == "New game":
                self._start_new_game()

            elif chosen == "Settings":
                self.previous_state = self.state
                self.state = GameState.SETTINGS
                pygame.mouse.set_visible(True)

            elif chosen == "Menu":
                self.state = GameState.MENU
                pygame.mouse.set_visible(True)


        elif self.state == GameState.SETTINGS:
           chosen = self.settings_screen.handle_key(event.key)

           if chosen == "Exit":
              self.settings.save()
              self.state = self.previous_state
              pygame.mouse.set_visible(True)

        elif self.state == GameState.RECORDS:
            chosen = self.records_screen.handle_key(event.key)
            if chosen:
                self.state = GameState.MENU

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d :
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a :
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.ship.firing = False

    def _handle_name_input(self, event):
        if event.key == pygame.K_RETURN:
            name = self.player_name.strip()

            if name == "":
                name = "PLAYER"

            self.profile.set_name(name)
            self.player_name = self.profile.name

            self.state = GameState.MENU
            pygame.mouse.set_visible(True)
            return

        if event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
            return

            
        char = event.unicode.upper()
        if char.isalnum():
            self.player_name = (self.player_name + char)[:10]

    def _quit_game(self):
        self.stats.save_high_score()
        self.settings.save()
        pygame.quit()
        sys.exit()

    def _toggle_fullscreen(self):
        old_size = self.screen.get_size()
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(self.base_size)
        rect = self.display.get_rect()
        self.settings.screen_width, self.settings.screen_height = rect.width, rect.height
        self.screen = pygame.Surface((rect.width, rect.height))
        self.starfield.resize(rect.width, rect.height)
        # всем, кто хранит старую поверхность, выдаём новую —
        # иначе они продолжат рисовать "в никуда"
        self.ship.screen = self.screen
        self.ship.screen_rect = self.screen.get_rect()
        self.ship.center_ship()
        for sprite in self.bullets.sprites() + self.aliens.sprites()+self.bonuses.sprites():
            sprite.screen = self.screen
        self._fit_aliens_to_screen(old_size)
        # экраны и HUD пересоздаём: внутри них и поверхность, и координаты кнопок
        self.sb = Scoreboard(self)
        self.menu = Menu(self)
        self.pause_menu = PauseMenu(self)
        self.game_over = GameOver(self)
        self.settings_screen = SettingsScreen(self)
        self.records_screen = RecordsScreen(self)

    def _fit_aliens_to_screen(self, old_size):
        """Сохраняет относительное положение врагов при изменении размера поля."""
        width, height = self.screen.get_size()
        for alien in self.aliens:
            old_range = max(1, old_size[0] - alien.rect.width)
            new_range = max(0, width - alien.rect.width)
            alien.x = max(0, min(new_range, alien.x / old_range * new_range))
            alien.base_y *= height / max(1, old_size[1])
            alien.rect.x = round(alien.x)
            alien.rect.y = round(alien.base_y)

    # ------------------------------------------------------------------ #
    # Play button / game (re)start
    # ------------------------------------------------------------------ #
    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and self.state!=GameState.PLAYING:
            self._start_new_game()

    def _start_new_game(self):
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stat()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.ship.moving_left = False
        self.ship.moving_right = False
        self.ship.firing = False
        self.ship.shield_active = False
        self.ship.triple_shot_timer = 0.0

        pygame.mouse.set_visible(False)
        self.state=GameState.PLAYING

        self.bullets.empty()
        self.aliens.empty()
        self.bonuses.empty()
        self.particles.clear()

        self.level_kills = 0
        self.level_quota = self.settings.level_kill_quota_base
        self._spawn_group()
        self._reset_spawn_timer()

        self.ship.center_ship()
        

    # ------------------------------------------------------------------ #
    # Ship / collisions
    # ------------------------------------------------------------------ #
    def _ship_hit(self):
        # Zen-режим: жизнь не отнимается и проигрыша нет — просто расчищаем поле
        if self.settings.zen_mode:
            self.aliens.empty()
            self.bullets.empty()
            self._spawn_group()
            self._reset_spawn_timer()
            self.ship.center_ship()
            self.sound.play("hit")
            return
        if self.ship.shield_active:
            self.ship.shield_active = False
            self.aliens.empty()
            self.bullets.empty()
            self._spawn_group()
            self._reset_spawn_timer()
            self.ship.center_ship()
            self.sound.play("hit")
            return
        self.stats.ships_left -= 1
        self.sb.prep_ships()
        if self.stats.ships_left > 0:
            self.aliens.empty()
            self.bullets.empty()
            self._spawn_group()
            self._reset_spawn_timer()
            self.ship.center_ship()

            self.shake_timer = 0.35
            self.sound.play("hit")
            pygame.time.wait(400)
        else:
            self.state=GameState.GAME_OVER
            self.stats.save_high_score()
            if self.stats.ranked_run and not self.settings.zen_mode:
                self.leaderboard.add_score(self.player_name, self.stats.score)
            pygame.mouse.set_visible(True)
            self.sound.play("gameover")

    def _fire_bullets(self):
        if self.state!=GameState.PLAYING:
            return
        offsets = (-18, 0, 18) if self.ship.triple_shot_timer > 0 else (0,)
        bullet_cap = self.settings.base_bullets_allowed * self.stats.bullet_multiplier()* len(offsets)
        if self.stats.super_ready:
            bullet=SuperBullet(self)
            self.bullets.add(bullet)
            self.sound.play("laser_big")
            self.stats.super_ready = False
        if len(self.bullets) + len(offsets) <= bullet_cap:
            for offset in offsets:
                new_bullet = Bullet(self, offset)
                self.bullets.add(new_bullet)
            self.sound.play("laser")

    def _update_bullets(self, dt):
        self.bullets.update(dt)
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_colisions_alien()

    def _update_bonuses(self, dt):
        self.bonuses.update(dt)
        collected = pygame.sprite.spritecollide(self.ship, self.bonuses, True)
        for bonus in collected:
            if isinstance(bonus, TripleShotBonus):
                self.ship.triple_shot_timer = self.settings.triple_shot_duration
            else:
                self.ship.shield_active = True
            # self.sound.play("menu")  # звук подбора, когда будет файл
            #self.sound.play("shield")

    def _check_colisions_alien(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, False, True)
        for bullet, hit_aliens in collisions.items():
            if not getattr(bullet, "piercing", False):
                bullet.kill()

        if collisions:
            killed = sum(len(aliens) for aliens in collisions.values())
            self.stats.combo += killed
            self.stats.combo_timer = 3.0
            if self.stats.combo >= 20:
                self.stats.super_ready = True
                self.stats.combo = 0
            self.sound.play("explosion")
            for bullet_pos, aliens in collisions.items():
                for alien in aliens:
                    old_tier = self.stats.combo_tier()
                    multiplier = self.stats.register_kill()
                    gained = int(alien.points * multiplier)
                    self.stats.score += gained
                    self.level_kills += 1
                    self._try_spawn_shield(alien.rect.center)

                    self.particles.spawn_burst(
                        alien.rect.centerx, alien.rect.centery,
                        alien.color,
                        count=self.settings.particles_per_kill,
                    )

                    new_tier = self.stats.combo_tier()
                    if new_tier > old_tier:
                        self._on_big_combo()
            self.sb.prep_score()
            self.sb.check_high_score()

        if self.level_kills >= self.level_quota:
            self._advance_level()

    def _on_big_combo(self):
        """Срабатывает каждый раз, когда комбо пересекает новый порог x2 снарядов."""
        self.sound.play("boost")
        self.particles.spawn_burst(
            self.ship.rect.centerx, self.ship.rect.centery,
            self.settings.neon_yellow, count=24, speed_range=(80, 260),
        )
        self.shake_timer = max(self.shake_timer, 0.15)

    def _advance_level(self):
        self.level_kills = 0
        self.level_quota = (
            self.settings.level_kill_quota_base
            + self.stats.level * self.settings.level_kill_quota_growth
        )
        self.settings.increase_speed()
        self.stats.level += 1
        self.sb.prep_level()
        self.sound.play("levelup")

        self.aliens.empty()
        self.bullets.empty()
        self._spawn_group()
        self._reset_spawn_timer()

    def _maybe_spawn_engine_trail(self):
        if random.random() < 0.5:
            x, y = self.ship.engine_glow_pos()
            self.particles.spawn_trail(x, y, self.settings.neon_cyan)

    def _try_spawn_shield(self, center):
        if random.random() < self.settings.shield_drop_chance:
            bonus_cls = random.choice([ShieldBonus, TripleShotBonus])
            bonus = bonus_cls(self, center)
            self.bonuses.add(bonus)

    # ------------------------------------------------------------------ #
    # Волны пришельцев: случайные группы вместо сплошной сетки
    # ------------------------------------------------------------------ #
    def _reset_spawn_timer(self):
        self.spawn_timer_ms = 0
        self.next_spawn_delay_ms = random.randint(
            self.settings.spawn_interval_min_ms, self.settings.spawn_interval_max_ms
        )

    def _update_spawning(self, dt_ms):
        self.spawn_timer_ms += dt_ms
        if self.spawn_timer_ms >= self.next_spawn_delay_ms:
            spawned=self._spawn_group()
            if spawned:
                self._reset_spawn_timer()
            else:
                self.spawn_timer_ms = 0
                self.next_spawn_delay_ms = 120

    def _spawn_group(self):
        available_slots = self.settings.max_aliens_on_screen - len(self.aliens)
        if available_slots <= 0:
            return False

        size = random.randint(self.settings.group_size_min, self.settings.group_size_max)
        size = min(size, available_slots)
        if size <= 0:
            return False

        tier = random.randint(0, len(self.settings.alien_tier_colors) - 1)

        probe = Alien(self, 0)
        gap = 18
        spacing_x = probe.rect.width + gap    # ~102 вместо 83
        spacing_y = probe.rect.height + gap
       
        pattern = random.choice(["line", "block"])

        if pattern == "line":
            cols, rows = size, 1
        else:
            cols = -(-size // 2)  
            rows = 2

        margin = spacing_x
        max_cols = max(1, (self.settings.screen_width - 2 * margin) // spacing_x)
        cols = min(cols, max_cols)

        group_width = cols * spacing_x
        group_height = rows * spacing_y

        for attempt in range(30):
          x_start = random.randint(margin, int(self.settings.screen_width - group_width - margin))
          y_start = random.randint(spacing_y, spacing_y * 3)
          candidate = pygame.Rect(x_start, y_start, group_width, group_height)
          occupied = [a.rect for a in self.aliens]
          if candidate.collidelist(occupied) == -1: 
            break
        else:
            return  False


    
        placed = 0
        for r in range(rows):
            for c in range(cols):
                if placed >= size:
                    break
                x = x_start + c * spacing_x
                y = y_start + r * spacing_y
                self._create_alien(x, y, tier)
                placed += 1
        return True

    def _create_alien(self, x_position, y_position, tier=0):
        new_alien = Alien(self, tier=tier)
        new_alien.x = x_position
        new_alien.base_y = y_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

        self.particles.spawn_burst(
            new_alien.rect.centerx, new_alien.rect.centery,
            new_alien.color, count=self.settings.particles_per_spawn,
            speed_range=(15, 50),
        )

    def _check_fleet_edges(self):
        if not self.aliens:
            return
        left = min(alien.rect.left for alien in self.aliens)
        right = max(alien.rect.right for alien in self.aliens)
        width = self.screen.get_width()
        direction = self.settings.fleet_direction
        if (direction > 0 and right >= width) or (direction < 0 and left <= 0):
            # Возвращаем флот внутрь поля, чтобы он не разворачивался каждый кадр.
            shift = width - right if direction > 0 else -left
            for alien in self.aliens:
                alien.x += shift
                alien.rect.x = round(alien.x)
            self._change_fleet_direction()

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.base_y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self, dt):
        self.aliens.update(dt)
        self._check_fleet_edges()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            return
        self._check_alien_bottom()

    def _check_alien_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                if self.settings.zen_mode:
                  alien.kill()        
                else:
                  self._ship_hit()
                  break

    # ------------------------------------------------------------------ #
    # Rendering
    # ------------------------------------------------------------------ #
    def _draw_name_input(self):
        font_title = pygame.font.Font(self.settings.font_file, 38)
        font_text = pygame.font.Font(self.settings.font_file, 22)
        font_small = pygame.font.Font(self.settings.font_file, 14)

        cx = self.settings.screen_width // 2
        cy = self.settings.screen_height // 2

        title = font_title.render( "PLAYER NAME",True,self.settings.neon_magenta)
        title_rect = title.get_rect(center=(cx, cy - 100))
        self.screen.blit(title, title_rect)

        label = font_small.render("ENTER YOUR NAME",True,self.settings.neon_yellow)
        label_rect = label.get_rect(center=(cx, cy - 35))
        self.screen.blit(label, label_rect)

        name_to_show = self.player_name

        if pygame.time.get_ticks() // 400 % 2 == 0:
         name_to_show += "_"

        name_img = font_text.render(name_to_show,True,self.settings.text_color)
        name_rect = name_img.get_rect(center=(cx, cy + 15))
        self.screen.blit(name_img, name_rect)

        hint = font_small.render("ENTER CONFIRM   BACKSPACE DELETE", True,(120, 120, 140))
        hint_rect = hint.get_rect(center=(cx, cy + 80))
        self.screen.blit(hint, hint_rect)
    
    def _draw_game(self):
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.bonuses.draw(self.screen)
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.particles.draw(self.screen)
        self.sb.show_score()

    def _draw_background(self):
        top = self.settings.bg_color
        bottom = self.settings.bg_color_bottom
        height = self.settings.screen_height
        for y in range(0, height, 4):
            t = y / height
            color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (self.settings.screen_width, y), 4)
    def _update_screen(self):


        self._draw_background()
        self.starfield.draw(self.screen)

        if self.state == GameState.ENTER_NAME:
            self._draw_name_input()
        elif self.state == GameState.MENU:
            self.menu.draw()
        elif self.state==GameState.PAUSED:
            self._draw_game()
            hovered=pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            hovered.fill((0, 0, 0,200))
            self.screen.blit(hovered,(0,0))
            self.pause_menu.draw()
        elif self.state==GameState.GAME_OVER:
            self._draw_game()
            hovered=pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
            hovered.fill((0, 0, 0,200))
            self.screen.blit(hovered,(0,0))
            self.game_over.draw()
        elif self.state == GameState.SETTINGS:
            self.settings_screen.draw()
        elif self.state == GameState.RECORDS:
            self.records_screen.draw()
        else:
            self._draw_game()

        offset = (0, 0)
        if self.shake_timer > 0:
            offset = (
                random.randint(-self.settings.shake_on_hit, self.settings.shake_on_hit),
                random.randint(-self.settings.shake_on_hit, self.settings.shake_on_hit),
            )
        self.display.fill((0, 0, 0))
        self.display.blit(self.screen, offset)
        pygame.display.flip()


if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
