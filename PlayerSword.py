from Sword import *
import pymunk
import math

BODY_DIM = Vec2d(7, 45)
VERTICES = [(0, 0), (BODY_DIM.x, 0), (BODY_DIM.x, BODY_DIM.y - 6), (BODY_DIM.x/2, BODY_DIM.y), (0, BODY_DIM.y - 6)]
COLOR = (185, 185, 185)
LIFE_TIME = 250  # ms
ATTACK_POWER = 20
SWING_FORCE = 300
CHARGE_COST = 15
CHARGE_TIME = 1000.0


# player sword is not rendered as a dirty sprite, but is manually drawn!
class PlayerSword(Sword):
    def __init__(self, player):
        super(PlayerSword, self).__init__(player, ATTACK_POWER, VERTICES, COLOR, CHARGE_COST, CHARGE_TIME)

        self.shape.collision_type = self.ge.collision_types["player_sword"]
