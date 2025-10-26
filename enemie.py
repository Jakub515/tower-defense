import math
import pygame

class Enemie:
    def __init__(self):
        self.enemie_list = []
        self.list_route = [
            [635, 0], [635, 170], [240, 170], [240, 558], [850, 558], [850, 415],
            [455, 415], [455, 290], [1035, 290], [1035, 720], [20, 720]
        ]

    def _segment_lengths(self, route):
        segments = []
        total = 0
        for i in range(len(route) - 1):
            x1, y1 = route[i]
            x2, y2 = route[i + 1]
            length = math.hypot(x2 - x1, y2 - y1)
            segments.append((length, total))
            total += length
        return segments, total

    def new_enemy(self, surface, speed, hp, end_power, reward):
        segments, total_len = self._segment_lengths(self.list_route)
        self.enemie_list.append([
            surface,      # 0 - surface
            hp,           # 1 - current HP
            end_power,    # 2 - damage if reaches end
            0.0,          # 3 - distance_travelled
            segments,     # 4 - segment info
            total_len,    # 5 - total distance
            False,        # 6 - reached end
            reward,       # 7 - cash reward
            speed,        # 8 - px/frame
            hp            # 9 - max HP (do paska życia)
        ])

    def update(self):
        for enemy in self.enemie_list:
            if not enemy[6]:
                enemy[3] += enemy[8]
                if enemy[3] >= enemy[5]:
                    enemy[6] = True
        return self.enemie_list

    def get_position(self, enemy):
        distance = enemy[3]
        route = self.list_route
        segments = enemy[4]

        for i, (seg_len, acc_len) in enumerate(segments):
            if distance < acc_len + seg_len:
                t = (distance - acc_len) / seg_len
                x1, y1 = route[i]
                x2, y2 = route[i + 1]
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                return [int(x), int(y)]
        return route[-1]

    def draw_health_bar(self, window, pos, current_hp, max_hp, width=36, height=7):
        if max_hp <= 0:
            return

        # Oblicz proporcję
        ratio = max(0, min(1.0, current_hp / max_hp))
        bar_width = int(width * ratio)

        # Pozycja
        x = pos[0] - width // 2
        y = pos[1] - 22

        # --- Tło (ciemnoczerwone) ---
        pygame.draw.rect(window, (20, 0, 0), (x, y - height, width, 2 * height))
        pygame.draw.circle(window, (20, 0, 0), (x, y), height)
        pygame.draw.circle(window, (20, 0, 0), (x + width, y), height)

        # --- Kolor paska (jaśniejszy + dynamiczna jasność) ---
        red = int(80 + (255 - 80) * (1 - ratio))
        green = int(80 + (255 - 80) * ratio)

        # Jasność zwiększona w środku
        whiteness = 0.5 * (1 - abs(0.5 - ratio) * 2)
        fill_color = (int(red + (255 - red) * whiteness),int(green + (255 - green) * whiteness),int((0 + (255 - 0) * whiteness)))

        # --- Pasek zdrowia ---
        if ratio > 0:
            # Minimalna szerokość, jeśli życie prawie 0
            min_bar_width = 2
            draw_width = max(bar_width, min_bar_width)
            inner_radius = height - 2

            # Zmniejszona jasność i przezroczystość przy minimalnym HP
            #if bar_width < min_bar_width + 1:
            #    # Zblenduj z tłem (ciemny kolor + lekki połysk)
            #    fill_color = (120, 40, 40)
            pygame.draw.rect(window, fill_color, (x, y - inner_radius, draw_width, 2 * inner_radius))
            pygame.draw.circle(window, fill_color, (x, y), inner_radius)
            pygame.draw.circle(window, fill_color, (x + draw_width, y), inner_radius)


    def shot(self, index, power):
        try:
            self.enemie_list[index][1] -= power
            if self.enemie_list[index][1] <= 0:
                reward = self.enemie_list[index][7]
                self.enemie_list.pop(index)
                return reward
            return 0
        except IndexError:
            return 0

    def remove_enemy(self, index):
        reward = self.enemie_list[index][2]
        self.enemie_list.pop(index)
        return reward
