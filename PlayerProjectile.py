from Projectile import *

RADIUS = 4
MOVE_FORCE = 1500


class PlayerProjectile(Projectile):
    def __init__(self, game_engine, screen_dim, start_pos, click_pos):
        super(PlayerProjectile, self).__init__(game_engine, YELLOW, RADIUS, screen_dim, start_pos, click_pos)

        self.ge.add_sprite(self)
        self.move()

    def update(self):
        self.dirty = 1
        self.rect = (self.body.position.x, self.body.position.y, self.radius, self.radius)