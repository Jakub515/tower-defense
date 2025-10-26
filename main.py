import pygame
import sys
import os
import time

# Import Twoich modułów
import load_images
import enemie
import levels
import soldiers
import shop
import menu_bar

# --- INICJALIZACJA PYGAME ---
pygame.init()
pygame.font.init()

# --- GŁÓWNE USTAWIENIA ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense - Zrekonstruowany Main.py")

clock = pygame.time.Clock()
FPS = 60

# --- CZCIONKI ---
main_font = pygame.font.SysFont("Arial", 24)
wave_font = pygame.font.SysFont("Arial", 38)
font_large = pygame.font.SysFont("Arial", 72)

# --- ŁADOWANIE OBRAZÓW I TŁA ---
image_loader = load_images.ImageLoad()

# Załaduj mapę
map_image = image_loader.get_image("maps/map1.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
if map_image is None:
    print("BŁĄD: Nie można załadować 'maps/map1.png'. Upewnij się, że plik istnieje.")
    # Stwórz zastępcze tło, jeśli mapa się nie załaduje
    map_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    map_image.fill((50, 50, 50))

# --- BAZA DANYCH ŻOŁNIERZY (MUSISZ DOSTOSOWAĆ TE WARTOŚCI) ---
# To jest kluczowy brakujący element, który musiałem zaimprowizować.
# Format: "klucz": { dane... }
SOLDIER_DATA = {
    "soldier": {
        "shop_img": "soldiers_buy/soldier.png",
        "desc": "Zwykły żołnierz. Zrównoważone statystyki.",
        "price": 100,
        "idle_img": "soldiers/soldier.png",
        "attack_img": "soldiers/soldier_shot.png",
        "range": 150,
        "fire_freq": 1.0,  # sekundy
        "fire_power": 10
    },
    "scout": {
        "shop_img": "soldiers_buy/scout.png",
        "desc": "Szybki zwiadowca. Strzela szybko, małe obrażenia.",
        "price": 120,
        "idle_img": "soldiers/scout.png",
        "attack_img": "soldiers/scout_shot.png",
        "range": 130,
        "fire_freq": 0.5,
        "fire_power": 6
    },
    "sniper": {
        "shop_img": "soldiers_buy/sniper.png",
        "desc": "Snajper. Ogromny zasięg i obrażenia, ale wolno strzela.",
        "price": 300,
        "idle_img": "soldiers/sniper.png",
        "attack_img": "soldiers/sniper_shot.png",
        "range": 350,
        "fire_freq": 2.5,
        "fire_power": 55
    },
    "shotgunner": {
        "shop_img": "soldiers_buy/shotgunner.png",
        "desc": "Strzelec. Mały zasięg, ale duże obrażenia.",
        "price": 250,
        "idle_img": "soldiers/shotgunner.png",
        "attack_img": "soldiers/shotgunner_shot.png",
        "range": 100,
        "fire_freq": 1.2,
        "fire_power": 30
    },
    "enforcer": {
        "shop_img": "soldiers_buy/enforcer.png",
        "desc": "Egzekutor. Wolny, ale potężny.",
        "price": 400,
        "idle_img": "soldiers/enforcer.png",
        "attack_img": "soldiers/enforcer_shot.png",
        "range": 140,
        "fire_freq": 1.5,
        "fire_power": 40
    },
    "mercenary": {
        "shop_img": "soldiers_buy/mercenary.png",
        "desc": "Najemnik. Drogi, ale skuteczny. Dobry zasięg i obrażenia.",
        "price": 500,
        "idle_img": "soldiers/mercenary.png",
        "attack_img": "soldiers/mercenary_shot.png",
        "range": 200,
        "fire_freq": 1.0,
        "fire_power": 45
    },
    "railgunner": {
        "shop_img": "soldiers_buy/railgunner.png",
        "desc": "Strzelec wyborowy. Ekstremalne obrażenia, bardzo wolny.",
        "price": 750,
        "idle_img": "soldiers/railgunner.png",
        "attack_img": "soldiers/railgunner_shot.png",
        "range": 300,
        "fire_freq": 3.0,
        "fire_power": 150
    },
    "commander": { # "commando" w /soldiers/, "commander" w /soldiers_buy/
        "shop_img": "soldiers_buy/commander.png",
        "desc": "Komandos. Szybkostrzelny, dobre obrażenia.",
        "price": 600,
        "idle_img": "soldiers/commando.png",
        "attack_img": "soldiers/commando_shot.png",
        "range": 180,
        "fire_freq": 0.4,
        "fire_power": 15
    },
    "GROM": {
        "shop_img": "soldiers_buy/GROM.png",
        "desc": "Jednostka GROM. Elitarny, wszechstronny żołnierz.",
        "price": 800,
        "idle_img": "soldiers/GROM.png",
        "attack_img": "soldiers/GROM_shot.png",
        "range": 220,
        "fire_freq": 0.7,
        "fire_power": 50
    },
    "gold_scout": { # "GS" w /soldiers/
        "shop_img": "soldiers_buy/gold_scout.png",
        "desc": "Złoty Zwiadowca. Ekstremalnie szybki ostrzał.",
        "price": 1000,
        "idle_img": "soldiers/GS.png",
        "attack_img": "soldiers/GS_shot.png",
        "range": 160,
        "fire_freq": 0.2,
        "fire_power": 12
    },
    "gold_commander": { # "GC" w /soldiers/
        "shop_img": "soldiers_buy/gold_commander.png",
        "desc": "Złoty Komandos. Najlepsza jednostka, ogromna siła ognia.",
        "price": 2500,
        "idle_img": "soldiers/GC.png",
        "attack_img": "soldiers/GC_shot.png",
        "range": 250,
        "fire_freq": 0.3,
        "fire_power": 35
    }
}

# Kolejność w sklepie musi odpowiadać plikowi load_images.py
SOLDIER_ORDER = [
    "commander", "enforcer", "gold_commander", "gold_scout", "GROM",
    "mercenary", "railgunner", "scout", "shotgunner", "sniper", "soldier"
]

# --- INSTANCJE KLAS GRY ---

# Stwórz obiekty handlerów
enemy_handler = enemie.Enemie()
level_handler = levels.Levels() # To automatycznie ładuje obrazy wrogów
soldier_handler = soldiers.Soldier(map_image) # Przekaż mapę do sprawdzania kolizji

# --- PRZYGOTOWANIE SKLEPU I UI ---

# Listy danych dla sklepu
soldier_list_shop = [] # Dla konstruktora Shop (obraz, opis, cena)
soldier_data_list = [] # Dla logiki gry (pełne dane)

for key in SOLDIER_ORDER:
    data = SOLDIER_DATA[key]
    
    # 1. Załaduj obrazy
    shop_image = image_loader.get_image(data["shop_img"], 100)
    idle_image = image_loader.get_image(data["idle_img"], 40)
    attack_image = image_loader.get_image(data["attack_img"], 40)
    
    # 2. Dodaj do listy dla sklepu (to widzi klasa Shop)
    soldier_list_shop.append(
        (shop_image, data["desc"], data["price"])
    )
    
    # 3. Dodaj do głównej listy danych (do użytku w main.py)
    soldier_data_list.append({
        "price": data["price"],
        "idle_surface": idle_image,
        "attack_surface": attack_image,
        "range": data["range"],
        "fire_freq": data["fire_freq"],
        "fire_power": data["fire_power"]
    })

# Załaduj obrazy dla UI
start_wave_img = image_loader.get_image("buttons_and_else/start_wave.png", 50)
cash_icon_img = image_loader.get_image("buttons_and_else/money.png", 10)
live_icon_img = image_loader.get_image("buttons_and_else/health.png", 7)
right_arrow_img = image_loader.get_image("buttons_and_else/right_buy.png", 100)
left_arrow_img = image_loader.get_image("buttons_and_else/left_buy.png", 100)
win_image = image_loader.get_image("buttons_and_else/you_win.png", 100)
bin_image = image_loader.get_image("buttons_and_else/bin.png", 100)
wave_text_surface = image_loader.get_image("buttons_and_else/wave.png", 100)

# Stwórz instancje UI
menu_bar_ui = menu_bar.MenuBar(
    start_wave_img,
    cash_icon_img,
    live_icon_img,
    main_font,
    SCREEN_WIDTH
)

shop_ui = shop.Shop(
    right_arrow_img,
    left_arrow_img,
    soldier_list_shop, # Przekaż listę (obraz, opis, cena)
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    main_font
)

# --- ZMIENNE STANU GRY ---
running = True
player_cash = 500  # Pieniądze na start
player_lives = 20  # Życie na start

current_wave_index = -1
wave_in_progress = False
wave_enemies_to_spawn = [] # Lista wrogów do wysłania w tej fali
spawn_timer = 0.0

mouse_x, mouse_y = 0, 0
click_state = False # Czy przycisk jest wciśnięty
click_event = False # True tylko przez jedną klatkę po kliknięciu

# Stan stawiania żołnierza
is_placing_soldier = False
placing_soldier_index = -1 # Indeks z `soldier_data_list`

# Stan wygranej/przegranej
game_over = False
game_won = False

# Przycisk sprzedaży
bin_rect = bin_image.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))


