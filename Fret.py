import random
import cv2

COLOR_GREEN = (152, 234, 140)

class Fret:

    def __init__(self, radius, string, position):
        self.x = -3000;
        self.y = -3000;
        self.radius = radius
        self.string = string
        self.position = position

    def update_x(self):
        self.x -= 5

    def reset(self, screen_width, screen_height, delay,):
        self.x = screen_width + (self.position * 63) + (delay * 350)
        self.y = screen_height - (self.string * (self.radius * 2)) - 25  # we use guitar_string value to calc y pos


class Fret_Set:
    def __init__(self, fret_type, delay):
        self.fret_type = fret_type
        self.delay = delay
        self.frets = []
        self.create_frets()

    def create_frets(self):
        if self.fret_type == 'g_chord':
            self.frets = [
                Fret( 15, 5, 0),
                Fret( 15, 4, 1),
                Fret( 15, 2, 2),
            ]

        elif self.fret_type == 'c_chord':
            self.frets = [
                Fret( 15, 1, 0),
                Fret( 15, 6, 1),
                Fret( 15, 4, 2),
            ]
        else:
            self.frets = []

    def prep_frets(self, frame):
        for fret in self.frets:
            fret.reset(frame.shape[1], frame.shape[0], self.delay)

    def animate_frets(self, frame):
        for fret in self.frets:
            # only move and print if circle has not moved out of screen
            if fret.x > -fret.radius:
                # update x pos - moves right to left
                fret.update_x()
                cv2.circle(frame, (fret.x, fret.y), fret.radius, COLOR_GREEN, -1)
            # else:
            #     fret.reset(frame.shape[1], frame.shape[0], self.delay)