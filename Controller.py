import pygame
from EventManager import *


class Controller(object):
    def __init__(self, event_manager, model):
        self.em = event_manager
        self.em.add_listener(self, "Controller")
        self.model = model
        # pygame.event.set_blocked(pygame.)  # Blocks events from registering
        print("Controller init")

    def notify(self, event):
        if event.name == EV_TICK:
            self.get_input()
        elif event.name == EV_QUIT:
            pass


    def get_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.em.post(QuitEvent())

            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                # down_press = None
                if event.type == pygame.KEYDOWN:
                    down_press = True
                else:
                    down_press = False

                ie = None
                if event.key == pygame.K_w:
                    ie = InputEvent("W", down_press)
                elif event.key == pygame.K_SPACE:
                    ie = InputEvent("SPACE", down_press)
                elif event.key == pygame.K_s:
                    ie = InputEvent("S", down_press)
                elif event.key == pygame.K_a:
                    ie = InputEvent("A", down_press)
                elif event.key == pygame.K_d:
                    ie = InputEvent("D", down_press)

                if ie is not None:
                    self.em.post(ie)

            elif event.type == pygame.MOUSEMOTION:
                self.em.post(MouseMoveEvent(event.pos))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pass
                elif event.button == 3:  # Right click
                    self.em.post(MouseClickEvent(event.pos, 3))