# --- GŁÓWNA PĘTLA GRY ---
while running:

    # --- Obsługa Zdarzeń (wewnętrzne) ---
    click_event = False
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click_state = True
                click_event = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                click_state = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_placing_soldier = False
                soldier_handler.setup_soldier_list = []
                soldier_handler.selected_soldier_index = None

    # -------------------------
    # 1) Najpierw: RZUĆ MAPĘ
    # -------------------------
    window.blit(map_image, (0, 0))

    # ---------------------------------------------------
    # 2) WAŻNE: Pobierz wejście UI (kliknięcia) na początku
    #    — to daje nam wartości sterujące (start_wave, shop)
    #    mimo że UI będzie narysowane dopiero na końcu.
    #    (UWAGA: to wywołanie może też narysować UI "pod" żołnierzami;
    #     dlatego po rysowaniu wszystkiego wywołamy update() ponownie
    #     aby narysować UI na wierzchu.)
    # ---------------------------------------------------
    start_wave_clicked = menu_bar_ui.update(window, mouse_x, mouse_y, click_state, player_cash, player_lives)
    shop_item_index = shop_ui.update(window, mouse_x, mouse_y, click_event, player_cash)

    # --- Logika Gry (tylko jeśli gra się toczy) ---
    if not game_over and not game_won:

        # 2. Logika Sklepu (Kupowanie)
        if shop_item_index is not False and click_event:
            soldier_to_buy_data = soldier_data_list[shop_item_index]

            if player_cash >= soldier_to_buy_data["price"]:
                is_placing_soldier = True
                placing_soldier_index = shop_item_index
                shop_ui.shop_state = False

                soldier_handler.setup_soldier(
                    soldier_to_buy_data["idle_surface"],
                    mouse_x,
                    mouse_y,
                    shop_item_index
                )
                soldier_handler.selected_soldier_index = None
            else:
                print("Za mało gotówki!")
                is_placing_soldier = False

        # 3. Logika Stawiania Żołnierza
        if is_placing_soldier:
            placement_result = soldier_handler.update_setup_soldier(mouse_x, mouse_y, click_event)

            if placement_result and placement_result[0]:
                placed_data_info = placement_result[1]
                soldier_index = placed_data_info[3]
                soldier_pos = placed_data_info[1]

                soldier_data = soldier_data_list[soldier_index]

                success = soldier_handler.new_soldier(
                    soldier_data["idle_surface"],
                    soldier_data["range"],
                    soldier_data["attack_surface"],
                    soldier_pos,
                    soldier_data["fire_freq"],
                    soldier_data["fire_power"]
                )

                if success:
                    player_cash -= soldier_data["price"]
                else:
                    print("Ostateczne sprawdzenie położenia nie powiodło się.")

                is_placing_soldier = False
                placing_soldier_index = -1

        elif click_event:
            if bin_rect.collidepoint(mouse_x, mouse_y) and soldier_handler.selected_soldier_index is not None:
                soldier_to_sell_index = soldier_handler.selected_soldier_index
                soldier_handler.delete_soldier(soldier_to_sell_index)
                soldier_handler.selected_soldier_index = None
            else:
                soldier_handler.handle_click((mouse_x, mouse_y))

        # 4. Logika Fal
        if start_wave_clicked and not wave_in_progress:
            wave_in_progress = True
            current_wave_index += 1

            if current_wave_index >= len(levels.waves):
                game_won = True
                wave_in_progress = False
            else:
                wave_data = level_handler.next_wave()
                wave_enemies_to_spawn = wave_data.copy()
                spawn_timer = time.time()
                print(f"Rozpoczynanie fali {current_wave_index + 1}")

        # 5. Spawnowanie Wrogów
        if wave_in_progress and wave_enemies_to_spawn:
            now = time.time()
            spawn_delay = wave_enemies_to_spawn[0][1]

            if now - spawn_timer >= spawn_delay:
                enemy_type_index = wave_enemies_to_spawn.pop(0)[0]
                enemy_data = level_handler.get_enemie_data(enemy_type_index)

                enemy_handler.new_enemy(
                    enemy_data[0],
                    enemy_data[1],
                    enemy_data[2],
                    enemy_data[3],
                    enemy_data[4]
                )
                spawn_timer = now

        # 6. Aktualizacja Wrogów (Ruch)
        active_enemy_list = enemy_handler.update()

        # 7. Przygotowanie danych dla Żołnierzy
        enemies_data_for_soldiers = []
        enemies_to_remove = []
        cash_to_add = 0

        for i, enemy_instance in enumerate(active_enemy_list):
            if enemy_instance[6]:
                player_lives -= enemy_instance[2]
                enemies_to_remove.append(i)
            elif enemy_instance[1] <= 0:
                cash_to_add += enemy_instance[7]
                enemies_to_remove.append(i)
            else:
                enemies_data_for_soldiers.append({
                    "pos": enemy_handler.get_position(enemy_instance),
                    "surface": enemy_instance[0],
                    "path_progress": enemy_instance[3],
                    "index": i
                })

        player_cash += cash_to_add

        for i in sorted(enemies_to_remove, reverse=True):
            enemy_handler.enemie_list.pop(i)

        # 8. Aktualizacja Żołnierzy (Atakowanie)
        soldier_draw_list, shots_fired = soldier_handler.update(enemies_data_for_soldiers)

        # 9. Obsługa Strzałów
        for shot in shots_fired:
            enemy_index_to_shoot = shot[0]
            damage = shot[1]
            reward = enemy_handler.shot(enemy_index_to_shoot, damage)
            player_cash += reward

        # 10. Sprawdzenie Końca Fali
        if wave_in_progress and not wave_enemies_to_spawn and not enemy_handler.enemie_list:
            wave_in_progress = False
            print(f"Fala {current_wave_index + 1} zakończona!")

        # 11. Sprawdzenie Przegranej
        if player_lives <= 0:
            player_lives = 0
            game_over = True
            print("KONIEC GRY")

    # -------------------------
    # 3) Rysowanie: w kolejności:
    #    a) Wrogowie
    #    b) Żołnierze
    #    c) (podgląd stawiania)
    # -------------------------

    # 3.a Rysowanie Wrogów
    current_enemy_list_for_drawing = enemy_handler.enemie_list
    for enemy_instance in current_enemy_list_for_drawing:
        pos = enemy_handler.get_position(enemy_instance)
        surface = enemy_instance[0]
        draw_x = pos[0] - surface.get_width() // 2
        draw_y = pos[1] - surface.get_height() // 2
        window.blit(surface, (draw_x, draw_y))
        enemy_handler.draw_health_bar(window, pos, enemy_instance[1], enemy_instance[9])

    # 3.b Rysowanie Żołnierzy
    for surface, rect in soldier_draw_list:
        window.blit(surface, rect)

    # 3.c Rysowanie Stawianego Żołnierza (Podgląd)
    if is_placing_soldier and soldier_handler.setup_soldier_list:
        setup_data = soldier_handler.setup_soldier_list
        surface = setup_data[0]
        pos = setup_data[1]
        is_invalid = setup_data[2]
        surface_copy = surface.copy()
        surface_copy.set_alpha(150)
        window.blit(surface_copy, pos)

        soldier_index = setup_data[3]
        range_radius = soldier_data_list[soldier_index]["range"]
        circle_surf = pygame.Surface((range_radius * 2, range_radius * 2), pygame.SRCALPHA)
        circle_color = (255, 0, 0, 40) if is_invalid else (100, 150, 250, 40)
        pygame.draw.circle(circle_surf, circle_color, (range_radius, range_radius), range_radius)
        circle_rect = circle_surf.get_rect(center=(mouse_x, mouse_y))
        window.blit(circle_surf, circle_rect)

    # -------------------------
    # 4) Na koniec: narysuj UI (menu bar i sklep) — wywołanie update() ponownie
    #    żeby UI było zawsze na wierzchu.
    # -------------------------
    menu_bar_ui.update(window, mouse_x, mouse_y, click_state, player_cash, player_lives)
    shop_ui.update(window, mouse_x, mouse_y, click_event, player_cash)

    # Dodatkowe rysunki UI (fala, kosz)
    #window.blit(wave_text_surface, (SCREEN_WIDTH // 2 - wave_text_surface.get_width() - 10, 10))
    wave_num_text = wave_font.render("Wave: "+str(current_wave_index + 1), True, (0, 0, 0))
    window.blit(wave_num_text, (SCREEN_WIDTH // 2 - 70, 20))

    if soldier_handler.selected_soldier_index is not None:
        window.blit(bin_image, bin_rect)

    # 6. Rysowanie Ekranu Końca Gry / Wygranej
    if game_over:
        go_text = font_large.render("KONIEC GRY", True, (255, 0, 0))
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))
        window.blit(go_text, go_rect)
    elif game_won:
        win_rect = win_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        window.blit(overlay, (0, 0))
        window.blit(win_image, win_rect)

    # --- Aktualizacja Ekranu ---
    pygame.display.flip()
    clock.tick(FPS)

# --- Zakończenie Gry ---
pygame.quit()
sys.exit()