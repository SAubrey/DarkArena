import pygame
import Player
import Enemy
import pymunk
from pymunk.vec2d import Vec2d
from EventManager import *
from EnemyManager import *



# Game Model
class GameEngine(object):
    def __init__(self, event_manager, screen_dim):
        self.em = event_manager
        self.screen_dim = Vec2d(screen_dim)
        event_manager.add_listener(self, "Game Engine")
        self.enemy_manager = None
        self.running = False

        self.collision_types = {
            "player": 1,
            "player_projectile": 2,
            "enemy": 3,
            "enemy_projectile": 4
        }

        #  Sprite lists
        self.all_sprites = None
        self.nonplayer_sprites = []
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.enemy_sprites = []

        self.ch_player_enemy = None
        self.ch_player_projectile = None

        self.player = None
        self.initialized = False

        self.space = None  # Pymunk physics simulation field

    def initialize(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.space.damping = 0.8  # lower = more dampening
        self.all_sprites = pygame.sprite.LayeredDirty()
        self.nonplayer_sprites = pygame.sprite.LayeredDirty()
        self.player_projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        self.ch_player_enemy = self.space.add_collision_handler(self.collision_types["player"], self.collision_types["enemy"])
        self.ch_player_enemy.pre_solve = self.pre_solve_player_enemy
        self.ch_player_projectile = self.space.add_wildcard_collision_handler(self.collision_types["player_projectile"])

        self.create_player()
        self.enemy_manager = EnemyManager(self)

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
            self.manage_collisions()

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

    def pre_solve_player_enemy(self, arbiter, space, data):
        player, enemy = arbiter.shapes
        

        return True

    def manage_collisions(self):
        pass

        # If True, all collided sprites will be removed from group
        # player_collisions = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False)
        # for c in player_collisions:
        #     self.player.take_damage(c.get_attack_power())

        # if len(self.enemy_sprites) > 0 and len(self.player_projectiles) > 0:
        #     enemy_collisions = pygame.sprite.groupcollide(self.enemy_sprites, self.player_projectiles, False, True)
        #     for enemy in enemy_collisions:
        #         ps = enemy_collisions[enemy]
        #         enemy.take_damage(ps[0].get_attack_power())
        #         for p in ps:
        #             self.remove_projectile(p)


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

    def add_body(self, body, shape):
        self.space.add(body, shape)

    def create_player(self):
        self.player = Player.Player(self, self.screen_dim)
        self.all_sprites.add(self.player)

    def create_enemy(self):
        enemy = Enemy.Enemy(self, self.screen_dim)
        self.all_sprites.add(enemy)
        self.enemy_sprites.add(enemy)
        self.nonplayer_sprites.add(enemy)

    def add_enemy(self, enemy):
        self.all_sprites.add(enemy)
        self.nonplayer_sprites.add(enemy)
        self.enemy_sprites.add(enemy)

    def remove_enemy(self, enemy):
        self.space.remove(enemy.shape, enemy.body)
        enemy.kill()

    def add_player_projectile(self, sprite):
        self.all_sprites.add(sprite)
        self.nonplayer_sprites.add(sprite)
        self.player_projectiles.add(sprite)

    def add_enemy_projectile(self, sprite):
        self.all_sprites.add(sprite)
        self.nonplayer_sprites.add(sprite)
        self.enemy_projectiles.add(sprite)

    def remove_projectile(self, sprite):
        self.space.remove(sprite.shape, sprite.body)
        sprite.kill()

    def get_all_sprites(self):
        return self.all_sprites

    def get_space(self):
        return self.space

    def post_player_position(self, position):
        self.em.post(PlayerMoveEvent(position))

    def post_player_update(self, health, stamina, mana):
        self.em.post(PlayerStatUpdate(health, stamina, mana))

    def flip_yaxis(self, vector):
        return vector[0], (-vector[1] + self.screen_dim.y)