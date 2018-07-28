from Projectile import *

RADIUS = 4
MOVE_FORCE = 600
LIFE_TIME = 1000
ATTACK_POWER = 10


class PlayerProjectile(Projectile):
    def __init__(self, game_engine, screen_dim, start_pos, click_pos):
        super(PlayerProjectile, self).__init__(game_engine, YELLOW, RADIUS * 2,
                                               screen_dim, start_pos, click_pos,
                                               LIFE_TIME, MOVE_FORCE, ATTACK_POWER)

        self.ge.add_player_projectile(self)
        self.shape.collision_type = self.ge.collision_types["player_projectile"]
        self.move()

    def update(self):
        self.dirty = 1
        self.update_image_position(self.body, self.width, self.height)
        self.check_dead()
        #self.rect = (self.body.position.x, self.body.position.y, self.radius, self.radius)