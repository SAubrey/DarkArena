from Sprite import Sprite
import pymunk
from pymunk.vec2d import Vec2d
from PlayerProjectile import PlayerProjectile

WHITE = (255, 255, 255)
WIDTH, HEIGHT = 100, 100
MAX_STAMINA = 100
MAX_HEALTH = 100
MAX_MANA = 100
RUN_FORCE = 1500.0
MAX_RUN_VELOCITY = 300.0
SPRINT_FORCE = 2500.0
MAX_SPRINT_VELOCITY = 600.0


class Player(Sprite):
    def __init__(self, game_engine, screen_dim):
        super(Player, self).__init__(game_engine, WHITE, WIDTH, HEIGHT)
        self.screen_dim = Vec2d(screen_dim)
        self.mass = 0.7
        self.radius = WIDTH / 2
        self.max_velocity = MAX_RUN_VELOCITY
        self.move_force = RUN_FORCE
        self.moving, self.sprinting = False, False
        start_posx = int(max(10, self.screen_dim.x / 3))
        start_posy = int(max(10, self.screen_dim.y / 3))

        self.stamina = MAX_STAMINA
        self.health = MAX_HEALTH
        self.mana = MAX_MANA

        self.projectiles = []

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (start_posx - WIDTH/2, start_posy - HEIGHT/2)
        #self.body.damping = 0.2

        self.shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        self.shape.elasticity = 0.3
        self.shape.collision_type = self.ge.collision_types["player"]

        self.rect.x = start_posx
        self.rect.y = start_posy
        self.ge.add_body(self.body, self.shape)

        # Directions remain true until key unpressed event falsifies
        # to handle holding a key down
        self.up, self.down, self.left, self.right = False, False, False, False
        self.cursor_pos = Vec2d(0, 0)
        self.stats_changed = False  # Determines if a stat update event should be sent

    def update(self):
        self.dirty = 1
        # Update surface rect to physics body position
        # (Adjusted for differences in origin coord between pygame/pymunk)
        self.update_image_position(self.body, WIDTH, HEIGHT)
        self.move()
        self.body.velocity = self.cap_velocity(self.body.velocity, self.max_velocity)
        self.deaccelerate()
        self.manage_stamina()
        if self.stats_changed:  # Only update if there's new info
            self.post_update_event()
        self.ge.post_player_position(self.rect)

    def post_update_event(self):
        self.ge.post_player_update(self.health, self.stamina, self.mana)
        self.stats_changed = False

    def manage_stamina(self):
        if self.stamina <= 0:
            self.toggle_sprinting(False)

        if self.sprinting:
            if self.stamina > 0 and self.moving:
                self.stamina -= 1
                self.stats_changed = True
        elif self.stamina < MAX_STAMINA:
                self.stamina += 1
                self.stats_changed = True

    def toggle_sprinting(self, sprinting):
        if sprinting:
            self.sprinting = True
            self.move_force = SPRINT_FORCE
            self.max_velocity = MAX_SPRINT_VELOCITY
        else:
            self.sprinting = False
            self.move_force = RUN_FORCE
            self.max_velocity = MAX_RUN_VELOCITY

    def deaccelerate(self):
        if not self.moving:
            counter_force = -self.body.velocity * 4
            self.body.apply_force_at_local_point(counter_force, (0, 0))

    def cast_spell(self, click_pos):
        #TODO: REVISE PROJECTILE START POSITION
        x = self.body.position.x
        y = self.body.position.y
        pp = PlayerProjectile(self.ge, self.screen_dim, (x, y), click_pos)
        self.mana -= 10
        self.stats_changed = True
        #self.projectiles.append(pp)

    def handle_input(self, key, down_press):
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
                if self.stamina > MAX_STAMINA / 2:
                    self.toggle_sprinting(True)
            else:
                self.toggle_sprinting(False)

    def handle_click(self, click_pos, button):
        if button == 1:  # Left click
            pass
        elif button == 3:  # Right click
            self.cast_spell(click_pos)

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

        if force.x != 0 and force.y != 0:  # Normalize diagonal motion
            force = self.move_force * Vec2d.normalized(force)
        if force.x != 0 or force.y != 0:
            self.body.apply_force_at_local_point(force, (0, 0))
            self.moving = True
        else:
            self.moving = False
            self.toggle_sprinting(False)

    def set_cursor_pos(self, position):
        self.cursor_pos = Vec2d(position)

    def flip_yaxis(self, vector):
        return vector.x, (-vector.y + self.screen_dim.y)

    def get_projectiles(self):
        return self.projectiles

    def take_damage(self, attack_power):
        self.health -= attack_power
        self.stats_changed = True
