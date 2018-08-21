from Chaser import Chaser


class EnemyManager(object):
    def __init__(self, game_engine, screen_dim):
        self.ge = game_engine
        self.screen_dim = screen_dim

        self.enemies = []
        self.swords = []
        self.enemy_dict = {}
        self.sword_dict = {}

        self.spawn()

    def spawn(self):
        for i in range(5):
            c = Chaser(self, self.screen_dim)
            self.ge.add_enemy(c)
            self.enemies.append(c)
            self.enemy_dict[c.shape] = c

    def update(self, player_pos):
        for enemy in self.enemies:
            enemy.set_player_position(player_pos)

    def remove_enemy(self, enemy):
        self.enemies.remove(enemy)
        del self.enemy_dict[enemy.shape]
        if enemy.sword is not None:
            self.swords.remove(enemy.sword)


    def add_sword(self, sword):
        self.sword_dict[sword.shape] = sword
        self.swords.append(sword)



