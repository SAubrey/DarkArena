from Enemy import Enemy
from EnemyProjectile import *
from EnemySword import *
import random
from pymunk.vec2d import Vec2d

RED = (155, 10, 10)
WIDTH, HEIGHT = 15, 15
MAX_HEALTH = 30
ATTACK_POWER = 5
MOVE_FORCE = 200
SPELL_DELAY = 5000
EVASION_DISTANCE = 200
HIT_INTERVAL = 300


class Chaser(Enemy):
    def __init__(self, enemy_manager, screen_dim):
        super(Chaser, self).__init__(enemy_manager, screen_dim, RED, Vec2d(WIDTH, HEIGHT), MAX_HEALTH, ATTACK_POWER)
        self.spell_timer = 0

        self.sword = EnemySword(self)
        enemy_manager.add_sword(self.sword)


    # Called by Game Engine, as a member of Game Engine's Sprite list
    def update(self):
        Enemy.update(self)
        tick = self.clock.tick()
        self.check_spell_action(tick)

        distance = distance_between_points(self.get_centered_pos(), self.player_pos)
        self.check_sword_action(distance, tick)
        if not self.sword.swinging:
            self.move(distance)

    def check_spell_action(self, tick):
        self.spell_timer += tick
        if self.spell_timer >= SPELL_DELAY:
            self._cast_spell()
            self.spell_timer = 0
            self.face_angle = self.body.velocity.angle

    def check_sword_action(self, distance, tick):
        if self.sword.swinging:
            self.sword.update(self.get_centered_pos(), tick)
        else:
            self.attack_interval_timer += tick
            if distance < 30 and self.attack_interval_timer >= HIT_INTERVAL:
                self.attack_interval_timer = 0
                self.swing_sword()

    def move(self, distance):
        if distance <= EVASION_DISTANCE:
            self.evade()
        else:
            self.pursue()

    def evade(self):
        force = projectile_velocity(self.body.position, self.player_pos, -MOVE_FORCE)
        force = self.randomize_force(force, 50, 300, .8)
        self.body.apply_force_at_local_point(force, (0, 0))
        return force

    def pursue(self):
        force = projectile_velocity(self.body.position, self.player_pos, MOVE_FORCE)
        force = self.randomize_force(force, 150, 350, .8)
        self.body.apply_force_at_local_point(force, (0, 0))
        return force

    def _cast_spell(self):
        EnemyProjectile(self, self.player_pos)

    def swing_sword(self):
        self.face_angle = angle_between_points(self.get_centered_pos(), self.player_pos)
        self.body.velocity = Vec2d(0, 0)
        self.sword.swing(self.get_centered_pos(), self.face_angle)


    """How will the enemy judge when to attack? block? """




