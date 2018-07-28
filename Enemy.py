from Sprite import Sprite
import pymunk
import random
import pygame

RED = (255, 50, 50)
WIDTH, HEIGHT = 15, 15


class Enemy(Sprite):
    def __init__(self, game_engine, screen_dim):
        super(Enemy, self).__init__(game_engine, RED, WIDTH, HEIGHT)
        self.screen_dim = screen_dim
        self.mass = 1
        self.radius = WIDTH / 2
        self.health = 20
        start_posx = int(max(10, self.screen_dim[0] / 2))
        start_posy = int(max(10, self.screen_dim[1] / 2))

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (start_posx, start_posy)

        self.shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        self.shape.elasticity = 0.3
        self.shape.collision_type = self.ge.collision_types["enemy"]

        self.rect.x = start_posx
        self.rect.y = start_posy
        self.ge.add_body(self.body, self.shape)
        self.ge.add_enemy(self)

        self.attack_power = 5

    def update(self):
        self.dirty = 1
        self.update_image_position(self.body, self.width, self.height)
        self.image.fill(RED)
        fx = random.randint(-1000, 1000)
        fy = random.randint(-1000, 1000)
        self.check_dead()
        #self.body.apply_force_at_local_point((fx, fy), (0, 0))

        # Let renderer only worry about drawing sprites, and update sprite data here

    def take_damage(self, attack_power):
        self.health -= attack_power
        self.image.fill((200, 255, 200))

    def check_dead(self):
        if self.health <= 0:
            self.ge.remove_enemy(self)

    def get_attack_power(self):
        return self.attack_power
