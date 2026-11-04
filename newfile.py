
import pygame
import random
import os
import math
import wave
import struct
import io

pygame.init()

# Звук
eat_sound = None

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    sample_rate = 22050
    duration = 0.15
    sound_data = io.BytesIO()

    with wave.open(sound_data, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)

        samples = []
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            volume = 1 - t / duration
            value = int(
                10000 * volume * math.sin(2 * math.pi * 880 * t)
            )
            samples.append(struct.pack("<h", value))

        wav.writeframes(b"".join(samples))

    sound_data.seek(0)
    eat_sound = pygame.mixer.Sound(file=sound_data)

except Exception:
    eat_sound = None

W, H = 400, 680
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("VAAAAAVEN SNAKE 2.3")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
big = pygame.font.SysFont(None, 45)

GREEN = (40, 230, 100)
WHITE = (255, 255, 255)
BLUE = (30, 130, 255)
DARK = (15, 20, 35)

# Сохранение рекорда
BEST_FILE = "vavaven_best.txt"

def load_best():
    try:
        with open(BEST_FILE, "r") as file:
            return int(file.read())
    except:
        return 0

def save_best():
    try:
        with open(BEST_FILE, "w") as file:
            file.write(str(best))
    except:
        pass

best = load_best()
score = 0
state = "menu"

play_button = pygame.Rect(100, 330, 200, 65)
restart_button = pygame.Rect(80, 350, 240, 60)
menu_button = pygame.Rect(80, 430, 240, 60)

buttons = {
    "UP": pygame.Rect(155, 510, 90, 45),
    "DOWN": pygame.Rect(155, 610, 90, 45),
    "LEFT": pygame.Rect(55, 560, 90, 45),
    "RIGHT": pygame.Rect(255, 560, 90, 45)
}

def reset_game():
    global snake, direction, food, score, timer

    snake = [(200, 270), (180, 270), (160, 270)]
    direction = (20, 0)
    score = 0
    timer = 0
    food = new_food()

def new_food():
    while True:
        p = (
            random.randrange(0, 400, 20),
            random.randrange(70, 470, 20)
        )
        if p not in snake:
            return p

def draw_button(rect, label, color=BLUE):
    pygame.draw.rect(screen, color, rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=15)

    text = font.render(label, True, WHITE)
    screen.blit(text, text.get_rect(center=rect.center))

def draw_game():
    screen.fill(DARK)

    title = font.render("VAAAAAVEN SNAKE 2.3", True, GREEN)
    screen.blit(title, (15, 20))

    pygame.draw.rect(screen, (25, 35, 55), (0, 70, 400, 400))

    # Сетка
    for x in range(0, 400, 20):
        pygame.draw.line(
            screen, (35, 45, 65),
            (x, 70), (x, 470)
        )

    for y in range(70, 470, 20):
        pygame.draw.line(
            screen, (35, 45, 65),
            (0, y), (400, y)
        )

    pygame.draw.rect(screen, WHITE, (0, 70, 400, 400), 2)

    # Еда
    pygame.draw.circle(
        screen, (255, 70, 70),
        (food[0] + 10, food[1] + 10), 9
    )

    # Змейка
    for i, part in enumerate(snake):
        color = GREEN if i == 0 else (20, 180, 90)

        pygame.draw.rect(
            screen, color,
            (*part, 20, 20),
            border_radius=6
        )

    # Глаза
    hx, hy = snake[0]

    pygame.draw.circle(screen, WHITE, (hx + 14, hy + 6), 2)
    pygame.draw.circle(screen, WHITE, (hx + 14, hy + 14), 2)

    text = font.render("SCORE: " + str(score), True, WHITE)
    screen.blit(text, (10, 475))

    text = font.render("BEST: " + str(best), True, GREEN)
    screen.blit(text, (260, 475))

    for name, rect in buttons.items():
        draw_button(rect, name)

def start_game():
    global state
    reset_game()
    state = "playing"

reset_game()

running = True

while running:
    dt = clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if state == "menu":
                if play_button.collidepoint(pos):
                    start_game()

            elif state == "playing":
                moves = {
                    "UP": (0, -20),
                    "DOWN": (0, 20),
                    "LEFT": (-20, 0),
                    "RIGHT": (20, 0)
                }

                for name, rect in buttons.items():
                    if rect.collidepoint(pos):
                        new_dir = moves[name]

                        if new_dir != (
                            -direction[0], -direction[1]
                        ):
                            direction = new_dir

            elif state == "over":
                if restart_button.collidepoint(pos):
                    start_game()

                elif menu_button.collidepoint(pos):
                    state = "menu"

    if state == "playing":
        timer += dt

        if timer >= 140:
            timer = 0

            head = (
                snake[0][0] + direction[0],
                snake[0][1] + direction[1]
            )

            if (head[0] < 0 or head[0] >= 400 or
                head[1] < 70 or head[1] >= 470):
                state = "over"

            elif head in snake[:-1] and head != food:
                state = "over"

            else:
                snake.insert(0, head)

                if head == food:
                    score += 1

                    if score > best:
                        best = score
                        save_best()

                    if eat_sound:
                        eat_sound.play()

                    food = new_food()

                else:
                    snake.pop()

    if state == "menu":
        screen.fill(DARK)

        title = big.render("VAAAAAVEN", True, GREEN)
        screen.blit(title, (65, 170))

        subtitle = font.render("SNAKE 2.3", True, WHITE)
        screen.blit(subtitle, (135, 230))

        draw_button(play_button, "PLAY", GREEN)

        record = font.render(
            "BEST SCORE: " + str(best), True, WHITE
        )
        screen.blit(record, (105, 430))

    elif state == "playing":
        draw_game()

    elif state == "over":
        draw_game()

        msg = big.render("GAME OVER", True, (255, 220, 0))
        screen.blit(msg, (105, 230))

        draw_button(restart_button, "RESTART", GREEN)
        draw_button(menu_button, "MAIN MENU")

    pygame.display.flip()

pygame.quit()
