import random


class Fret:
    def __init__(self, x, y, radius, guitar_string):
        self.x = x;
        self.y = y
        self.radius = radius
        self.guitar_string = guitar_string

    def update_x(self):
        self.x -= 3

    def reset(self, screen_width, screen_height):
        self.x = screen_width + random.randrange(16, 100, 2)
        self.y = screen_height - (self.guitar_string * (self.radius * 2))  # we use guitar_string value to calc y pos
