"""Главный файл игры с классами объектов и основной логикой."""

import pygame
import sys
from random import randint

SCREEN_HEIGHT = 950
SCREEN_WIDTH = 713

clock = pygame.time.Clock()


class GameObject:
    body_color = None

    def __init__(self, position):
        self.position = position

    def move(self):
        pass

    def draw(self, screen):
        pass

    def get_rect(self):
        """Возвращает прямоугольник объекта для проверки столкновений"""
        pass


class Bullet(GameObject):
    def __init__(self, position):
        super().__init__(position)
        self.speed = 10
        self.width = 3
        self.height = 15
        self.color = (255, 255, 0)  # желтый цвет для пуль

    def move(self):
        x, y = self.position
        y -= self.speed  # пули летят вверх
        self.position = (x, y)

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (self.position[0], self.position[1], self.width, self.height),
        )

    def is_off_screen(self):
        return self.position[1] < 0

    def get_rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.width, self.height)


class Starship(GameObject):
    def __init__(self):
        starship_img = pygame.image.load("images/starship.png").convert_alpha()
        starship_width = starship_img.get_width()
        starship_height = starship_img.get_height()

        x = (SCREEN_WIDTH - starship_width) // 2
        y = SCREEN_HEIGHT - starship_height - 10

        super().__init__((x, y))
        self.starship = starship_img
        self.speed = 5  # скорость движения
        self.bullets = []  # список пуль
        self.shoot_cooldown = 0  # перезарядка между выстрелами
        self.shoot_delay = 15  # задержка между выстрелами (в кадрах)
        self.alive = True  # статус жизни игрока

    def move(self):
        if not self.alive:
            return
            
        # Получаем состояние клавиш КАЖДЫЙ кадр
        keys = pygame.key.get_pressed()

        # Создаем новую позицию
        x, y = self.position

        if keys[pygame.K_d]:  # D - вправо
            x += self.speed
        if keys[pygame.K_a]:  # A - влево
            x -= self.speed

        # Ограничиваем движение в пределах экрана
        x = max(0, min(x, SCREEN_WIDTH - self.starship.get_width()))

        self.position = (x, y)

        # Обновляем перезарядку
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Двигаем все пули
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)

    def shoot(self):
        if not self.alive:
            return
            
        # Проверяем перезарядку
        if self.shoot_cooldown == 0:
            # Позиции двух пушек (слева и справа от корабля)
            ship_width = self.starship.get_width()
            ship_height = self.starship.get_height()

            # Левая пушка (смещение от левого края корабля)
            left_gun_x = self.position[0] + ship_width * 0.2
            left_gun_y = self.position[1]

            # Правая пушка (смещение от правого края корабля)
            right_gun_x = self.position[0] + ship_width * 0.8
            right_gun_y = self.position[1]

            # Создаем две пули
            self.bullets.append(Bullet((left_gun_x, left_gun_y)))
            self.bullets.append(Bullet((right_gun_x, right_gun_y)))

            # Устанавливаем перезарядку
            self.shoot_cooldown = self.shoot_delay

    def draw(self, screen):
        if self.alive:
            screen.blit(self.starship, self.position)
        # Рисуем все пули
        for bullet in self.bullets:
            bullet.draw(screen)

    def get_rect(self):
        return pygame.Rect(
            self.position[0], 
            self.position[1], 
            self.starship.get_width(), 
            self.starship.get_height()
        )

    def die(self):
        """Вызывается при столкновении с метеоритом"""
        self.alive = False


class Meteorite(GameObject):
    def __init__(self):
        # Загружаем изображение и сохраняем в атрибут
        self.meteorite = pygame.image.load("images/starship.png").convert_alpha()

        # Случайная позиция в верхней части экрана
        x = randint(0, SCREEN_WIDTH - self.meteorite.get_width())
        y = -self.meteorite.get_height()

        super().__init__((x, y))
        self.speed = randint(2, 5)  # случайная скорость
        self.alive = True  # статус жизни метеорита

    def move(self):
        if not self.alive:
            return
            
        x, y = self.position
        y += self.speed  # метеориты падают вниз
        self.position = (x, y)

    def is_off_screen(self):
        return self.position[1] > SCREEN_HEIGHT

    def draw(self, screen):
        if self.alive:
            screen.blit(self.meteorite, self.position)

    def get_rect(self):
        return pygame.Rect(
            self.position[0], 
            self.position[1], 
            self.meteorite.get_width(), 
            self.meteorite.get_height()
        )

    def destroy(self):
        """Вызывается при попадании пули"""
        self.alive = False


class GameManager:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Starship")

        self.bg = pygame.image.load("images/bg.jpg").convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.bg_y = 0
        self.font = pygame.font.Font(None, 36)  # шрифт для текста
        self.score = 0  # счет игрока

    def draw(self):
        # Очищаем экран
        self.screen.fill((0, 0, 0))

        # Рисуем фон
        self.bg_y -= 3
        if self.bg_y <= -SCREEN_HEIGHT:
            self.bg_y = 0

        self.screen.blit(self.bg, (0, self.bg_y))
        self.screen.blit(self.bg, (0, self.bg_y + SCREEN_HEIGHT))

        # Рисуем счет
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def check_collisions(self, starship, meteorites):
        """Проверяет столкновения между пулями, метеоритами и кораблем"""
        
        # Проверяем столкновения пуль с метеоритами
        for bullet in starship.bullets[:]:
            for meteorite in meteorites[:]:
                if (bullet.get_rect().colliderect(meteorite.get_rect()) 
                    and meteorite.alive):
                    # Уничтожаем метеорит и пулю
                    meteorite.destroy()
                    starship.bullets.remove(bullet)
                    self.score += 10  # увеличиваем счет
                    break

        # Проверяем столкновения корабля с метеоритами
        if starship.alive:
            for meteorite in meteorites[:]:
                if (starship.get_rect().colliderect(meteorite.get_rect()) 
                    and meteorite.alive):
                    starship.die()
                    return True  # игра окончена
                    
        return False  # игра продолжается

    def show_game_over(self):
        """Показывает экран завершения игры"""
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50))


def main():
    pygame.init()
    game = GameManager()
    starship = Starship()
    meteorites = []  # список метеоритов вместо одного
    meteorite_timer = 0
    game_over = False

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    starship.shoot()
                elif event.key == pygame.K_r and game_over:
                    # Рестарт игры
                    starship = Starship()
                    meteorites = []
                    meteorite_timer = 0
                    game.score = 0
                    game_over = False

        if not game_over:
            # Создание новых метеоритов
            meteorite_timer += 1
            if meteorite_timer >= 60:  # каждую секунду (60 кадров)
                meteorites.append(Meteorite())
                meteorite_timer = 0

            # Обновление позиций
            starship.move()

            # Двигаем метеориты и удаляем те, что ушли за экран или уничтожены
            for meteorite in meteorites[:]:
                meteorite.move()
                if meteorite.is_off_screen() or not meteorite.alive:
                    meteorites.remove(meteorite)

            # Проверяем столкновения
            game_over = game.check_collisions(starship, meteorites)

        # Отрисовка
        game.draw()
        starship.draw(game.screen)
        for meteorite in meteorites:
            meteorite.draw(game.screen)
            
        if game_over:
            game.show_game_over()

        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()