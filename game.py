"""
Главный файл игры с классами объектов и основной логикой.

Содержит классы для игровых объектов (корабль, пули, метеориты)
и управление игровым процессом.
"""

import pygame
import sys
from random import randint
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position):
        """
        Инициализирует игровой объект.

        Args:
            position: Кортеж (x, y) с начальной позицией объекта
        """
        self.position = position

    def move(self):
        """Обновляет позицию объекта."""
        pass

    def draw(self, screen):
        """Отрисовывает объект на экране."""
        pass

    def get_rect(self):
        """Возвращает прямоугольник объекта для проверки столкновений."""
        pass


class Starship(GameObject):
    """Класс игрового корабля."""

    def __init__(self):
        """Инициализирует корабль игрока."""
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
        """Обновляет позицию корабля и обрабатывает управление."""
        if not self.alive:
            return

        # Получаем состояние клавиш КАЖДЫЙ кадр
        keys = pygame.key.get_pressed()

        # Создаем новую позицию
        x, y = self.position

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:  # D - вправо
            x += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  # A - влево
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
        """Производит выстрел из двух пушек корабля."""
        if not self.alive:
            return

        # Проверяем перезарядку
        if self.shoot_cooldown == 0:
            # Позиции двух пушек (слева и справа от корабля)
            ship_width = self.starship.get_width()

            # Левая пушка (смещение от левого края корабля)
            left_gun_x = self.position[0] + ship_width * 0.2
            left_gun_y = self.position[1]

            # Правая пушка (смещение от правого края корабля)
            right_gun_x = self.position[0] + ship_width * 0.8
            right_gun_y = self.position[1] + 20

            # Создаем две пули
            self.bullets.append(Bullet((left_gun_x, left_gun_y)))
            self.bullets.append(Bullet((right_gun_x, right_gun_y)))

            # Устанавливаем перезарядку
            self.shoot_cooldown = self.shoot_delay

    def draw(self, screen):
        """
        Отрисовывает корабль и все его пули.

        Args:
            screen: Поверхность для отрисовки
        """
        if self.alive:
            screen.blit(self.starship, self.position)
        # Рисуем все пули
        for bullet in self.bullets:
            bullet.draw(screen)

    def get_rect(self):
        """
        Возвращает прямоугольник корабля для проверки столкновений.

        Returns:
            pygame.Rect: Прямоугольник, описывающий границы корабля
        """
        return pygame.Rect(
            self.position[0],
            self.position[1],
            self.starship.get_width(),
            self.starship.get_height(),
        )

    def die(self):
        """Вызывается при столкновении с метеоритом."""
        self.alive = False


class Bullet(GameObject):
    """Класс пули, выпускаемой кораблем."""

    def __init__(self, position):
        """
        Инициализирует пулю.

        Args:
            position: Кортеж (x, y) с начальной позицией пули
        """
        super().__init__(position)
        self.speed = 10
        self.width = 5
        self.height = 18
        self.color = (255, 255, 0)  # желтый цвет для пуль

    def move(self):
        """Двигает пулю вверх по экрану."""
        x, y = self.position
        y -= self.speed  # пули летят вверх
        self.position = (x, y)

    def draw(self, screen):
        """
        Отрисовывает пулю на экране.

        Args:
            screen: Поверхность для отрисовки
        """
        pygame.draw.rect(
            screen,
            self.color,
            (self.position[0], self.position[1], self.width, self.height),
        )

    def is_off_screen(self):
        """
        Проверяет, вышла ли пуля за границы экрана.

        Returns:
            bool: True если пуля вышла за верхнюю границу экрана
        """
        return self.position[1] < 0

    def get_rect(self):
        """
        Возвращает прямоугольник пули для проверки столкновений.

        Returns:
            pygame.Rect: Прямоугольник, описывающий границы пули
        """
        return pygame.Rect(
            self.position[0], self.position[1], self.width, self.height)


