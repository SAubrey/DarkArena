import pygame
from pymunk.vec2d import Vec2d

class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, game_engine, color, width, height):
        pygame.sprite.DirtySprite.__init__(self)
        self.ge = game_engine

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        #  rect must remain pygame.Rect type
        self.rect = self.image.get_rect()
        self.color = color
        self.width = width
        self.height = height

    def update(self):
        pass

    def update_image_position(self, body, width, height):
        v = self.get_adjusted_position(body, width, height)
        self.rect.x = v[0]
        self.rect.y = v[1]

    def get_adjusted_position(self, body, width, height):
        return int(body.position.x - width / 2), int(body.position.y - height / 2)

    def cap_velocity(self, velocity, max_velocity):
        vel = Vec2d(velocity)
        vel_sum = abs(vel.x) + abs(vel.y)
        if vel_sum > max_velocity:
            new_vel = Vec2d(0, 0)
            xrat = vel.x / vel_sum
            yrat = vel.y / vel_sum
            new_vel.x = xrat * max_velocity
            new_vel.y = yrat * max_velocity
            return new_vel
        return vel