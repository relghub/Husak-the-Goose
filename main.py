import random
import pygame
import pickle
from pygame.constants import QUIT, K_DOWN, K_UP, K_RIGHT, K_LEFT
from os import listdir

pygame.init()

FPS = pygame.time.Clock()

screen = width, height = 1280, 720

BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0

font = pygame.font.Font('.\Roboto-Medium.ttf', 30)

main_surface = pygame.display.set_mode(screen)

IMGS_PATH = "goose"

player_imgs = [pygame.image.load(IMGS_PATH + '/' + file).convert_alpha() for file in listdir(IMGS_PATH)]
player = player_imgs[0]
player_rect = player.get_rect()
player_speed = 7


def create_enemy():
    enemy = pygame.image.load('enemy.png').convert_alpha()
    enemy_rect = pygame.Rect(width, random.randint(0, height - 72), *enemy.get_size())
    enemy_speed = random.randint(5, 12)
    return [enemy, enemy_rect, enemy_speed]


def create_bonus():
    bonus = pygame.image.load('bonus.png').convert_alpha()
    bonus_rect = pygame.Rect(random.randint(0, width - 179), -298, *bonus.get_size())
    bonus_speed = random.randint(3, 5)
    return [bonus, bonus_rect, bonus_speed]


try:
    with open("highscore.pkl", "rb") as f:
        highscore = pickle.load(f)
except FileNotFoundError:
    highscore = 0


def game_over(scores):
    global highscore

    game_over_font = pygame.font.Font('.\Roboto-Bold.ttf', 50)
    game_over_text = game_over_font.render("Кінець гри", True, RED)
    score_text = font.render(f"Набрано очок: {scores}", True, BLACK)
    highscore_text = font.render(f"Рекорд: {highscore}", True, BLACK)

    if scores > highscore:
        highscore = scores
        with open("highscore.pkl", "wb") as f:
            pickle.dump(highscore, f)

    # Вікно завершення гри
    game_over_rect = pygame.Rect(width // 3.4, height // 4, width // 2.4, height // 2)
    pygame.draw.rect(main_surface, WHITE, game_over_rect)
    main_surface.blit(game_over_text, game_over_text.get_rect(center=(width // 2, height // 3)))
    main_surface.blit(score_text, (width // 2 - 100, height // 2 - 40))
    main_surface.blit(highscore_text, (width // 2 - 100, height // 2))

    # Кнопка "Грати"
    restart_button_rect = pygame.Rect(width // 2 + 50, height // 2 + 100, width // 8.5, height // 14.4)
    pygame.draw.rect(main_surface, GREEN, restart_button_rect)
    restart_text = font.render("Грати", True, WHITE)
    restart_text_rect = restart_text.get_rect()
    restart_text_rect.center = restart_button_rect.center
    main_surface.blit(restart_text, restart_text_rect)

    # Кнопка "Вийти"
    quit_button_rect = pygame.Rect(width // 2 - 200, height // 2 + 100, width // 8.5, height // 14.4)
    pygame.draw.rect(main_surface, RED, quit_button_rect)
    quit_text = font.render("Вийти", True, WHITE)
    quit_text_rect = quit_text.get_rect()
    quit_text_rect.center = quit_button_rect.center
    main_surface.blit(quit_text, quit_text_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_pos):
                    return True
                elif quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()


CREATE_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ENEMY, 2500)

CREATE_BONUS = pygame.USEREVENT + 2
pygame.time.set_timer(CREATE_BONUS, 3500)

CHANGE_IMG = pygame.USEREVENT + 3
pygame.time.set_timer(CHANGE_IMG, 125)

bg = pygame.transform.scale(pygame.image.load('background.png').convert(), screen)

bgX = 0

bgX2 = bg.get_width()

bg_speed = 3

img_index = 0

scores = 0

enemies = []

bonuses = []

is_working = True


while is_working:

    FPS.tick(60)

    for event in pygame.event.get():
        if event.type == QUIT:
            is_working = False

        if event.type == CREATE_ENEMY:
            enemies.append(create_enemy())

        if event.type == CREATE_BONUS:
            bonuses.append(create_bonus())

        if event.type == CHANGE_IMG:
            img_index += 1
            if img_index == len(player_imgs):
                img_index = 0
            player = player_imgs[img_index]

    pressed_keys = pygame.key.get_pressed()

    bgX -= bg_speed
    bgX2 -= bg_speed

    if bgX < -bg.get_width():
        bgX = bg.get_width()

    if bgX2 < -bg.get_width():
        bgX2 = bg.get_width()

    main_surface.blit(bg, (bgX, 0))

    main_surface.blit(bg, (bgX2, 0))

    main_surface.blit(player, player_rect)

    main_surface.blit(font.render(str(scores), True, RED), (width - 50, 0))

    for enemy in enemies:
        enemy[1] = enemy[1].move(-enemy[2], 0)
        main_surface.blit(enemy[0], enemy[1])

        if enemy[1].left < -205:
            enemies.pop(enemies.index(enemy))

        if player_rect.colliderect(enemy[1]):
            is_working = game_over(scores)
            if is_working:
                player_rect = player.get_rect()
                scores = 0
                enemies.clear()
                bonuses.clear()

    for bonus in bonuses:
        bonus[1] = bonus[1].move(0, bonus[2])
        main_surface.blit(bonus[0], bonus[1])

        if bonus[1].bottom > height + 298:
            bonuses.pop(bonuses.index(bonus))

        if player_rect.colliderect(bonus[1]):
            bonuses.pop(bonuses.index(bonus))
            scores += 1

    if pressed_keys[K_DOWN] and not player_rect.bottom >= height:
        player_rect = player_rect.move(0, player_speed)

    if pressed_keys[K_UP] and not player_rect.top <= 0:
        player_rect = player_rect.move(0, -player_speed)

    if pressed_keys[K_RIGHT] and not player_rect.right >= width:
        player_rect = player_rect.move(player_speed, 0)

    if pressed_keys[K_LEFT] and not player_rect.left <= 0:
        player_rect = player_rect.move(-player_speed, 0)

    pygame.display.flip()
