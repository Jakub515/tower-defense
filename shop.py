import pygame

class Shop:
    def __init__(self,right_arrow, left_arrow, soldier_list, cxx, cyy, font): 
        # Inicjalizacja sklepu – ustawienie strzałek, listy żołnierzy, pozycji i czcionki
        self.soldier_list = soldier_list
        self.right_arrow_normal = right_arrow        # Obraz strzałki w prawo (normalny)
        self.left_arrow_normal = left_arrow          # Obraz strzałki w lewo (normalny)
        # Tworzymy jaśniejsze wersje strzałek (np. efekt najechania myszą)
        self.right_arrow_bright = self.apply_brightness(right_arrow,50)
        self.left_arrow_bright = self.apply_brightness(left_arrow,50)
        self.cxx = cxx                               # Szerokość okna (środek X)
        self.cyy = cyy                               # Wysokość okna (środek Y)
        self.shop_state = False                      # Czy sklep jest otwarty
        self.bright_state = False                    # Czy przycisk ma być rozjaśniony (hover)
        self.font = font                             # Czcionka używana w sklepie
        self.shop_width = 430                        # Szerokość panelu sklepu
        self.shop_x_start = self.cxx - self.shop_width  # Początek sklepu (X)

    @staticmethod
    def colide(x,y,w,h,a,b):
        # Sprawdza, czy punkt (a,b) znajduje się wewnątrz prostokąta (x, y, w, h)
        if((a >= x and a <= x+w) and (b >= y and b <= y+h)):
            return True
        return False

    @staticmethod
    def apply_brightness(surface, brightness):
        """
        Zmienia jasność powierzchni podobnie jak w Scratchu.
        brightness = 0 → oryginał
        brightness > 0 → jaśniejszy
        brightness < 0 → ciemniejszy
        """
        result = surface.copy().convert_alpha()

        # Jasność dodatnia – dodajemy kolor (rozjaśnienie)
        if brightness > 0:
            color = (brightness, brightness, brightness)
            result.fill(color, special_flags=pygame.BLEND_RGB_ADD)

        # Jasność ujemna – odejmujemy kolor (przyciemnienie)
        elif brightness < 0:
            color = (-brightness, -brightness, -brightness)
            result.fill(color, special_flags=pygame.BLEND_RGB_SUB)

        return result
    
    def wrap_text(self, text, font, max_width):
        """
        Dzieli długi tekst na linie, aby mieścił się w danej szerokości.
        Zwraca listę linii tekstu.
        """
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            # Sprawdź, czy dodanie nowego słowa przekroczy szerokość
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))  # Ostatnia linia
        return lines

    def update(self,window,mouse_x,mouse_y,click_state,cash):
        """
        Główna funkcja aktualizująca wygląd i logikę sklepu.
        Obsługuje otwieranie/zamykanie, najeżdżanie na strzałki i kliknięcia.
        """
        ret=False  # Wartość zwracana – indeks kupionego żołnierza lub False

        # Sprawdzenie kolizji z prawą i lewą strzałką
        flag = self.colide(self.cxx-430-self.right_arrow_normal.get_width(),
                           self.cyy//2-self.right_arrow_normal.get_height()//2,
                           self.right_arrow_normal.get_width(),
                           self.right_arrow_normal.get_height(),
                           mouse_x,mouse_y)
        
        flag2 = self.colide(self.cxx-self.left_arrow_normal.get_width(),
                            self.cyy//2-self.left_arrow_normal.get_height()//2,
                            self.left_arrow_normal.get_width(),
                            self.left_arrow_normal.get_height(),
                            mouse_x,mouse_y)
        
        # Kliknięcie na prawą/lewą strzałkę zmienia stan sklepu (otwarty/zamknięty)
        if self.shop_state == True and flag == True and click_state:
            self.shop_state = False
        elif self.shop_state == False and flag2 == True and click_state:
            self.shop_state = True
        # Najechanie bez kliknięcia – rozjaśnij przycisk
        elif self.shop_state == True and flag == True and not click_state:
            self.bright_state = True
        elif self.shop_state == False and flag2 == True and not click_state:
            self.bright_state = True
        else:
            self.bright_state = False

        # --- SKLEP OTWARTY ---
        if self.shop_state == True:
            # Wyświetl odpowiednią strzałkę (rozjaśnioną lub normalną)
            if self.bright_state == True:
                window.blit(self.right_arrow_bright,(self.cxx-430-self.right_arrow_normal.get_width(),
                                                     self.cyy//2-self.right_arrow_normal.get_height()//2))
            else:
                window.blit(self.right_arrow_normal,(self.cxx-430-self.right_arrow_normal.get_width(),
                                                     self.cyy//2-self.right_arrow_normal.get_height()//2))

            # Rysowanie białego panelu sklepu
            pygame.draw.rect(window,(255, 255, 255),(self.shop_x_start,0,self.shop_width,self.cyy))
            print(f"Number of soldiers in shop: {len(self.soldier_list)}")
        
            count_sold=0
            # Układ 4x3 (4 wiersze, 3 kolumny)
            for i in range(4):
                for nn in range(3):
                    if  count_sold < len(self.soldier_list):
                        # Dane żołnierza: (obraz, opis, cena)
                        imx = self.soldier_list[count_sold][0].get_width()
                        imy = self.soldier_list[count_sold][0].get_height()
                        
                        # Pozycja obrazu żołnierza w siatce sklepu
                        img_x = int((nn * imy) + self.cxx - (self.cxx / 3) - 30) + 60
                        img_y = int(i * 150)

                        # Sprawdzenie kolizji myszy z danym obrazem
                        col = self.colide(img_x, img_y, imx, imy, mouse_x, mouse_y)
                        if col:
                            # Pozycja kursora względem obrazka
                            rel_x = mouse_x - img_x
                            rel_y = mouse_y - img_y

                            # Sprawdzenie, czy kursor jest na nieprzezroczystym pikselu
                            if 0 <= rel_x < imx and 0 <= rel_y < imy:
                                pixel_alpha = self.soldier_list[count_sold][0].get_at((rel_x, rel_y)).a
                                if pixel_alpha > 0:
                                    # Wyświetlenie opisu
                                    description_text = self.soldier_list[count_sold][1]
                                    wrapped_lines = self.wrap_text(description_text, self.font, self.shop_width - 20)
                                    
                                    text_y_pos = self.cyy - 100  # Pozycja tekstu opisu
                                    for line in wrapped_lines:
                                        text_surface = self.font.render(line, True, (0, 0, 0))
                                        text_rect = text_surface.get_rect(center=(self.shop_x_start + self.shop_width // 2, text_y_pos))
                                        window.blit(text_surface, text_rect)
                                        text_y_pos += self.font.get_height() + 2

                                    # Wyświetlenie ceny
                                    price_text = f"Cost: ${self.soldier_list[count_sold][2]}" 
                                    price_surface = self.font.render(price_text, True, (0, 0, 0))
                                    price_rect = price_surface.get_rect(center=(self.shop_x_start + self.shop_width // 2, text_y_pos + 10))
                                    window.blit(price_surface, price_rect)

                                    # Kliknięcie na żołnierza → zwróć jego indeks
                                    if click_state:
                                        ret = count_sold
                        # Narysuj obraz żołnierza
                        window.blit(self.soldier_list[count_sold][0],
                                    ((nn*imy)+self.cxx-(self.cxx/3)-30+60,i*150))
                        count_sold+=1
        
        # --- SKLEP ZAMKNIĘTY ---
        elif self.shop_state == False:
            # Wyświetl lewą strzałkę (rozjaśnioną lub normalną)
            if self.bright_state == True:
                window.blit(self.left_arrow_bright,(self.cxx-self.left_arrow_normal.get_width(),
                                                    self.cyy//2-self.left_arrow_normal.get_height()//2))
            else:
                window.blit(self.left_arrow_normal,(self.cxx-self.left_arrow_normal.get_width(),
                                                    self.cyy//2-self.left_arrow_normal.get_height()//2))

        # Debug – pokazuje, czy coś zostało kupione
        print("ret:",ret)
        return ret