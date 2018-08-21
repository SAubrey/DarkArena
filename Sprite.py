import pygame
import math
from pymunk.vec2d import Vec2d


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, game_engine, color, body_dim):
        pygame.sprite.DirtySprite.__init__(self)
        self.ge = game_engine

        self.body = None
        self.image = pygame.Surface([body_dim.x, body_dim.y])
        self.image.fill(color)

        #  rect must remain pygame.Rect type
        self.rect = self.image.get_rect()
        self.color = color
        self.body_dim = body_dim

        # Turned on in first collision handle, off when collided bodies separate.
        # This prevents registering of multiple hits for a single attack
        #self._in_contact = False

    def update(self):
        self.dirty = 1
        self.update_image_position(self.body, self.body_dim)

    # Set render position to top-left corner of the body
    def update_image_position(self, body, body_dim):
        self.rect.x = int(body.position.x - body_dim.x / 2)
        self.rect.y = int(body.position.y - body_dim.y / 2)

    def cap_velocity(self, velocity, max_velocity):
        """
        Caps velocity so that bodies move as fast diagonally as horizontally/vertically.
        The absolute difference (vel_difference) between the current x and y velocities
        is used to determine the degree to which the body is moving diagonally. (0 == perfectly diagonal)
        This difference is then constrained by the max velocity. The ratio of this difference to the max
        velocity is inverted, so that max velocity is multiplied by some n that is 0.707 < n < 1. Thus,
        the more vertical/horizontal the current movement, the lower the velocity cap.
        .707 is sqrt(2)/2, the normalization factor for diagonal movement.
        """
        vel = Vec2d(velocity)
        vel_sum = abs(vel.x) + abs(vel.y)
        if vel_sum < max_velocity * .707:  # Don't cap unless lower bound velocity is reached
            return vel
        vel_difference = abs(abs(vel.x) - abs(vel.y))
        relative_vd = vel_difference * (max_velocity/vel_sum) # since vel>max
        max_velocity *= max(1 - relative_vd/max_velocity, .707)
        if vel_sum > max_velocity:
            new_vel = Vec2d(0, 0)
            xrat = vel.x / vel_sum
            yrat = vel.y / vel_sum
            new_vel.x = xrat * max_velocity
            new_vel.y = yrat * max_velocity
            return new_vel
        return vel

    def get_centered_pos(self):
        # self.body.position returns the same as the following though without decimal accuracy
        return Vec2d(self.rect.x + self.body_dim.x/2, self.rect.y + self.body_dim.y/2)

    # @property
    # def in_contact(self):
    #     return self._in_contact
    #
    # @in_contact.setter
    # def in_contact(self, in_contact):
    #     self._in_contact = in_contact


def calculate_pos_between_points(p1, p2, offset):
    angle = angle_between_points(p1, p2)
    return angled_offset_pos(p1, angle, offset)


def angle_between_points(p1, p2):
    return (Vec2d(p2) - Vec2d(p1)).angle


# def angled_offset_position(p, angle, offset):
#     return Vec2d(p + Vec2d(offset, 0).rotated(angle))

def angled_offset_pos(p, angle, offset):
    x = offset * math.cos(angle) + p.x
    y = offset * math.sin(angle) + p.y
    return Vec2d(x, y)


def sum_velocity(velocity):
    velocity = Vec2d(velocity)
    return abs(velocity.x) + abs(velocity.y)


def distance_between_points(p1, p2):
    p = Vec2d(p1 - p2)
    return math.sqrt(p.x**2 + p.y**2)


def projectile_velocity(start, dest, move_force):
    start, dest = Vec2d(start), Vec2d(dest)

    dx, dy = (dest.x - start.x), (dest.y - start.y)
    if dx == 0:
        dx += 1
    if dy == 0:
        dy += 1
    slope = abs(dy / dx)
    vel = Vec2d(1, 1)
    if dx < 0:
        vel.x *= -1
    if dy < 0:
        vel.y *= -1
    vel.y *= (slope / (slope + 1))
    vel.x *= (1 / (slope + 1))
    vel = Vec2d.normalized(vel)
    vel *= move_force
    return vel
