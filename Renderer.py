import pygame
import os
import pymunk.pygame_util
from EventManager import *
from TailPoint import *
from Player import *
from pymunk.vec2d import Vec2d
import pygame.gfxdraw

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60
EMPTY_RECT = (0, 0, 0, 0)


class Renderer(object):
    def __init__(self, event_manager, game_engine, screen_dim):
        self.em = event_manager
        self.ge = game_engine
        self.screen_dim = Vec2d(screen_dim)
        self.em.add_listener(self, "Renderer")

        self.initialized = False
        self.clock = None
        self.font = None
        self.screen = None
        self.background = None
        self.draw_options = None

        self.all_sprites = None
        self.dirty_rects = []

        self.player_tail_drawer = None
        self.current_player_pos = Vec2d(0, 0)
        self.last_player_pos = self.current_player_pos
        self.player_sword = None
        self.sword_rects, self.old_sword_rects = [], []
        self.enemies = []

        self.player_health = 100
        self.max_player_health = 100
        self.player_stamina = 100
        self.player_mana = 100
        self.stat_rects = {"health": EMPTY_RECT, "stamina": EMPTY_RECT, "mana": EMPTY_RECT}
        self.blit_stat_rects = {"health": EMPTY_RECT, "stamina": EMPTY_RECT, "mana": EMPTY_RECT}
        self.fps_rect = (0, 50, 130, 30)

        # Pymunk
        self.space = None
        #pymunk.pygame_util.positive_y_is_up = False

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

        self.player_tail_drawer = TailDrawer(self)
        pygame.mouse.set_visible(1)
        self.initialized = True
        print("Renderer init")

    def notify(self, event):
        en = event.name
        if en == EV_TICK:
            self.clock.tick(FPS)
            self.render()
        elif en == EV_PLAYER_MOVE:
            p = (Vec2d(event.position))
            self.last_player_pos = self.current_player_pos
            self.current_player_pos = p
        elif en == EV_PLAYER_STATS:
            self.player_health = event.health
            self.player_stamina = event.stamina
            self.player_mana = event.mana
        elif en == EV_RESIZE:
            self.screen_dim = event.screen_dim
        elif en == EV_INIT:
            self.initialize()
        elif en == EV_MODEL_SHARE:
            self.space = event.space
            self.all_sprites = event.all_sprites
            self.all_sprites.clear(self.screen, self.background)  # Replace old w/ background
            self.player_sword = event.player_sword
            self.enemy_swords = event.enemy_swords
        elif en == EV_QUIT:
            self.initialized = False
            pygame.quit()

    # Blit the background over THEN draw images
    # blitted background rects and new draw rects must be included in display.update() list
    def render(self):
        if not self.initialized:
            print("missed init in renderer")
            return
        self.draw_sprites()
        self.draw_HUD()
        self.screen.blit(self.background, self.fps_rect, self.fps_rect)
        self.screen.blit(self.font.render("fps: " + str(self.clock.get_fps()), 1, WHITE), (0, 50))

        all_rects = self.player_tail_drawer.get_tail_rects() + \
                    self.stat_rects.values() + \
                    self.blit_stat_rects.values()
        all_rects.append(self.fps_rect)

        del self.old_sword_rects[:]
        for rect in self.sword_rects:
            self.screen.blit(self.background, rect, rect)
            self.old_sword_rects.append(rect)
        del self.sword_rects[:]
        self.draw_swords()

        all_rects = all_rects + self.dirty_rects + self.sword_rects + self.old_sword_rects

        #self.screen.fill(BLACK)
        pygame.display.update(all_rects)
        #self.space.debug_draw(self.draw_options)
        #pygame.display.flip()  # Update entire screen

    def draw_sprites(self):
        self.dirty_rects = self.all_sprites.draw(self.screen)  # Gets list of rects from sprites
        self.player_tail_drawer.draw(self.last_player_pos, self.current_player_pos)

    def draw_swords(self):
        swords = []
        swords += self.enemy_swords
        swords.append(self.player_sword)
        for sword in swords:
            if sword.renderable:
                self.draw_sword(sword)

    def draw_sword(self, sword):
        adjusted_vertices = self.convert_vertices_to_pygame(sword.get_vertices(), sword.get_angle(), sword.get_position())
        pygame.gfxdraw.aapolygon(self.screen, adjusted_vertices, sword.color)
        self.sword_rects.append(pygame.draw.polygon(self.screen, sword.color, adjusted_vertices, 0))

    def convert_vertices_to_pygame(self, vertices, angle, position):
        newv = []
        for pos in vertices:
            x, y = pos.rotated(angle) + position
            newv.append((int(x), int(y)))
        return newv

    def draw_HUD(self):
        # Clear old image before redrawing
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
        h_width = self.calc_stat_x(MAX_HEALTH - self.player_health, MAX_HEALTH)
        health_blit_rect = (h_x, 0, h_width, height)
        s_width = self.calc_stat_x(MAX_STAMINA - self.player_stamina, MAX_STAMINA)
        stamina_blit_rect = (s_x, height + 5, s_width, height)
        m_width = self.calc_stat_x(MAX_MANA - self.player_mana, MAX_MANA)
        mana_blit_rect = (m_x, 2 * (height + 5), m_width, height)

        self.blit_stat_rects["health"] = health_blit_rect
        self.blit_stat_rects["stamina"] = stamina_blit_rect
        self.blit_stat_rects["mana"] = mana_blit_rect

    def calc_stat_x(self, n, max_n):
        return int((n * (self.screen_dim.x / max(max_n, 1)))/4)

    def to_pygame_coordinates(self, vector):
        return pymunk.pygame_util.to_pygame(vector, self.screen)
        #return int(vector.x), int(-vector.y + self.screen_dim.y)
