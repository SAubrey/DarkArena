from Sprite import *
import pymunk
import math

BODY_DIM = Vec2d(7, 45)
LIFE_TIME = 250  # ms
SWING_FORCE = 300
MAX_CHARGE = 2  # Charge is an attack multiplier


# player sword is not rendered as a dirty sprite, but is manually drawn!
class Sword(object):
    def __init__(self, owner, attack_power, vertices, color, charge_cost=None, charge_time=None):
        self.owner = owner
        self.ge = self.owner.ge
        self.attack_power = attack_power
        self.base_color = color
        self.color = color
        self.charge_cost = charge_cost
        self.charge_time = charge_time

        mass = .01
        self.vertices = vertices
        moment = pymunk.moment_for_poly(mass, vertices)
        self.body = pymunk.Body(mass, moment)

        self.shape = pymunk.Poly(self.body, vertices, pymunk.Transform.identity(), 1)  # Transform?
        self.shape.sensor = True

        self.pj = None
        self.spawn_angle = 0

        self.swing_timer = 0
        self.charge_timer = 0
        self._swinging = False
        self._charging = False
        self._held_charge = False  # Complete charge that is waiting to be swung
        self._renderable = False
        self._body_formed = False
        self.charge = 1.0
        self.max_charge = MAX_CHARGE

    def _form_body(self, owner_pos, face_angle):
        self.init_time = pygame.time.get_ticks()
        self.spawn_angle = face_angle + math.pi/2  # To the right of the player

        spawn_point = angled_offset_pos(owner_pos, self.spawn_angle, 10)
        self.body.position = spawn_point
        self.body.angle = angle_between_points(owner_pos, self.body.position) - math.pi / 2

        self.pj = pymunk.PinJoint(self.owner.body, self.body, (0, 0), (0, 0))
        self.pj.collide_bodies = True
        #self.pj.distance = 10

        self.ge.add_body(self.body, self.shape)
        self.ge.space.add(self.pj)
        self._body_formed = True

    def update_charge_position(self, owner_pos, face_angle):
        angle = face_angle + math.pi/2
        position = angled_offset_pos(owner_pos, angle, 10)
        self.body.position = position
        self.body.angle = angle_between_points(owner_pos, self.body.position) - math.pi / 2

    #  Sword charges while mouse button is held down until at max charge or
    # the player is out of stamina, but only swings once the button is released.
    def update(self, owner_pos, tick, face_angle=None):
        if self.swinging:
            self.swing_timer += tick
            if self.swing_timer > LIFE_TIME:
                self.despawn()
                self.swinging = False
                self.swing_timer = 0
        elif self.charging:
            self._increase_charge(tick)
            self.update_charge_position(owner_pos, face_angle)
        elif self.held_charge:
            self.update_charge_position(owner_pos, face_angle)
        elif not self.held_charge:
            pass
            # self.deaccelerate()
        self.body.angle = angle_between_points(owner_pos, self.body.position) - math.pi / 2

    def _increase_charge(self, tick):
        self.charge += float(tick) / self.charge_time  # 1 < charge < 2 (1000ms)
        self.color = self._determine_charged_color(self.charge)
        if self.charge >= self.max_charge:
            self.halt_charge()

    def halt_charge(self):
        self.charging = False
        self.held_charge = True

    def begin_charge(self, owner_pos, face_angle):
        self.charging = True
        self._form_body(owner_pos, face_angle)

    def _determine_charged_color(self, charge):
        c1 = min(int(charge * self.base_color[0]), 255)
        c3 = c1
        c2 = min(int(self.base_color[0] / charge), 255)
        return c1, c2, c3

    def swing(self, owner_pos, face_angle):
        if not self._body_formed:
            self._form_body(owner_pos, face_angle)
        self.charging = False
        self.held_charge = False
        self.swinging = True
        # angle_vector = Vec2d(math.cos(self.spawn_angle), math.sin(self.spawn_angle))
        # swing_vector = angle_vector.perpendicular_normal() * SWING_FORCE
        # #swing_vector = angle_vector * SWING_FORCE
        offset = 500
        target_pos = angled_offset_pos(self.body.position, face_angle, offset)
        self.body.velocity = projectile_velocity(self.body.position, target_pos, SWING_FORCE)

    def deaccelerate(self):
        if pygame.time.get_ticks() - self.init_time > 3 * LIFE_TIME / 6:
            self.body.velocity *= .9
        if pygame.time.get_ticks() - self.init_time > 4 * LIFE_TIME / 6:
            self.body.velocity *= .4

    def despawn(self):
        self.charge = 1
        self.ge.remove_body(self.body, self.shape)
        self.ge.remove_joint(self.pj)
        self._body_formed = False

    def check_render_status(self):
        if self.charging or self.swinging or self.held_charge:
            self.renderable = True
        else:
            self.renderable = False

    @property
    def swinging(self):
        return self._swinging

    @swinging.setter
    def swinging(self, swinging):
        self._swinging = swinging
        self.check_render_status()

    @property
    def charging(self):
        return self._charging

    @charging.setter
    def charging(self, charging):
        self._charging = charging
        self.check_render_status()

    @property
    def held_charge(self):
        return self._held_charge

    @held_charge.setter
    def held_charge(self, held_charge):
        self._held_charge = held_charge
        self.check_render_status()

    @property
    def renderable(self):
        return self._renderable

    @renderable.setter
    def renderable(self, renderable):
        self._renderable = renderable

    def get_attack_power(self):
        return self.attack_power * self.charge

    def get_angle(self):
        return self.body.angle

    def get_position(self):
        return self.body.position

    def get_vertices(self):
        return self.shape.get_vertices()
