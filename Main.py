
import os
import random
import math
import wave
import struct

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex


class SnakeGame(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.state = "menu"
        self.score = 0
        self.best = 0

        self.cols = 18
        self.snake = []
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = (10, 9)

        self.timer = None
        self.eat_sound = None

        self.bind(size=self.redraw, pos=self.redraw)

    def on_start_game(self):
        try:
            path = os.path.join(
                App.get_running_app().user_data_dir,
                "best.txt"
            )
            if os.path.exists(path):
                with open(path, "r") as f:
                    self.best = int(f.read())
        except:
            self.best = 0

        self.create_sound()
        self.redraw()

    def create_sound(self):
        try:
            path = os.path.join(
                App.get_running_app().user_data_dir,
                "eat.wav"
            )

            if not os.path.exists(path):
                with wave.open(path, "w") as f:
                    f.setparams(
                        (1, 2, 22050, 0, "NONE", "not compressed")
                    )

                    samples = []
                    for i in range(2205):
                        t = i / 22050
                        value = int(
                            10000 *
                            math.sin(2 * math.pi * 700 * t) *
                            (1 - t / 0.1)
                        )
                        samples.append(struct.pack("<h", value))

                    f.writeframes(b"".join(samples))

            self.eat_sound = SoundLoader.load(path)

        except:
            self.eat_sound = None

    def save_best(self):
        try:
            path = os.path.join(
                App.get_running_app().user_data_dir,
                "best.txt"
            )
            with open(path, "w") as f:
                f.write(str(self.best))
        except:
            pass

    def new_game(self):
        self.score = 0

        self.snake = [
            (5, 9),
            (4, 9),
            (3, 9)
        ]

        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.spawn_food()
        self.state = "playing"

        if self.timer:
            self.timer.cancel()

        self.timer = Clock.schedule_interval(
            self.update_game, 0.14
        )

        self.redraw()

    def spawn_food(self):
        while True:
            food = (
                random.randint(0, self.cols - 1),
                random.randint(0, self.cols - 1)
            )

            if food not in self.snake:
                self.food = food
                break

    def update_game(self, dt):
        self.direction = self.next_direction

        hx, hy = self.snake[0]
        dx, dy = self.direction

        new_head = (hx + dx, hy + dy)

        if (
            new_head[0] < 0 or
            new_head[0] >= self.cols or
            new_head[1] < 0 or
            new_head[1] >= self.cols
        ):
            self.game_over()
            return

        eating = new_head == self.food

        body = self.snake if eating else self.snake[:-1]

        if new_head in body:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if eating:
            self.score += 1

            if self.eat_sound:
                try:
                    self.eat_sound.stop()
                    self.eat_sound.play()
                except:
                    pass

            if self.score > self.best:
                self.best = self.score
                self.save_best()

            self.spawn_food()

        else:
            self.snake.pop()

        self.redraw()

    def game_over(self):
        self.state = "over"

        if self.timer:
            self.timer.cancel()
            self.timer = None

        self.redraw()

    def change_direction(self, direction):
        dx, dy = direction
        old_x, old_y = self.direction

        if (dx, dy) != (-old_x, -old_y):
            self.next_direction = (dx, dy)

    def draw_text(self, text, x, y, size, color=(1, 1, 1, 1)):
        label = CoreLabel(
            text=str(text),
            font_size=size,
            color=color
        )

        label.refresh()
        texture = label.texture

        Color(1, 1, 1, 1)

        Rectangle(
            texture=texture,
            pos=(
                x - texture.width / 2,
                y - texture.height / 2
            ),
            size=texture.size
        )

    def draw_button(self, text, x, y, w, h, color):
        Color(*color)
        Rectangle(pos=(x, y), size=(w, h))

        self.draw_text(
            text,
            x + w / 2,
            y + h / 2,
            max(16, int(h * 0.38))
        )

    def redraw(self, *args):
        self.canvas.clear()

        w = self.width
        h = self.height
        ox, oy = self.pos

        with self.canvas:
            Color(*get_color_from_hex("#101522"))
            Rectangle(pos=self.pos, size=self.size)

            if self.state == "menu":

                self.draw_text(
                    "VAAAAAVEN SNAKE",
                    ox + w / 2,
                    oy + h * 0.70,
                    int(w * 0.075),
                    (0.2, 1, 0.4, 1)
                )

                self.draw_text(
                    "BEST: " + str(self.best),
                    ox + w / 2,
                    oy + h * 0.59,
                    22
                )

                self.draw_button(
                    "PLAY",
                    ox + w * 0.22,
                    oy + h * 0.38,
                    w * 0.56,
                    65,
                    (0.1, 0.65, 0.25, 1)
                )

                return

            board_size = min(w * 0.88, h * 0.53)
            cell = board_size / self.cols

            bx = ox + (w - board_size) / 2
            by = oy + h * 0.30

            self.draw_text(
                "SCORE: " + str(self.score),
                ox + w * 0.28,
                oy + h * 0.91,
                21
            )

            self.draw_text(
                "BEST: " + str(self.best),
                ox + w * 0.73,
                oy + h * 0.91,
                21
            )

            Color(*get_color_from_hex("#1B2638"))
            Rectangle(
                pos=(bx, by),
                size=(board_size, board_size)
            )

            Color(0.25, 0.32, 0.4, 0.35)

            for i in range(self.cols + 1):
                Line(
                    points=[
                        bx + i * cell, by,
                        bx + i * cell, by + board_size
                    ],
                    width=0.5
                )

                Line(
                    points=[
                        bx, by + i * cell,
                        bx + board_size, by + i * cell
                    ],
                    width=0.5
                )

            fx, fy = self.food

            Color(1, 0.15, 0.18, 1)

            Ellipse(
                pos=(
                    bx + fx * cell + cell * 0.12,
                    by + fy * cell + cell * 0.12
                ),
                size=(cell * 0.76, cell * 0.76)
            )

            for index, (sx, sy) in enumerate(self.snake):

                if index == 0:
                    Color(0.25, 1, 0.35, 1)
                else:
                    Color(0.05, 0.75, 0.22, 1)

                Rectangle(
                    pos=(
                        bx + sx * cell + 1,
                        by + sy * cell + 1
                    ),
                    size=(cell - 2, cell - 2)
                )

            # UP
            self.draw_button(
                "UP",
                ox + w * 0.39,
                oy + h * 0.15,
                w * 0.22,
                42,
                (0.17, 0.25, 0.38, 1)
            )

            # LEFT
            self.draw_button(
                "LEFT",
                ox + w * 0.14,
                oy + h * 0.075,
                w * 0.22,
                42,
                (0.17, 0.25, 0.38, 1)
            )

            # DOWN
            self.draw_button(
                "DOWN",
                ox + w * 0.39,
                oy + h * 0.075,
                w * 0.22,
                42,
                (0.17, 0.25, 0.38, 1)
            )

            # RIGHT
            self.draw_button(
                "RIGHT",
                ox + w * 0.64,
                oy + h * 0.075,
                w * 0.22,
                42,
                (0.17, 0.25, 0.38, 1)
            )

            if self.state == "over":

                Color(0, 0, 0, 0.75)

                Rectangle(
                    pos=(bx, by),
                    size=(board_size, board_size)
                )

                self.draw_text(
                    "GAME OVER",
                    ox + w / 2,
                    by + board_size * 0.60,
                    30,
                    (1, 0.3, 0.3, 1)
                )

                self.draw_button(
                    "RESTART",
                    ox + w * 0.22,
                    by + board_size * 0.35,
                    w * 0.56,
                    55,
                    (0.1, 0.65, 0.25, 1)
                )

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        x, y = touch.pos
        w, h = self.size
        ox, oy = self.pos

        rx = x - ox
        ry = y - oy

        if self.state == "menu":
            if h * 0.35 < ry < h * 0.48:
                self.new_game()
            return True

        if self.state == "over":
            self.new_game()
            return True

        # UP button
        if (
            w * 0.39 < rx < w * 0.61 and
            h * 0.15 < ry < h * 0.15 + 42
        ):
            self.change_direction((0, 1))
            return True

        # LEFT button
        if (
            w * 0.14 < rx < w * 0.36 and
            h * 0.075 < ry < h * 0.075 + 42
        ):
            self.change_direction((-1, 0))
            return True

        # DOWN button
        if (
            w * 0.39 < rx < w * 0.61 and
            h * 0.075 < ry < h * 0.075 + 42
        ):
            self.change_direction((0, -1))
            return True

        # RIGHT button
        if (
            w * 0.64 < rx < w * 0.86 and
            h * 0.075 < ry < h * 0.075 + 42
        ):
            self.change_direction((1, 0))
            return True

        return True


class VaaaavenApp(App):

    def build(self):
        self.title = "VAAAAAVEN SNAKE"
        self.game = SnakeGame()
        return self.game

    def on_start(self):
        self.game.on_start_game()


if __name__ == "__main__":
    VaaaavenApp().run()
