import pygame
from pathlib import Path

class SoundManager:
    def __init__(self, music_volume=0.3, effects_volume=0.5):
        self.enable=False
        try:
            sounds_dir=Path(__file__).parent/"sounds"
            self.laser = pygame.mixer.Sound(sounds_dir/"laser.wav")
            self.laser_big = pygame.mixer.Sound(sounds_dir/ "laser_big.wav")
            self.explosion = pygame.mixer.Sound(sounds_dir / "explosion.wav")
            self.hit = pygame.mixer.Sound(sounds_dir / "hit.wav")
            self.menu = pygame.mixer.Sound(sounds_dir / "Menu.wav")
            # отдельных wav для этих событий пока нет — берём существующие файлы
            self.boost = pygame.mixer.Sound(sounds_dir / "laser2.wav")
            self.levelup = pygame.mixer.Sound(sounds_dir / "laser2.wav")
            self.gameover = pygame.mixer.Sound(sounds_dir / "explosion.wav")
            pygame.mixer.music.load(sounds_dir / "Menu.wav")
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
            self.enable = True
            self.set_effects_volume(effects_volume)
        except Exception as e:
            print("Error:",e)

    def play(self,name):
        if not self.enable:
            return
        sound=getattr(self,name,None)
        if sound is not None:
            sound.play()
    def set_effects_volume(self, volume):
     if not self.enable:
        return
     for name in ("laser", "laser_big", "explosion", "hit", "menu", "boost", "levelup", "gameover"):
        sound = getattr(self, name, None)
        if sound is not None:
            sound.set_volume(volume)

