import pygame
import Player
import Enemy
import pymunk
from pymunk.vec2d import Vec2d
from EventManager import *

# Game Model
class GameEngine(object):
    def __init__(self, event_manager, screen_dim):
        self.em = event_manager
        self.screen_dim = Vec2d(screen_dim)
        event_manager.add_listener(self, "Game Engine")
        self.running = False

        self.all_sprites = None
        #self.nonplayer_sprites = []
        self.player_collisions = []
        #self.projectile_sprites = []

        self.player = None
        self.initialized = False

        self.space = None # pymunk playfield

    def initialize(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.space.damping = 0.8  # lower = more dampening
        self.all_sprites = pygame.sprite.LayeredDirty()
        #self.nonplayer_sprites = pygame.sprite.LayeredDirty()

        self.add_player()
        for i in range(10):
            self.add_enemy()

       # self.player_collisions = pygame.sprite.spritecollide(self.player,
                                                            # self.nonplayer_sprites,
                                                            # False)
        self.create_borders()
        self.initialized = True
        print("Game Engine init")

    def run(self):
        if not self.initialized:
            self.initialize()
        self.running = True

        self.em.post(InitializeEvent())
        self.em.post(ModelShareEvent(self.space, self.all_sprites))

        while self.running:
            self.em.post(TickEvent())
            self.all_sprites.update()  # calls update for each sprite
            self.space.step(1 / 50.0)

    def notify(self, event):
        if event.name == EV_INPUT:
            self.player.handle_input(event.key, event.down_press)
        elif event.name == EV_MOUSE_MOVE:
            self.player.set_cursor_pos(event.position)
        elif event.name == EV_MOUSE_CLICK:
            self.player.handle_click(event.position, event.button)
        elif event.name == EV_RESIZE:
            self.screen_dim = Vec2d(event.width, event.height)
        elif event.name == EV_QUIT:
            self.running = False

    def add_player(self):
        self.player = Player.Player(self, self.screen_dim)
        self.all_sprites.add(self.player)

    def add_enemy(self):
        enemy = Enemy.Enemy(self, self.screen_dim)
        self.all_sprites.add(enemy)

    def create_borders(self):
        s = pymunk.Body(body_type=pymunk.Body.STATIC)
        width = 5
        x = self.screen_dim.x
        y = self.screen_dim.y
        walls = [pymunk.Segment(s, (0, 0), (x, 0), width),  # floor
                 pymunk.Segment(s, (0, y), (x, y), width),  # ceiling
                 pymunk.Segment(s, (0, y), (0, 0), width),  # left
                 pymunk.Segment(s, (x, y), (x, 0), width)]  # right
        for wall in walls:
            wall.friction = 0.4
        self.space.add(walls)

    def get_all_sprites(self):
        return self.all_sprites

    def add_body(self, body, shape):
        self.space.add(body, shape)

    def add_sprite(self, sprite):
        self.all_sprites.add(sprite)

    def get_space(self):
        return self.space

    def post_player_position(self, position):
        self.em.post(PlayerMoveEvent(position))

    def post_player_update(self, health, stamina, mana):
        self.em.post(PlayerStatUpdate(health, stamina, mana))

    def flip_yaxis(self, vector):
        return vector[0], (-vector[1] + self.screen_dim.y)