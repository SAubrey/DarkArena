from Sprite import Sprite
import pymunk
from pymunk.vec2d import Vec2d
from PlayerProjectile import PlayerProjectile

WHITE = (255, 255, 255)
WIDTH, HEIGHT = 10, 10
MAX_STAMINA = 100
MAX_HEALTH = 100
MAX_MANA = 100


class Player(Sprite):
    def __init__(self, game_engine, screen_dim):
        super(Player, self).__init__(game_engine, WHITE, WIDTH, HEIGHT)
        self.screen_dim = Vec2d(screen_dim)
        self.mass = 0.7
        self.radius = WIDTH / 2
        self.run_force, self.sprint_force = 1000.0, 700.0
        self.max_velocity = 300.0
        self.move_force = self.run_force
        self.moving, self.sprinting = False, False
        start_posx = int(max(10, self.screen_dim.x / 3))
        start_posy = int(max(10, self.screen_dim.y / 3))

        self.stamina = MAX_STAMINA
        self.health = MAX_HEALTH
        self.mana = MAX_MANA

        self.projectiles = ()

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (start_posx, start_posy)
        #self.body.damping = 0.2

        shape = pymunk.Circle(self.body, self.radius) # Collision shape
        shape.elasticity = 0.3

        self.rect.x = start_posx
        self.rect.y = start_posy
        self.ge.add_body(self.body, shape)

        # Directions remain true until key unpressed event falsifies
        # to handle holding a key down
        self.up, self.down, self.left, self.right = False, False, False, False
        self.last_up, self.last_down, self.last_left, self.last_right = False, False, False, False
        self.cursor_pos = Vec2d(0, 0)


    def update(self):
        self.dirty = 1
        self.rect = (self.body.position.x, self.body.position.y, WIDTH, HEIGHT)
        self.move()
        self.cap_velocity()
        self.manage_stamina()
        self.post_update_event()
        self.ge.post_player_position(self.rect)
        self.deaccelerate()
        # Let renderer only worry about drawing sprites, and update sprite data here

    def post_update_event(self):
        self.ge.post_player_update(self.health, self.stamina, self.mana)

    def manage_stamina(self):
        if self.stamina == 0:
            self.sprinting = False

        if self.moving:
            if self.sprinting and self.stamina > 0:
                self.move_force = self.sprint_force
                self.max_velocity = self.sprint_force
                self.stamina -= 1

        if not self.sprinting:
            self.move_force = self.run_force
            if self.stamina < MAX_STAMINA:
                self.stamina += 1

    def deaccelerate(self):
        if not self.moving:
            vec = -self.body.velocity * 2
            self.body.apply_force_at_local_point(vec, (0, 0))

    # MOUSE MOVEMENT (moving towards mouse position)
    # def move2(self):
    #     pos = Vec2d(self.rect[0], self.rect[1])
    #     cpos = Vec2d(self.cursor_pos)
    #
    #     dx = (cpos.x - pos.x)
    #     dy = (cpos.y - pos.y)
    #     if dx == 0: dx += 1  # Don't divide by 0
    #     if dy == 0: dy += 1
    #     slope = abs(dx / dy)
    #     vec = Vec2d(self.move_force, self.move_force)
    #     if dx < 0:  # Account for all cartesian quadrants
    #         vec.x *= -1
    #     if dy < 0:
    #         vec.y *= -1
    #     vec.x *= (slope/(slope + 1))
    #     vec.y *= (1/(slope + 1))
    #     #self.body.apply_force_at_local_point(vec, (0, 0))
    #     self.body.velocity = vec

    def cast_spell(self, click_pos):
        #TODO: REVISE PROJECTILE START POSITION
        x1 = self.body.position.x
        x2 = self.body.position.y
        pp = PlayerProjectile(self.ge, self.screen_dim, (x1, x2), click_pos)
        #self.projectiles.add(pp)

    def handle_input(self, key, down_press):
        if key == "W":
            self.last_up = self.up  # Record for next iteration
            self.up = down_press
           # self.moving = down_press
        elif key == "S":
            self.last_down = self.down
            self.down = down_press
        elif key == "A":
            self.last_left = self.left
            self.left = down_press
        elif key == "D":
            self.last_right = self.right
            self.right = down_press
        elif key == "SPACE":
            # Don't allow sprinting unless stamina is at least half recharged
            if self.stamina < MAX_STAMINA / 2 and down_press is True:
                return
            self.sprinting = down_press

    def handle_click(self, click_pos, button):
        if button == 1:  # Left click
            pass
        elif button == 3:  # Right click
            self.cast_spell(click_pos)

    # WASD MOVEMENT
    def move(self):
        self.moving = False
        force = Vec2d(0.0, 0.0)
        impulse = Vec2d(0.0, 0.0)
        if self.up and self.down:
            return
        if self.right and self.left:
            return
        if self.up:
            if self.last_up is False:
                self.last_up = True
                impulse.y = -1
            else:
                force.y = -1
        elif self.down:
            if self.last_down is False:
                self.last_down = True
                impulse.y = 1
            else:
                force.y = 1
        if self.left:
            if self.last_left is False:
                self.last_left = True
                impulse.x = -1
            else:
                force.x = -1
        elif self.right:
            if self.last_right is False:
                self.last_right = True
                impulse.x = 1
            else:
                force.x = 1

        force *= self.move_force
        impulse *= self.max_velocity

        if force.x != 0 and force.y != 0:
            force = self.move_force * Vec2d.normalized(force)
        if impulse.x != 0 and impulse.y != 0:
            impulse = self.max_velocity * Vec2d.normalized(impulse)
        if force.x != 0 or force.y != 0:
            self.body.apply_force_at_local_point(force, (0, 0))
            self.moving = True
        if impulse.x != 0 or impulse.y != 0:
            #self.body.apply_impulse_at_local_point(impulse / 2, (0, 0))
            self.moving = True

    def cap_velocity(self):
        vel = Vec2d(self.body.velocity)
        new_vel = Vec2d(0, 0)
        vel_sum = abs(vel.x) + abs(vel.y)
        if vel_sum > self.max_velocity:
            xrat = vel.x/vel_sum
            yrat = vel.y/vel_sum
            new_vel.x = xrat * self.max_velocity
            new_vel.y = yrat * self.max_velocity
            self.body.velocity = new_vel

    def set_cursor_pos(self, position):
        self.cursor_pos = Vec2d(position)

    def flip_yaxis(self, vector):
        return vector.x, (-vector.y + self.screen_dim.y)

    def get_projectiles(self):
        return self.projectiles
