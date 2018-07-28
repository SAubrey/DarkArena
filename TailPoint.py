import pygame

BLACK = (0, 0, 0)


class TailPoint:
    def __init__(self, renderer, color, width, position):
        self.renderer = renderer
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

    def update(self):
        self.tick += 25
        offset = 35
        if self.tick > 255 - offset:
            self.renderer.remove_tailpoint(self)
            self.color = BLACK
        else:
            #c1 = max(0, min(255, self.tick - 255))
            c2 = max(0, min(255, 255 - self.tick))

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