class Meteorite(GameObject):
    """Класс метеорита, падающего на корабль."""

    def __init__(self):
        """Инициализирует метеорит со случайной позицией и скоростью."""
        # Загружаем изображение и сохраняем в атрибут
        self.meteorite = pygame.image.load(
            "images/meteorite.png").convert_alpha()

        # Случайная позиция в верхней части экрана
        x = randint(0, SCREEN_WIDTH - self.meteorite.get_width())
        y = -self.meteorite.get_height()

        super().__init__((x, y))
        self.speed = randint(2, 5)  # случайная скорость
        self.alive = True  # статус жизни метеорита

    def move(self):
        """Двигает метеорит вниз по экрану."""
        if not self.alive:
            return

        x, y = self.position
        y += self.speed  # метеориты падают вниз
        self.position = (x, y)

    def is_off_screen(self):
        """
        Проверяет, ушел ли метеорит за границы экрана.

        Returns:
            bool: True если метеорит ушел за нижнюю границу экрана
        """
        return self.position[1] > SCREEN_HEIGHT

    def draw(self, screen):
        """
        Отрисовывает метеорит на экране.

        Args:
            screen: Поверхность для отрисовки
        """
        if self.alive:
            screen.blit(self.meteorite, self.position)

    def get_rect(self):
        """
        Возвращает прямоугольник метеорита для проверки столкновений.

        Returns:
            pygame.Rect: Прямоугольник, описывающий границы метеорита
        """
        return pygame.Rect(
            self.position[0],
            self.position[1],
            self.meteorite.get_width(),
            self.meteorite.get_height(),
        )

    def destroy(self):
        """Вызывается при попадании пули."""
        self.alive = False


class GameManager:
    """Класс для управления игровым процессом и отрисовкой."""

    def __init__(self):
        """Инициализирует игровой менеджер и создает игровое окно."""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Starship")

        self.icon = pygame.image.load("images/starship.png")
        pygame.display.set_icon(self.icon)

        self.bg = pygame.image.load("images/bg.jpg").convert()
        self.bg = pygame.transform.scale(
            self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.bg_y = 0
        self.font = pygame.font.Font(None, 36)  # шрифт для текста
        self.score = 0  # счет игрока

    def draw(self):
        """Отрисовывает фон игры с эффектом прокрутки."""
        # Рисуем фон
        self.bg_y -= 3
        if self.bg_y <= -SCREEN_HEIGHT:
            self.bg_y = 0

        self.screen.blit(self.bg, (0, self.bg_y))
        self.screen.blit(self.bg, (0, self.bg_y + SCREEN_HEIGHT))

    def draw_score(self):
        """Отрисовывает счет поверх всех объектов в правом верхнем углу."""
        score_text = self.font.render(
            f"Очки: {self.score}", True, (255, 255, 255))
        # Позиционируем счет в правом верхнем углу
        score_rect = score_text.get_rect()
        score_rect.right = SCREEN_WIDTH - 10
        score_rect.top = 10
        self.screen.blit(score_text, score_rect)

    def check_collisions(self, starship, meteorites):
        """
        Проверяет столкновения между пулями, метеоритами и кораблем.

        Args:
            starship: Объект корабля игрока
            meteorites: Список активных метеоритов

        Returns:
            bool: True если игра должна завершиться (столкновение корабля)
        """
        # Проверяем столкновения пуль с метеоритами
        for bullet in starship.bullets[:]:
            for meteorite in meteorites[:]:
                if (
                    bullet.get_rect().colliderect(meteorite.get_rect())
                    and meteorite.alive
                ):
                    # Уничтожаем метеорит и пулю
                    meteorite.destroy()
                    starship.bullets.remove(bullet)
                    self.score += 10  # увеличиваем счет
                    break

        # Проверяем столкновения корабля с метеоритами
        if starship.alive:
            for meteorite in meteorites[:]:
                if (
                    starship.get_rect().colliderect(meteorite.get_rect())
                    and meteorite.alive
                ):
                    starship.die()
                    return True  # игра окончена

        return False  # игра продолжается

    def show_game_over(self):
        """Показывает экран завершения игры с итоговым счетом."""
        game_over_text = self.font.render("Поражение!", True, (255, 0, 0))
        score_text = self.font.render(
            f"Набрано очков: {self.score}", True, (255, 255, 255)
        )
        restart_text = self.font.render(
            "Нажмите R для перезапуска", True, (255, 255, 255)
        )

        self.screen.blit(
            game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50)
        )
        self.screen.blit(
            score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        self.screen.blit(
            restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50)
        )


def main():
    """
    Главная функция игры.

    Инициализирует pygame, создает игровые объекты и запускает главный цикл.
    """
    pygame.init()
    game = GameManager()
    starship = Starship()
    meteorites = []  # список метеоритов вместо одного
    meteorite_timer = 0
    game_over = False

    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
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
            if meteorite_timer >= 30:  # каждую секунду (60 кадров)
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

        game.draw_score()

        if game_over:
            game.show_game_over()

        clock.tick(60)
        pygame.display.update()


if __name__ == "__main__":
    main()
