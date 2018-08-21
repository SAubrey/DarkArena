from Projectile import *
from Sprite import *

RADIUS = 4
MOVE_FORCE = 400
LIFE_TIME = 1000
ATTACK_POWER = 10


class EnemyProjectile(Projectile):
    def __init__(self, enemy, player_pos):
        super(EnemyProjectile, self).__init__(enemy, YELLOW, RADIUS, player_pos,
                                               LIFE_TIME, MOVE_FORCE, ATTACK_POWER)

        self.shape.collision_type = self.ge.collision_types["eprojectile"]
        self.shape.sensor = True  # Allow passing through other enemies
        self.ge.add_projectile(self)

    def update(self):
        Sprite.update(self)
        self.check_expired()

