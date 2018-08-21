from Sprite import *
import pymunk
from pymunk.vec2d import Vec2d
import pygame

YELLOW = (200, 200, 20)
PURPLE = (200, 0, 200)


class Projectile(Sprite):
    def __init__(self, shooter, color, radius, target_pos, life_time, move_force, attack_power):
        super(Projectile, self).__init__(shooter.ge, color, Vec2d(radius * 2, radius * 2))
        self.start_pos = calculate_pos_between_points(shooter.get_centered_pos(), target_pos, shooter.radius + 5)
        self.target_pos = Vec2d(target_pos)
        self.radius = radius
        self.mass = 0.01
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

        self.life_time = life_time  # ms
        self.birth_time = pygame.time.get_ticks()

        self.fire()

    def check_expired(self):
        elapsed_time = pygame.time.get_ticks() - self.birth_time
        if elapsed_time > self.life_time:
            self.destroy()

    def destroy(self):
        self.ge.remove_projectile(self.shape)
        self.ge.remove_sprite(self)

    def get_attack_power(self):
        return self.attack_power

    def update(self):
        pass

    def fire(self):
        start_pos = calculate_pos_between_points(self.get_centered_pos(), self.target_pos, self.radius + 5)
        force = projectile_velocity(start_pos, self.target_pos, self.move_force)
        self.body.apply_force_at_local_point(force, (0, 0))


