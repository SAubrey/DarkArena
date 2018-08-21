import pymunk
from pymunk.vec2d import Vec2d
import PlayerSword
from PlayerProjectile import PlayerProjectile
from Sprite import *

WHITE = (255, 255, 255)
BODY_DIM = Vec2d(13, 13)
MAX_STAMINA = 100
STAMINA_REGEN_DELAY = 50
MAX_HEALTH = 100
HEALTH_REGEN_DELAY = 500
MAX_MANA = 100
MANA_REGEN_DELAY = 300
SPELL_COST = 8

RUN_FORCE = 1500.0
MAX_RUN_VELOCITY = 300.0
SPRINT_FORCE = 2500.0
MAX_SPRINT_VELOCITY = 600.0

SWING_COST = 20
DASH_COST = 15
DASH_TIME = 90


class Player(Sprite):
    def __init__(self, game_engine, screen_dim):
        super(Player, self).__init__(game_engine, WHITE, BODY_DIM)
        self.screen_dim = Vec2d(screen_dim)
        self.mass = 1.3
        self.radius = BODY_DIM.x / 2
        self.max_velocity = MAX_RUN_VELOCITY
        self.move_force = RUN_FORCE
        self.movement_input = False
        self.sprinting = False
        self.dashing = False
        self.dash_timer = 0

        self.stamina = MAX_STAMINA
        self.health = MAX_HEALTH
        self.mana = MAX_MANA
        self.stamina_regen_timer = 0
        self.health_regen_timer = 0
        self.mana_regen_timer = 0
        self.spell_cost = SPELL_COST
        self.charge_tick_cost = 0
        self.clock = pygame.time.Clock()

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        start_posx = int(max(10, self.screen_dim.x / 3))
        start_posy = int(max(10, self.screen_dim.y / 3))
        self.body.position = (start_posx - BODY_DIM.x / 2, start_posy - BODY_DIM.y / 2)

        self.shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        self.shape.elasticity = 0.9
        self.shape.collision_type = self.ge.collision_types["player"]

        self.rect.x = start_posx
        self.rect.y = start_posy

        # Directions remain true until key unpressed event falsifies
        # to handle holding a key down
        self.up, self.down, self.left, self.right = False, False, False, False
        self.cursor_pos = Vec2d(0, 0)
        self.stats_changed = True  # Determines if a stat update event should be sent
        self.face_angle = self.body.angle  # Forward facing angle for image updates

        self.post_position_update_event()
        self.sword = PlayerSword.PlayerSword(self)
        self.spell_charge = 0

    def update(self):
        Sprite.update(self)

        tick = self.clock.tick()
        self._manage_stats(tick)

        if self.sword.swinging:
            self.sword.update(self.get_centered_pos(), tick)
            # self._deaccelerate(24)
        elif self.sword.charging or self.sword.held_charge:
            self.face_angle = angle_between_points(self.get_centered_pos(), self.cursor_pos)
            self.sword.update(self.get_centered_pos(), tick, self.face_angle)
            self.body.velocity = (0, 0)
        elif self.dashing:
            self.dash_timer += tick
            if self.dash_timer > DASH_TIME:
                self.dash_timer = 0
                self.dashing = False
        else:
            # If not normal movement inhibiting circumstance
            self._manage_velocity_threshholds()
            self.move()
            if not self.movement_input and self.body.velocity != (0, 0):
                self._deaccelerate(8)
            else:
                self.body.velocity = self.cap_velocity(self.body.velocity, self.max_velocity)

    def _manage_velocity_threshholds(self):
        velocity_sum = sum_velocity(self.body.velocity)
        if velocity_sum < 0.1:
            self.body.velocity = (0, 0)
        else:
            if velocity_sum > MAX_RUN_VELOCITY / 8:
                self.face_angle = self.body.velocity.angle
            self.body.angular_velocity = 0
            self.post_position_update_event()

    # Stat managers return True if stat was changed to prompt update event
    def _manage_stats(self, tick):
        h = self._manage_health(tick)
        s = self._manage_stamina(tick)
        m = self._manage_mana(tick)
        if s or h or m:
            self.stats_changed = True
        if self.stats_changed:
            self.post_stat_update_event()

    def _manage_health(self, tick):
        if self.health <= 0:
            pass

        elif self.health < MAX_HEALTH:
            self.health_regen_timer += tick
            if self.health_regen_timer >= HEALTH_REGEN_DELAY:
                self.health += 1
                self.health_regen_timer = 0
                return True
        return False

    def _manage_stamina(self, tick):
        if self.stamina <= 0:
            self._toggle_sprinting(False)

        if self.sprinting:
            self.stamina -= .7
            return True
        elif self.sword.charging:
            #  Sword stops
            tick_charge_cost = self.sword.charge_cost / (self.sword.charge_time / tick)
            if self.stamina >= tick_charge_cost + SWING_COST:
                self.stamina -= tick_charge_cost
            else:
                self.sword.halt_charge()

        elif self.stamina < MAX_STAMINA and not self.sword.held_charge:
            self.stamina_regen_timer += tick
            if self.stamina_regen_timer >= STAMINA_REGEN_DELAY:
                self.stamina += 1
                self.stamina_regen_timer = 0
            return True
        return False

    def _manage_mana(self, tick):
        if self.mana < MAX_MANA:
            self.mana_regen_timer += tick
            if self.mana_regen_timer >= MANA_REGEN_DELAY:
                self.mana += 1
                self.mana_regen_timer = 0
                return True
        return False

    def _toggle_sprinting(self, sprinting):
        if sprinting:
            self.sprinting = True
            self.move_force = SPRINT_FORCE
            self.max_velocity = MAX_SPRINT_VELOCITY
        else:
            self.sprinting = False
            self.move_force = RUN_FORCE
            self.max_velocity = MAX_RUN_VELOCITY

    def _dash(self, cursor_pos):
        if self.stamina >= DASH_COST and not self.dashing and not self.sword.renderable:
            force = projectile_velocity(self.body.position, Vec2d(cursor_pos), 800)
            self.body.velocity = (0, 0)
            self.body.apply_impulse_at_local_point(force, (0, 0))
            self.face_angle = angle_between_points(self.get_centered_pos(), cursor_pos)
            self.stamina -= DASH_COST
            self.dashing = True
            self.stats_changed = True

    def take_damage(self, attack_power):
        if not self.dashing:
            self.health -= attack_power
            self.stats_changed = True

    def _swing_sword(self, click_pos):
        if self.stamina >= SWING_COST and not self.sword.swinging and not self.dashing:
            self.face_angle = angle_between_points(self.get_centered_pos(), click_pos)
            self.body.velocity = Vec2d(0, 0)
            self.sword.swing(self.get_centered_pos(), self.face_angle)
            self.stamina -= SWING_COST
            self.stats_changed = True

    def _cast_spell(self, click_pos):
        if self.mana >= self.spell_cost:
            self.face_angle = angle_between_points(self.get_centered_pos(), click_pos)
            PlayerProjectile(self, click_pos)
            self.mana -= self.spell_cost
            self.stats_changed = True

    # Handles relevant Pygame surface input events
    def handle_input(self, key, down_press, cursor_pos):
        if key == "W":
            self.up = down_press
        elif key == "S":
            self.down = down_press
        elif key == "A":
            self.left = down_press
        elif key == "D":
            self.right = down_press
        elif key == "SPACE":
            # Don't allow sprinting unless stamina is at least half recharged
            if down_press:
                if self.stamina > MAX_STAMINA / 3:
                    self._toggle_sprinting(True)
            else:
                self._toggle_sprinting(False)
        elif key == "SHIFT":
            if down_press and self.stamina > DASH_COST:
                self._dash(cursor_pos)

        if self.up or self.down or self.right or self.left:
            self.movement_input = True
        else:
            self.movement_input = False

    def handle_click(self, click_pos, button, down_press):
        if button == 1:  # Left click
            if down_press:
                if self.stamina >= SWING_COST + self.sword.charge_cost:
                    self.face_angle = angle_between_points(self.get_centered_pos(), self.cursor_pos)
                    self.sword.begin_charge(self.get_centered_pos(), self.face_angle)
                else:
                    self._swing_sword(click_pos)
            else:
                if self.sword.held_charge or self.sword.charging:
                    self._swing_sword(click_pos)
        elif button == 3:  # Right click
            if down_press:
                self._cast_spell(click_pos)

    # WASD MOVEMENT
    def move(self):
        if self.up and self.down:
            return
        if self.right and self.left:
            return

        force = Vec2d(0.0, 0.0)
        if self.up:
            force.y = -1
        elif self.down:
            force.y = 1
        if self.left:
            force.x = -1
        elif self.right:
            force.x = 1
        force *= self.move_force

        if force.x != 0 and force.y != 0:  # Normalize diagonal force
            force = self.move_force * Vec2d.normalized(force)
        if force.x != 0 or force.y != 0:
            self.body.apply_force_at_local_point(force, (0, 0))
        else:
            self._toggle_sprinting(False)

    def _deaccelerate(self, slow_factor):
        counter_force = -self.body.velocity * slow_factor
        self.body.apply_force_at_local_point(counter_force, (0, 0))

    def set_cursor_pos(self, position):
        self.cursor_pos = Vec2d(position)

    def get_position(self):
        return Vec2d(self.rect)

    def post_stat_update_event(self):
        self.ge.post_player_stat_update(self.health, self.stamina, self.mana)

    def post_position_update_event(self):
        self.ge.post_player_position(self.get_position())

    def flip_yaxis(self, vector):
        return vector.x, (-vector.y + self.screen_dim.y)

    def get_face_angle(self):
        return self.face_angle
