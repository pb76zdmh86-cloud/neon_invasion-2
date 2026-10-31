import math

import pygame.font
from ui_style import draw_thin_rule, draw_diamond

class Button:
    def __init__(self, ai_game, msg,center,color,font_size=30):
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        self.width, self.height = 240, 60
        self.border_color = color
        self.text_color = (255, 255, 255)
        self.border_color_hovered=(255,255,255)
        self.font = pygame.font.Font(self.settings.font_file, font_size)
        self.border_dim = tuple(int(c * 0.9) for c in self.border_color)
        self.text_dim = tuple(int(c * 0.75) for c in self.settings.text_color)

        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = center

        self.pulse_timer = 0.0

        self.prep_msg(msg)
        self.msg = msg


        self.hovered=False

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg.upper(), True, self.border_color_hovered)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

        self.msg_image_dim = self.font.render(msg.upper(), True, self.border_dim )
        self.msg_image_rect_dim = self.msg_image.get_rect()
        self.msg_image_rect_dim.center = self.rect.center

    def update(self,dt,mouse_pos):
        self.pulse_timer += dt
        self.hovered=self.rect.collidepoint(mouse_pos)

    def draw_button(self):
     cy = self.rect.centery

     if self.hovered:
        pulse = (math.sin(self.pulse_timer * 8.0) + 1) / 2

        brightness = 0.60 + pulse * 0.40

        line_color = tuple(
            min(255, int(c * brightness))
            for c in self.border_color )

        draw_thin_rule(self.screen, cy + 28,self.rect.centerx,self.width - 76,line_color,
            alpha=120,
            diamond_caps=False)

        draw_diamond(self.screen,(self.rect.left + 18, cy), 8,line_color,glow=True)

        draw_diamond(self.screen,(self.rect.right - 18, cy),8,line_color,
            width=1,
            glow=True)
        
        text = self.font.render(self.msg,True,line_color)
        text_rect = text.get_rect(center=self.msg_image_rect.center)
        self.screen.blit(text, text_rect)
        # Рисуем кнопку всегда
     else:
          pulse = 0.75 + 0.25 * math.sin(self.pulse_timer * 3.0)
          line_color = tuple(min(255, int(c * (0.82 + pulse * 0.18))) for c in self.border_color)
        
          draw_thin_rule(self.screen,cy + 28,self.rect.centerx,
                               self.width - 76,line_color,alpha=90, diamond_caps=False)
        
          draw_diamond( self.screen,(self.rect.left + 18, cy),8,line_color,  glow=True )
        
          draw_diamond( self.screen, (self.rect.right - 18, cy),8,line_color, width=1, glow=True)
        
          self.screen.blit(self.msg_image, self.msg_image_rect )

    @property
    def label(self):
        return self.msg
    @property
    def center(self):
        return self.rect.center

    def change(self, direction):
        pass   # кнопке нечего крутить — но метод ОБЯЗАН быть

    def draw(self, screen, font, color, dim_color):
        self.draw_button()

