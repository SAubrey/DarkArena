import pygame
import os
import pymunk.pygame_util
from EventManager import *
import TailPoint
from Player import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 50


class Renderer(object):
    def __init__(self, event_manager, game_engine, screen_dim):
        self.em = event_manager
        self.screen_dim = Vec2d(screen_dim)
        self.em.add_listener(self, "Renderer")

        self.ge = game_engine
        self.initialized = False
        self.screen = None
        self.clock = None

        self.background = None
        self.draw_options = None
        self.all_sprites = None
        self.dirty_rects = []  #
        self.tail_sprites = []  # To hold rect & color data
        self.tail_rects = []  # To be rendered
        self.old_rects = []  # To be replaced with background
        self.tail_skip_counter = 0
        self.tail_skip_thresh = 1
        self.new_player_pos = Vec2d((int(max(10, self.screen_dim.x / 3))), int(max(10, self.screen_dim.y / 3)))
        self.last_player_pos = self.new_player_pos

        self.player_health = 100
        self.max_player_health = 100
        self.player_stamina = 100
        self.player_mana = 100
        r = (0, 0, 0, 0)
        self.stat_rects = {"health": r, "stamina": r, "mana": r}
        self.blit_stat_rects = {"health": r, "stamina": r, "mana": r}

        # Pymunk
        self.space = None

    def initialize(self):
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.screen = pygame.display.set_mode(self.screen_dim)
        pygame.display.set_caption("Incessance")
        self.background = pygame.image.load(os.path.join("3dgrid.jpg")).convert()
        self.background = pygame.transform.scale(self.background,
                                                 (self.screen_dim.x,
                                                  self.screen_dim.y))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        pygame.mouse.set_visible(1)
        self.initialized = True
        print("Renderer init")

    def notify(self, event):
        if event.name == EV_TICK:
            self.clock.tick(FPS)
            self.render()
        elif event.name == EV_PLAYER_MOVE:
            p = (Vec2d(event.position))
            self.last_player_pos = self.new_player_pos
            self.new_player_pos = p
        elif event.name == EV_PLAYER_STATS:
            self.player_health = event.health
            self.player_stamina = event.stamina
            self.player_mana = event.mana
        elif event.name == EV_RESIZE:
            self.screen_dim = event.screen_dim
        elif event.name == EV_INIT:
            self.initialize()
        elif event.name == EV_MODEL_SHARE:
            self.space = event.space
            self.all_sprites = event.all_sprites
            self.all_sprites.clear(self.screen, self.background)  # Replace old w/ background
        elif event.name == EV_QUIT:
            self.initialized = False
            pygame.quit()

    # Blit the background over THEN draw images
    def render(self):
        if not self.initialized:
            print("missed init in renderer")
            return

        self.draw_sprites()
        self.draw_HUD()
        self.screen.blit(self.background, (0, 50, 130, 30), (0, 50, 130, 30))
        self.screen.blit(self.font.render("fps: " + str(self.clock.get_fps()), 1, WHITE), (0, 50))
        all_rects = self.dirty_rects + self.tail_rects + self.stat_rects.values() + self.blit_stat_rects.values()
        pygame.display.update(all_rects)
        pygame.display.update((0, 50, 130, 30))
        #pygame.display.flip()  # Update entire screen
        self.space.debug_draw(self.draw_options)

    def draw_sprites(self):
        self.dirty_rects = self.all_sprites.draw(self.screen)  # Gets list of rects from sprites

        # Clear and re-fill tail Rects (updates color)
        del self.tail_rects[:]
        for s in self.tail_sprites:
            s.update()
            pos = s.get_rect().x + s.get_radius(), s.get_rect().y + s.get_radius()
            self.tail_rects.append(pygame.draw.circle(self.screen, s.get_color(), pos, s.get_radius(), 0))
            #self.tail_rects.append(pygame.draw.rect(self.screen, s.get_color(), s.get_rect()))
        self.draw_player_tail()

        # Replace old tail pixels with background
        for a in self.old_rects:
            self.screen.blit(self.background, a, a)
        del self.old_rects[:]

    def draw_player_tail(self):
        self.tail_skip_counter += 1
        if self.tail_skip_counter >= self.tail_skip_thresh:
            self.draw_line_between(self.last_player_pos, self.new_player_pos, 10)
            self.tail_skip_counter = 0

    def draw_line_between(self, p1, p2, width):
        color = (0, 0, 255)

        dx = int(p1[0] - p2[0])
        dy = int(p1[1] - p2[1])
        iterations = max(abs(dx), abs(dy))

        for i in range(iterations):
            progress = 1.0 * i / iterations
            aprogress = 1 - progress
            x = int(aprogress * p1[0] + progress * p2[0])
            y = int(aprogress * p1[1] + progress * p2[1])
            if i % 2 == 0:
                tp = TailPoint.TailPoint(self, color, width, (x, y))
                self.tail_sprites.append(tp)

    def draw_HUD(self):
        for rect in self.blit_stat_rects.values():
            self.screen.blit(self.background, rect, rect)

        height = 10
        c = 20

        h_x = self.calc_stat_x(self.player_health, MAX_HEALTH)
        h_rect = (0, 0, h_x, height)
        pygame.draw.rect(self.screen, (145, c, c), h_rect)

        s_x = self.calc_stat_x(self.player_stamina, MAX_STAMINA)
        s_rect = (0, height + 5, s_x, height)
        pygame.draw.rect(self.screen, (c, 125, c), s_rect)

        m_x = self.calc_stat_x(self.player_mana, MAX_MANA)
        m_rect = pygame.Rect(0, 2 * (height + 5), m_x, height)
        pygame.draw.rect(self.screen, (c, c, 125), m_rect)

        self.stat_rects["health"] = h_rect
        self.stat_rects["stamina"] = s_rect
        self.stat_rects["mana"] = m_rect

        # Rects to re-draw background over begin at current stat bar levels (zero if full)
        health_blit_rect = (h_x, 0, self.calc_stat_x(MAX_HEALTH, MAX_HEALTH), height)
        stamina_blit_rect = (s_x, height + 5, self.calc_stat_x(MAX_STAMINA, MAX_STAMINA), height)
        mana_blit_rect = (m_x, 2 * (height + 5), self.calc_stat_x(MAX_MANA, MAX_MANA), height)

        self.blit_stat_rects["health"] = health_blit_rect
        self.blit_stat_rects["stamina"] = stamina_blit_rect
        self.blit_stat_rects["mana"] = mana_blit_rect

    def calc_stat_x(self, n, max_n):
        return int((n * (self.screen_dim.x / max(max_n, 1)))/4)

    def remove_tailpoint(self, tp):
        self.old_rects.append(tp.get_rect())
        self.tail_sprites.remove(tp)

    def to_pygame_coordinates(self, vector):
        return int(vector.x), int(-vector.y + self.screen_dim.y)
