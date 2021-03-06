from Projectile import *
from Sprite import *

RADIUS = 4
MOVE_FORCE = 400
LIFE_TIME = 1000
ATTACK_POWER = 10


class PlayerProjectile(Projectile):
    def __init__(self, player, click_pos):
        super(PlayerProjectile, self).__init__(player, PURPLE, RADIUS, click_pos,
                                               LIFE_TIME, MOVE_FORCE, ATTACK_POWER)

        self.shape.collision_type = self.ge.collision_types["pprojectile"]
        self.ge.add_projectile(self)

    def update(self):
        Sprite.update(self)
        self.check_expired()

