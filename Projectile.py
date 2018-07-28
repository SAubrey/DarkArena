from Sprite import Sprite
import pymunk
from pymunk.vec2d import Vec2d
import pygame


YELLOW = (200, 20, 200)


class Projectile(Sprite):
    def __init__(self, game_engine, color, radius, screen_dim, start_pos, dest_pos, life_time, move_force, attack_power):
        super(Projectile, self).__init__(game_engine, color, radius, radius)
        self.screen_dim = screen_dim
        self.start_pos = Vec2d(start_pos)
        self.dest_pos = Vec2d(dest_pos)
        self.radius = radius
        self.mass = 0.02
        self.move_force = move_force
        self.attack_power = attack_power

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (self.start_pos.x, self.start_pos.y)
        # self.body.damping = 0.2

        self.shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        self.shape.elasticity = 0.3

        self.rect.x = self.start_pos.x
        self.rect.y = self.start_pos.y
        self.ge.add_body(self.body, self.shape)
        #self.ge.add_sprite(self)

        self.life_time = life_time  # ms
        self.birth_time = pygame.time.get_ticks()

    def move(self):
        start = self.start_pos
        dest = self.dest_pos

        dx = (dest.x - start.x)
        dy = (dest.y - start.y)
        if dx == 0: dx += 1
        if dy == 0: dy += 1
        slope = abs(dx / dy)
        vec = Vec2d(self.move_force, self.move_force)
        if dx < 0:
            vec.x *= -1
        if dy < 0:
            vec.y *= -1
        vec.x *= (slope/(slope + 1))
        vec.y *= (1/(slope + 1))
        self.body.apply_force_at_local_point(vec, (0, 0))

    def check_dead(self):
        elapsed_time = pygame.time.get_ticks() - self.birth_time
        if elapsed_time > self.life_time:
            self.ge.remove_projectile(self)

    def get_attack_power(self):
        return self.attack_power

    def update(self):
        pass