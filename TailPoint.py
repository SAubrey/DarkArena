import pygame
from pymunk.vec2d import Vec2d

BLACK = (0, 0, 0)
BRIGHTEST = 255


class TailPoint:
    def __init__(self, tail_drawer, color, width, position):
        self.tail_drawer = tail_drawer
        self.width = width
        self.position = position
        self.image = pygame.Surface([width, width])
        self.image.fill(color)
        #self.image.set_alpha(10)  # 0 = transparent
        self.image.set_colorkey(BLACK)  # Makes black transparent

        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.tick = 0
        self.color = color

    # Tail Sprites get darker every tick.
    def update(self):
        self.tick += 25
        offset = 35
        if self.tick > BRIGHTEST - offset:
            self.tail_drawer.remove_tailpoint(self)
            self.color = BLACK
        else:
            #c1 = max(0, min(255, self.tick - 255))
            c2 = max(0, min(BRIGHTEST, BRIGHTEST - self.tick))

            if c2 < 100:
                self.color = BLACK
            else:
                self.color = (c2, c2, c2)
        self.image.fill(self.color)

    def get_color(self):
        return self.color

    def get_rect(self):
        return self.rect

    def get_radius(self):
        return self.width / 2


class TailDrawer(object):
    def __init__(self, renderer):
        self.re = renderer
        self.screen = self.re.screen
        self.tail_sprites = []
        self.tail_rects = []
        self.old_rects = []
        self.tail_skip_counter = 0
        self.tail_skip_thresh = 1
        self.tail_width = 13

    def draw(self, last_pos, current_pos):
        append = self.tail_rects.append
        # Clear and re-fill tail Rects (updates color)
        del self.tail_rects[:]
        for s in self.tail_sprites:
            s.update()
            pos = s.get_rect().x + s.get_radius(), s.get_rect().y + s.get_radius()
            append(pygame.draw.circle(self.screen, s.get_color(), pos, s.get_radius(), 0))

        self.draw_player_tail(last_pos, current_pos)
        self.clear_old_rects()

    def clear_old_rects(self):
        blit = self.screen.blit
        # Replace old tail pixels with background
        for a in self.old_rects:
            blit(self.re.background, a, a)
        del self.old_rects[:]

    def draw_player_tail(self, last_pos, current_pos):
        self.tail_skip_counter += 1
        if self.tail_skip_counter >= self.tail_skip_thresh and \
                self.difference_between_points(last_pos, current_pos) > 2:
            self.draw_line_between(last_pos, current_pos, self.tail_width)
            self.tail_skip_counter = 0

    def difference_between_points(self, p1, p2):
        p1, p2 = Vec2d(p1), Vec2d(p2)
        return abs(p1.x - p2.x) + abs(p1.y - p2.y)

    def draw_line_between(self, p1, p2, width):
        color = (0, 0, 255)

        dx = int(p1[0] - p2[0])
        dy = int(p1[1] - p2[1])
        iterations = max(abs(dx), abs(dy))

        for i in range(iterations):
            progress = 1.0 * i / iterations
            aprogress = 1 - progress
            x = int(aprogress * p1[0] + progress * p2[0])
            y = int(aprogress * p1[1] + progress * p2[1])
            if i % 2 == 0:
                tp = TailPoint(self, color, width, (x, y))
                self.tail_sprites.append(tp)

    def remove_tailpoint(self, tp):
        self.old_rects.append(tp.get_rect())
        self.tail_sprites.remove(tp)

    def get_tail_rects(self):
        return self.tail_rects
