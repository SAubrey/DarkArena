from Sprite import Sprite
import pymunk
import random

RED = (255, 50, 50)
WIDTH, HEIGHT = 15, 15


class Enemy(Sprite):
    def __init__(self, game_engine, screen_dim):
        super(Enemy, self).__init__(game_engine, RED, WIDTH, HEIGHT)
        self.screen_dim = screen_dim
        self.mass = 1
        self.radius = WIDTH / 2
        start_posx = int(max(10, self.screen_dim[0] / 2))
        start_posy = int(max(10, self.screen_dim[1] / 2))

        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        self.body = pymunk.Body(self.mass, moment)
        self.body.position = (start_posx, start_posy)

        shape = pymunk.Circle(self.body, self.radius)  # Collision shape
        shape.elasticity = 0.3

        self.rect.x = start_posx
        self.rect.y = start_posy
        self.ge.add_body(self.body, shape)

    def update(self):
        self.dirty = 1
        # print(self.body.position)
        fx = random.randint(-1000, 1000)
        fy = random.randint(-1000, 1000)
        self.body.apply_force_at_local_point((fx, fy), (0, 0))
        self.rect.x = self.body.position.x  # rect is sprite position
        self.rect.y = self.body.position.y

        # Let renderer only worry about drawing sprites, and update sprite data here
