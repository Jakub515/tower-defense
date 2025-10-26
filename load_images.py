import pygame
import os

pygame.init()

list_image_name = assets = [
    # buttons_and_else
    "buttons_and_else/bin.png",
    "buttons_and_else/bum.png",
    "buttons_and_else/buy.png",
    "buttons_and_else/health.png",
    "buttons_and_else/left_buy.png",
    "buttons_and_else/money.png",
    "buttons_and_else/right_buy.png",
    "buttons_and_else/start_wave.png",
    "buttons_and_else/wave.png",
    "buttons_and_else/you_win.png",

    # enemies
    "enemies/Boss1.png",
    "enemies/Boss2.png",
    "enemies/Boss3.png",
    "enemies/Boss4.png",
    "enemies/Guardian.png",
    "enemies/Hidden.png",
    "enemies/Hidden_Boss.png",
    "enemies/Lava.png",
    "enemies/Lightning.png",
    "enemies/Normal.png",
    "enemies/Slime.png",
    "enemies/Slow.png",
    "enemies/Speedy.png",
    "enemies/Void.png",

    # maps
    "maps/map.png",
    "maps/map1.png",
    "maps/map2.png",

    # soldiers
    "soldiers/commando.png",
    "soldiers/commando_shot.png",
    "soldiers/enforcer.png",
    "soldiers/enforcer_shot.png",
    "soldiers/GC.png",
    "soldiers/GC_shot.png",
    "soldiers/GROM.png",
    "soldiers/GROM_shot.png",
    "soldiers/GS.png",
    "soldiers/GS_shot.png",
    "soldiers/mercenary.png",
    "soldiers/mercenary_shot.png",
    "soldiers/railgunner.png",
    "soldiers/railgunner_shot.png",
    "soldiers/scout.png",
    "soldiers/scout_shot.png",
    "soldiers/shotgunner.png",
    "soldiers/shotgunner_shot.png",
    "soldiers/sniper.png",
    "soldiers/sniper_shot.png",
    "soldiers/soldier.png",
    "soldiers/soldier_shot.png",

    # soldiers_buy
    "soldiers_buy/commander.png",
    "soldiers_buy/enforcer.png",
    "soldiers_buy/gold_commander.png",
    "soldiers_buy/gold_scout.png",
    "soldiers_buy/GROM.png",
    "soldiers_buy/mercenary.png",
    "soldiers_buy/railgunner.png",
    "soldiers_buy/scout.png",
    "soldiers_buy/shotgunner.png",
    "soldiers_buy/sniper.png",
    "soldiers_buy/soldier.png"
]



class ImageLoad:
    def __init__(self):
        self.image_dict = {}
        for name in list_image_name:
            image = pygame.image.load(name)
            # Sprawdzanie, czy obrazek ma kanał alfa i konwersja
            if image.get_alpha():
                self.image_dict[name] = image.convert_alpha()
            else:
                self.image_dict[name] = image.convert()

    def get_image(self, name, scale):
        image = self.image_dict.get(name)
        ret = None
        if not image:
            ret = None
        elif isinstance(scale, (list, tuple)):
            if len(scale) == 2:
                width, height = scale
                ret = pygame.transform.scale(image, (width, height))
            elif len(scale) == 1:
                percent = scale[0] / 100
                width = int(image.get_width() * percent)
                height = int(image.get_height() * percent)
                ret = pygame.transform.scale(image, (width, height))
        elif isinstance(scale, (int, float)):
            percent = scale / 100
            width = int(image.get_width() * percent)
            height = int(image.get_height() * percent)
            ret = pygame.transform.scale(image, (width, height))
        
        return ret