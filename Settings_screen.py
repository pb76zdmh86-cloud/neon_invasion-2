from button import Button
from scoreboard import Scoreboard
import pygame


class SettingsRow:
        def __init__(self, label, value, minimum, maximum, center):
            self.label = label
            self.value = value
            self.minimum = minimum
            self.maximum = maximum
            self.center = center
            self.rect = pygame.Rect(0, 0, 650, 50)
            self.rect.center = center
            self.bar_offset = 80 
            self.cell_step = 26

        def change(self, direction):
            self.value += direction
            if self.value < self.minimum:
               self.value = self.minimum
            if self.value > self.maximum:
               self.value = self.maximum

        def draw(self, screen, font, color, dim_color):
            label_img = font.render(self.label, True, color)
            label_rect = label_img.get_rect(center=self.center)
            screen.blit(label_img, label_rect)

            size=8
            x = self.center[0] + 80
            cy=self.center[1]
            size=8
            for k in range(self.maximum):
                cx=x+k*26
                points=[(cx, cy - size), (cx+size, cy), (cx, cy + size), (cx - size, cy)]
                if k < self.value:
                        pygame.draw.polygon(screen,color,points)
                else:
                        pygame.draw.polygon(screen,color,points,2)
        def set_from_mouse(self, mouse_x):
          bar_x = self.center[0] + self.bar_offset
          if mouse_x < bar_x - self.cell_step // 2:
             return False                      # клик левее шкалы — по лейблу, не трогаем
          k = round((mouse_x - bar_x) / self.cell_step)
          self.value = max(self.minimum, min(self.maximum, k + 1))
          return True

class ThemeRow:
    def __init__(self, settings, center):
        self.settings = settings
        self.label = "THEME"
        self.center = center
        self.rect = pygame.Rect(0, 0, 620, 50)
        self.rect.center = center

    def change(self, direction):
        names = list(self.settings.themes.keys())          # ["NEON", "RETRO", "LAVA"]
        i = names.index(self.settings.theme_name)          # где мы сейчас
        i = (i + direction) % len(names)                   # карусель! знакомый приём
        self.settings.apply_theme(names[i])

    def draw(self, screen, font, color, dim_color):
        text = f"THEME: {self.settings.theme_name}"
        img = font.render(text, True, color)
        screen.blit(img, img.get_rect(center=self.center))

class ToggleRow:
    def __init__(self, settings, center):
        self.settings = settings
        self.label = "ZEN MODE"
        self.center = center
        self.rect = pygame.Rect(0, 0, 620, 50)
        self.rect.center = center

    def change(self, direction):
        self.settings.zen_mode = not self.settings.zen_mode   # щёлк — и наоборот

    def draw(self, screen, font, color, dim_color):
        state = "ON" if self.settings.zen_mode else "OFF"
        img = font.render(f"ZEN MODE: {state}", True, color)
        screen.blit(img, img.get_rect(center=self.center))

class SettingsScreen:
    def __init__(self, ai_game):
    
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.sound = ai_game.sound
        self.ai_game = ai_game

        self.title_font = pygame.font.Font(self.settings.font_file, 80)
        self.row_font = pygame.font.Font(self.settings.font_file, 22)
    

        screen_rect = self.screen.get_rect()
        cx = screen_rect.centerx
        h = screen_rect.height

        self.rows = [
            SettingsRow( "MUSIC", self.settings.music_volume,0,10, (int(cx*0.85), int(h * 0.55))),
            SettingsRow("EFFECTS", self.settings.effects_volume,0,10, (int(cx*0.88), int(h * 0.50))),
            ThemeRow(self.settings, (cx, int(h * 0.60))),
            ToggleRow(self.settings, (cx, int(h * 0.65))),
            Button(ai_game, "Exit",     (cx, int(h * 0.52) + 180),self.settings.orange_exit_button)
        ]
    
        self.selected = 0
        self.hovered=False



        
    def update(self, dt, mouse_pos):
        for i, item in enumerate(self.rows):
           if item.rect.collidepoint(mouse_pos):
               self.selected = i

    def handle_key(self, key):
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.rows)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.rows)
        elif key == pygame.K_LEFT:
            self.rows[self.selected].change(-1)
            self._apply(self.rows[self.selected])
        elif key == pygame.K_RIGHT:
            self.rows[self.selected].change(+1)
            self._apply(self.rows[self.selected])
        elif key == pygame.K_RETURN:
            return self.rows[self.selected].label

    def handle_click(self, mouse_pos):
        for item in self.rows:
            if item.rect.collidepoint(mouse_pos):
                if isinstance(item, SettingsRow):
                    # клик по шкале громкости сразу выставляет значение
                    if item.set_from_mouse(mouse_pos[0]):
                        self._apply(item)
                    return None
                if isinstance(item, Button):
                    return item.label    # кнопка Exit
                # THEME и ZEN: клик переключает, как стрелка вправо
                item.change(+1)
                self._apply(item)
                return None
        return None

    def draw(self):
       screen_rect=self.screen.get_rect()


       title_img=self.title_font.render("SETTINGS",True,self.settings.neon_cyan)
       title_rect=title_img.get_rect(centerx=screen_rect.centerx,y=int(screen_rect.height * 0.3))
       self.screen.blit(title_img,title_rect)


       for i,item in enumerate(self.rows):
           if i==self.selected:
               color=self.settings.neon_cyan
           else:
               color=tuple(int(c * 0.7) for c in self.settings.neon_cyan)
           item.hovered=(i==self.selected)
           item.draw(self.screen,self.row_font,color,tuple(int(c * 0.7) for c in self.settings.neon_cyan))

           

       tri_h = 26
       tri_w = 22

       cy = self.rows[self.selected].center[1]     # y центра строки
       x_tip = screen_rect.centerx - 260            # на глаз левее лейбла
       x_base = x_tip - tri_w
       points = [
           (x_base, cy - tri_h // 2),
           (x_base, cy + tri_h // 2),
           (x_tip, cy),
       ]
       pygame.draw.polygon(self.screen,self.settings.neon_cyan,points)

       hint_img = pygame.font.Font(self.settings.font_file, 12).render(
            "ARROWS: CHANGE    ESC: BACK", True,
            tuple(int(c * 0.55) for c in self.settings.neon_cyan))
       hint_rect = hint_img.get_rect(centerx=screen_rect.centerx,
                                      y=int(screen_rect.height * 0.85))
       self.screen.blit(hint_img, hint_rect)

    def _apply(self, row):
     if row.label == "ZEN MODE" and self.settings.zen_mode:
        self.stats.ranked_run = False
     if row.label == "THEME":
        self.ai_game.sb = Scoreboard(self.ai_game)
     if row.label == "MUSIC":
        self.settings.music_volume = row.value
        if self.sound.enable:
            pygame.mixer.music.set_volume(row.value / 10)
     elif row.label == "EFFECTS":
        self.settings.effects_volume = row.value
        self.sound.set_effects_volume(row.value / 10)

        
