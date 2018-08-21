from Sword import *

BODY_DIM = Vec2d(7, 45)
VERTICES = [(0, 0), (BODY_DIM.x, 0), (BODY_DIM.x, BODY_DIM.y - 6), (BODY_DIM.x/2, BODY_DIM.y), (0, BODY_DIM.y - 6)]
COLOR = (145, 145, 145)
LIFE_TIME = 250  # ms
ATTACK_POWER = 20
SWING_FORCE = 300


# player sword is not rendered as a dirty sprite, but is manually drawn!
class EnemySword(Sword):
    def __init__(self, enemy):
        super(EnemySword, self).__init__(enemy, ATTACK_POWER, VERTICES, COLOR)

        self.shape.collision_type = self.ge.collision_types["enemy_sword"]