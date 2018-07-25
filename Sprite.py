import pygame


class Sprite(pygame.sprite.DirtySprite):
    def __init__(self, game_engine, color, width, height):
        pygame.sprite.DirtySprite.__init__(self)
        self.ge = game_engine

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.color = color
        self.width = width
        self.height = height

    def update(self):
        pass