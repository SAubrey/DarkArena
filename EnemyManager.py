

class EnemyManager(object):
    def __init__(self, game_engine):
        self.ge = game_engine
        self.spawn()

    def spawn(self):
        for i in range(10):
            self.ge.create_enemy()

    def update(self):
        pass
