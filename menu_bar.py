import pygame

class MenuBar:
    def __init__(self, start_wave_surface, cash_icon_surface, live_icon_surface, font, cxx):
        self.start_wave_surface = start_wave_surface
        self.cash_icon_surface = cash_icon_surface
        self.live_icon_surface = live_icon_surface
        self.font = font
        self.cxx = cxx
        self.start_wave_rect = self.start_wave_surface.get_rect(topleft=(10, 10))

    @staticmethod
    def collide(x, y, w, h, a, b):
        return (a >= x and a <= x + w) and (b >= y and b <= y + h)

    @staticmethod
    def apply_brightness(surface, brightness):
        result = surface.copy().convert_alpha()
        color = (abs(brightness), abs(brightness), abs(brightness))
        if brightness > 0:
            result.fill(color, special_flags=pygame.BLEND_RGB_ADD)
        else:
            result.fill(color, special_flags=pygame.BLEND_RGB_SUB)
        return result

    def update(self, window, mouse_x, mouse_y, click_state, cash, lives):
        ret = False
        window.blit(self.start_wave_surface, self.start_wave_rect)

        if self.start_wave_rect.collidepoint(mouse_x, mouse_y):
            if click_state:
                window.blit(self.apply_brightness(self.start_wave_surface, -50), self.start_wave_rect)
                ret = True
            else:
                window.blit(self.apply_brightness(self.start_wave_surface, 50), self.start_wave_rect)
                ret = False

        window.blit(self.cash_icon_surface, (self.start_wave_rect.right + 15, 10))
        window.blit(self.font.render(str(cash), True, (255, 255, 255)), (self.start_wave_rect.right + 15 + self.cash_icon_surface.get_width() + 5, 20))

        lives_text_surface = self.font.render(str(lives), True, (255, 255, 255))
        window.blit(lives_text_surface, (self.cxx - 80, 20))
        window.blit(self.live_icon_surface, (self.cxx - 80 - 55, 10))

        return ret