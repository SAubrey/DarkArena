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
        self.post_event = self.em.post
        self.screen_dim = Vec2d(screen_dim)
        event_manager.add_listener(self, "Game Engine")
        self.enemy_manager = None
        self.running = False

        self.collision_types = {
            "player": 1,
            "pprojectile": 2,
            "enemy": 3,
            "eprojectile": 4,
            "player_sword": 5,
            "enemy_sword": 6
        }

        #  Sprite lists
        self.all_sprites = None
        self.enemies = []
        #self.nonplayer_sprites = []
        #self.player_projectiles = []
        #self.enemy_projectiles = []
        #self.enemy_sprites = []

        #  enemies dict allows enemy object lookup from its pymunk body in collision handling
        self.enemy_dict = {}
        self.sword_dict = {}
        self.pprojectiles = {}
        self.eprojectiles = {}

        #  Collision handler dictionaries key: pygame.body value: sprite
        #  Order defined by: ch_attacked_attacker
        self.ch_player_enemy = None
        self.ch_player_eprojectile = None
        self.ch_player_enemy_sword = None
        self.ch_enemy_player_sword = None
        self.ch_enemy_pprojectile = None

        self.player = None
        self.initialized = False

        self.space = None  # Pymunk physics simulation field

    def initialize(self):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.space.damping = 0.8  # lower = more dampening
        self.all_sprites = pygame.sprite.LayeredDirty()
        #self.nonplayer_sprites = pygame.sprite.LayeredDirty()
        #self.player_projectiles = pygame.sprite.Group()
        #self.enemy_projectiles = pygame.sprite.Group()
        #self.enemy_sprites = pygame.sprite.Group()

        # self.ch_player_enemy = self.space.add_collision_handler(self.collision_types["player"],
        #                                                         self.collision_types["enemy"])
        # self.ch_player_enemy.begin = self.player_enemy_begin

        self.ch_player_eprojectile = self.space.add_collision_handler(self.collision_types["player"],
                                                                      self.collision_types["eprojectile"])
        self.ch_player_eprojectile.begin = self.player_eprojectile_begin

        self.ch_player_enemy_sword = self.space.add_collision_handler(self.collision_types["player"],
                                                                      self.collision_types["enemy_sword"])
        self.ch_player_enemy_sword.begin = self.player_enemy_sword_begin

        self.ch_enemy_pprojectile = self.space.add_collision_handler(self.collision_types["enemy"],
                                                                     self.collision_types["pprojectile"])
        self.ch_enemy_pprojectile.begin = self.enemy_pprojectile_begin

        self.ch_enemy_player_sword = self.space.add_collision_handler(self.collision_types["enemy"],
                                                               self.collision_types["player_sword"])
        self.ch_enemy_player_sword.begin = self.enemy_player_sword_begin

        #self.ch_pprojectile = self.space.add_wildcard_collision_handler(self.collision_types["pprojectile"])

        self.create_player()

        self.enemy_manager = EnemyManager(self, self.screen_dim)
        self.enemies = self.enemy_manager.enemies
        self.sword_dict = self.enemy_manager.sword_dict
        self.enemy_dict = self.enemy_manager.enemy_dict

        self.create_borders()
        self.initialized = True
        print("Game Engine init")

    def run(self):
        if not self.initialized:
            self.initialize()
        self.running = True

        self.post_event(InitializeEvent())
        self.player.post_position_update_event()
        self.post_event(ModelShareEvent(self.space, self.all_sprites, self.player.sword, self.enemy_manager.swords))

        step = self.space.step
        while self.running:
            self.post_event(TickEvent())
            self.all_sprites.update()  # calls update for each sprite
            self.enemy_manager.update(self.player.get_centered_pos())
            step(1 / 60.0)

    def notify(self, event):
        en = event.name
        if en == EV_INPUT:
            self.player.handle_input(event.key, event.down_press, event.cursor_pos)
        elif en == EV_MOUSE_MOVE:
            self.player.set_cursor_pos(event.position)
        elif en == EV_MOUSE_CLICK:
            self.player.handle_click(event.position, event.button, event.down_press)
        elif en == EV_RESIZE:
            self.screen_dim = Vec2d(event.width, event.height)
        elif en == EV_QUIT:
            self.running = False

    def player_eprojectile_begin(self, arbiter, space, data):
        player_shape, eprojectile_shape = arbiter.shapes
        ep = self.eprojectiles[eprojectile_shape]
        self._register_attack(self.player, ep)
        ep.destroy()
        return False

    # def player_enemy_begin(self, arbiter, space, data):
    #     player_shape, enemy_shape = arbiter.shapes
    #     self._register_attack(self.player, self.enemy_dict[enemy_shape])
    #     return True

    def player_enemy_sword_begin(self, arbiter, space, data):
        player_shape, enemy_sword_shape = arbiter.shapes
        self._register_attack(self.player, self.sword_dict[enemy_sword_shape])
        return False

    def enemy_pprojectile_begin(self, arbiter, space, data):
        enemy_shape, pprojectile_shape = arbiter.shapes
        pp = self.pprojectiles[pprojectile_shape]
        e = self.enemy_dict[enemy_shape]
        self._register_attack(e, pp)
        pp.destroy()
        #TODO: Create kill list of sprites/bodies to be removed at the next tick?
        return False  # Do not finish calculating collision

    def enemy_player_sword_begin(self, arbiter, space, data):
        enemy_shape, sword_shape = arbiter.shapes
        self._register_attack(self.enemy_dict[enemy_shape], self.player.sword)
        return True

    def _register_attack(self, attacked, attacker):
        #if not attacked.in_contact:
        attacked.take_damage(attacker.get_attack_power())
        attacked.in_contact = True

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
        bodies = self.space.bodies
        if body not in bodies:
            self.space.add(body, shape)

    def remove_body(self, body, shape):
        bodies = self.space.bodies
        if body in bodies:
            self.space.remove(body, shape)

    def remove_joint(self, joint):
        constraints = self.space.constraints
        if joint in constraints:
            self.space.remove(joint)

    def add_sprite(self, sprite):
        self.all_sprites.add(sprite)

    def create_player(self):
        self.player = Player.Player(self, self.screen_dim)
        self.all_sprites.add(self.player)
        self.add_body(self.player.body, self.player.shape)

    def add_enemy(self, enemy):
        self.add_body(enemy.body, enemy.shape)
        self.add_sprite(enemy)

    def add_projectile(self, projectile):
        self.space.add(projectile.body, projectile.shape)
        self.all_sprites.add(projectile)
        if projectile.shape.collision_type == self.collision_types["pprojectile"]:
            self.pprojectiles[projectile.shape] = projectile
        else:
            self.eprojectiles[projectile.shape] = projectile

    def remove_projectile(self, projectile_shape):
        if projectile_shape.collision_type == self.collision_types["pprojectile"]:
            del self.pprojectiles[projectile_shape]
        else:
            del self.eprojectiles[projectile_shape]

    def remove_sprite(self, sprite):
        self.space.remove(sprite.shape, sprite.body)
        sprite.kill()  # Removes sprite from all associated sprite lists

    def get_all_sprites(self):
        return self.all_sprites

    def get_space(self):
        return self.space

    def post_player_position(self, position):
        self.em.post(PlayerMoveEvent(position))

    def post_player_stat_update(self, health, stamina, mana):
        self.em.post(PlayerStatUpdate(health, stamina, mana))

    def flip_yaxis(self, vector):
        return vector[0], (-vector[1] + self.screen_dim.y)