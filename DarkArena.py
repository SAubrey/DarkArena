import EventManager
import Renderer
import GameEngine
import Controller
import os
import pygame
from pymunk.vec2d import Vec2d

"""
Created by Sean Aubrey
"""
def start():
    win_offset_y = 25
    os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(win_offset_y)
    pygame.init()
    info_obj = pygame.display.Info()
    #print(info_obj)
    screen_dim = Vec2d(int(info_obj.current_w), int(info_obj.current_h - win_offset_y))

    em = EventManager.EventManager()
    game_engine = GameEngine.GameEngine(em, screen_dim)
    renderer = Renderer.Renderer(em, game_engine, screen_dim)
    controller = Controller.Controller(em, game_engine)

    game_engine.run()


if __name__ == '__main__':
    start()
