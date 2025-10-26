import pygame
import time
import math

class Soldier:
    def __init__(self, map_surface):
        self.soldier_list = []
        self.map = map_surface
        self.allowed_colors = [(202, 158, 83)] 
        self.setup_soldier_list = []
        self.selected_soldier_index = None # NEW: To track the selected soldier

    def _generate_allowed_placement_mask(self, map_surface, allowed_colors):
        mask = pygame.mask.Mask(map_surface.get_size())
        for x in range(map_surface.get_width()):
            for y in range(map_surface.get_height()):
                color_at_map_pos = map_surface.get_at((x, y))[:3]
                if color_at_map_pos in allowed_colors:
                    mask.set_at((x, y), 1)
        return mask

    def check_placement_validity(self, image_surface, image_pos, soldier_list_to_check):
        int_image_pos_x = int(image_pos[0])
        int_image_pos_y = int(image_pos[1])
        image_rect = image_surface.get_rect(topleft=(int_image_pos_x, int_image_pos_y))

        if not self.map.get_rect().contains(image_rect):
            return False

        for x_img in range(image_surface.get_width()):
            for y_img in range(image_surface.get_height()):
                if image_surface.get_at((x_img, y_img)).a > 0:
                    map_x = int_image_pos_x + x_img
                    map_y = int_image_pos_y + y_img
                    
                    if not (0 <= map_x < self.map.get_width() and 0 <= map_y < self.map.get_height() and
                            self.map.get_at((map_x, map_y))[:3] in self.allowed_colors):
                        return False

        new_soldier_placement_mask = pygame.mask.from_surface(image_surface) 

        for i, soldier_in_list in enumerate(soldier_list_to_check):
            existing_soldier_mask = soldier_in_list[10] 
            existing_soldier_rect = soldier_in_list[13] 

            if existing_soldier_mask is None or existing_soldier_rect is None:
                continue 

            if image_rect.colliderect(existing_soldier_rect):
                offset_x = existing_soldier_rect.x - image_rect.x
                offset_y = existing_soldier_rect.y - image_rect.y

                if new_soldier_placement_mask.overlap(existing_soldier_mask, (offset_x, offset_y)):
                    return False

        return True

    def new_soldier(self, surface_idle, range_, surface_attack, pos, fire_freq_sec, fire_power):
        if not self.check_placement_validity(surface_idle, pos, self.soldier_list):
            return False
            
        soldier_mask_initial = pygame.mask.from_surface(surface_idle) 

        range_radius = range_
        circle_surface = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        circle_color = (100, 150, 250, 40)
        pygame.draw.circle(circle_surface, circle_color, (range_radius, range_radius), range_radius)

        self.soldier_list.append([
            surface_idle,       # 0 - idle surface (original)
            surface_attack,     # 1 - attack surface (original)
            range_,             # 2
            list(pos),          # 3 - pos (list, mutable)
            fire_freq_sec,      # 4
            fire_power,         # 5
            False,              # 6 - is_attacking
            0.0,                # 7 - direction (angle in degrees)
            0.0,                # 8 - last_fire_time
            0.0,                # 9 - last_attack_animation_time
            soldier_mask_initial, # 10 - Mask for the current visual representation
            circle_surface,     # 11 - Range circle surface
            None,               # 12 - current_rotated_surface
            None,               # 13 - current_rotated_rect
            -999.0,             # 14 - previous_direction
            False               # 15 - previous_is_attacking
        ])
        return True

    def update(self, enemies_data):
        updated_draws = []
        shots_fired = []
        now = time.time()

        for i, soldier in enumerate(self.soldier_list):
            x, y = soldier[3]
            idle_surface = soldier[0]
            soldier_center_x = x + idle_surface.get_width() // 2
            soldier_center_y = y + idle_surface.get_height() // 2
            
            target_enemy_farthest = None
            max_progress = -1

            for enemy in enemies_data:
                ex, ey = enemy['pos']
                enemy_radius = enemy['surface'].get_width() // 2
                effective_range = soldier[2] + enemy_radius
                dist = math.hypot(ex - soldier_center_x, ey - soldier_center_y)
                
                if dist <= effective_range:
                    if enemy['path_progress'] > max_progress:
                        max_progress = enemy['path_progress']
                        target_enemy_farthest = enemy
            
            is_currently_attacking = False
            if target_enemy_farthest:
                is_currently_attacking = True
                closest_target_pos = target_enemy_farthest['pos']
                closest_target_index = target_enemy_farthest['index']
                dx = closest_target_pos[0] - soldier_center_x
                dy = closest_target_pos[1] - soldier_center_y
                current_direction = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
                soldier[7] = current_direction 

                if now - soldier[8] >= soldier[4]:
                    shots_fired.append([closest_target_index, soldier[5]])
                    soldier[8] = now
                    soldier[9] = now
            
            soldier[6] = is_currently_attacking
            if now - soldier[9] < 0.05:
                current_surface_to_draw = soldier[1]
            else:
                current_surface_to_draw = soldier[0]
            
            previous_direction = soldier[14]
            previous_is_attacking_state_for_surface = soldier[15] 
            effective_current_direction = soldier[7] 
            
            is_surface_type_changed = (current_surface_to_draw == soldier[1] and not previous_is_attacking_state_for_surface) or \
                                      (current_surface_to_draw == soldier[0] and previous_is_attacking_state_for_surface)

            if effective_current_direction != previous_direction or is_surface_type_changed or soldier[12] is None:
                rotated_surface = pygame.transform.rotate(current_surface_to_draw, effective_current_direction)
                soldier[10] = pygame.mask.from_surface(rotated_surface)
                original_rect = current_surface_to_draw.get_rect(topleft=(int(x), int(y)))
                rect = rotated_surface.get_rect(center=original_rect.center)
                soldier[12] = rotated_surface
                soldier[13] = rect
                soldier[14] = effective_current_direction
                soldier[15] = (current_surface_to_draw == soldier[1])
            else:
                rotated_surface = soldier[12]
                rect = soldier[13]

            # --- MODIFIED --- Only draw the circle for the selected soldier
            if i == self.selected_soldier_index:
                circle_surface = soldier[11]
                circle_rect = circle_surface.get_rect(center=(soldier_center_x, soldier_center_y))
                updated_draws.append((circle_surface, circle_rect))

            updated_draws.append((rotated_surface, rect))

        return updated_draws, shots_fired
    
    # --- NEW --- Method to handle clicks for selection/deselection
    def handle_click(self, mouse_pos):
        # Check if the click is on any existing soldier
        for i, soldier in enumerate(self.soldier_list):
            rect = soldier[13] # The soldier's current rect
            if rect and rect.collidepoint(mouse_pos):
                # Using the mask to check  for clicks on transparent parts
                mask = soldier[10]
                offset_x = mouse_pos[0] - rect.x
                offset_y = mouse_pos[1] - rect.y
                if mask.get_at((offset_x, offset_y)):
                    self.selected_soldier_index = i
                    return # Exit after finding the clicked soldier

        # If the click was not on any soldier, deselect
        self.selected_soldier_index = None

    def delete_soldier(self, index):
        if 0 <= index < len(self.soldier_list):
            return self.soldier_list.pop(index)

    def setup_soldier(self, surface, m_x, m_y, index):
        # --- MODIFIED --- Deselect any soldier when starting to place a new one
        self.selected_soldier_index = None 
        self.setup_soldier_list = []
        # Center the image on the mouse cursor
        pos_x = m_x - surface.get_width() // 2
        pos_y = m_y - surface.get_height() // 2
        self.setup_soldier_list.append(surface)
        self.setup_soldier_list.append([pos_x, pos_y])
        self.setup_soldier_list.append(False) 
        self.setup_soldier_list.append(index)
        self.setup_soldier_list.append(time.time())

    def update_setup_soldier(self, m_x, m_y, click):
        if not self.setup_soldier_list:
            return False
        if self.setup_soldier_list[4] + 0.1 > time.time():
            return [False, self.setup_soldier_list]
        surface = self.setup_soldier_list[0]
        # Center the image on the mouse cursor
        pos_x = m_x - surface.get_width() // 2
        pos_y = m_y - surface.get_height() // 2
        self.setup_soldier_list[1] = [pos_x, pos_y] 
        new_soldier_pos = self.setup_soldier_list[1]

        is_valid_placement = self.check_placement_validity(surface, new_soldier_pos, self.soldier_list)

        if not is_valid_placement:
            self.setup_soldier_list[2] = True
        else:
            self.setup_soldier_list[2] = False
            if click:
                a = self.setup_soldier_list.copy()
                self.setup_soldier_list = []
                return [True, a]
                
        return [False, self.setup_soldier_list]