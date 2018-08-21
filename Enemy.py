from Sprite import Sprite
import pymunk
import pygame
import random


class Enemy(Sprite):
    def __init__(self, enemy_manager, screen_dim, color, body_dim, max_health, attack_power):
        super(Enemy, self).__init__(enemy_manager.ge, color, body_dim)
        self.em = enemy_manager
        self.screen_dim = screen_dim
        self.mass = 1
        self.radius = body_dim.x / 2
        self.health = max_health
        self.player_pos = (0, 0)
        start_posx = int(max(10, self.screen_dim[0] / 2))
        start_posy = int(max(10, self.screen_dim[1] / 2))

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (start_posx, start_posy)

        self.shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        self.shape.elasticity = 0.9
        self.shape.collision_type = self.ge.collision_types["enemy"]

        self.rect.x = start_posx
        self.rect.y = start_posy

        self.attack_power = attack_power
        self.took_hit = False
        self.clock = pygame.time.Clock()
        self.sword = None
        self.face_angle = self.body.angle
        #self.moving = False
        self.attack_interval_timer = 0

    def update(self):
        Sprite.update(self)

        if self.took_hit:
            self.check_dead()
            self.image.fill(self.color)

    def randomize_force(self, force, min_deviance, max_deviance, chance):
        divergence_chance = random.random()
        if divergence_chance > chance:
            # pd = max(min(random.gauss(0, 80), 300), -300)
            deviance = random.randint(min_deviance, max_deviance)
            deviance *= random.randint(-1, 1)
            force.x += deviance
            force.y += deviance
        return force

    def take_damage(self, attack_power):
        self.health -= attack_power
        self.image.fill((255, 200, 200))
        self.took_hit = True

    def check_dead(self):
        if self.health <= 0:
            self.ge.remove_sprite(self)
            self.em.remove_enemy(self)

    def get_attack_power(self):
        return self.attack_power

    def set_player_position(self, player_position):
        self.player_pos = player_position

