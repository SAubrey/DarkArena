from weakref import WeakValueDictionary as Wkd


EV_INIT = 1
EV_QUIT = 2
EV_TICK = 3
EV_INPUT = 4
EV_PLAYER_MOVE = 5
EV_MOUSE_MOVE = 6
EV_RESIZE = 7
EV_NEW_GROUP = 8
EV_PLAYER_STATS = 9
EV_MOUSE_CLICK = 10
EV_MODEL_SHARE = 11
EV_SWORD_SWING = 12


class Event(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class EventManager(object):
    def __init__(self):
        self.listeners = Wkd()

    def add_listener(self, listener, name):
        self.listeners[name] = listener

    def remove_listener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        en = event.name
        # if event.name != EV_TICK and event.name != EV_PLAYER_MOVE:
        #     pass
            #print(type(event))
        try:
            # All listeners
            if en == EV_TICK or \
                    en == EV_QUIT or \
                    en == EV_INIT or \
                    en == EV_RESIZE:
                for val in self.listeners.values():
                    val.notify(event)
            # Game Engine only
            elif en == EV_INPUT or en == EV_MOUSE_MOVE or en == EV_MOUSE_CLICK:
                self.listeners["Game Engine"].notify(event)
            # Renderer only
            elif en == EV_PLAYER_MOVE or \
                    en == EV_PLAYER_STATS or \
                    en == EV_MODEL_SHARE or \
                    en == EV_SWORD_SWING:
                self.listeners["Renderer"].notify(event)

        except KeyError as ke:
            print("Error:", ke.message)


class TickEvent(Event):
    def __init__(self):
        super(TickEvent, self).__init__(EV_TICK)


class QuitEvent(Event):
    def __init__(self):
        super(QuitEvent, self).__init__(EV_QUIT)


class InputEvent(Event):
    def __init__(self, key, down_press, cursor_pos=None):
        super(InputEvent, self).__init__(EV_INPUT)
        self.key = key
        self.down_press = down_press
        self.cursor_pos = cursor_pos


class InitializeEvent(Event):
    def __init__(self):
        super(InitializeEvent, self).__init__(EV_INIT)


class PlayerMoveEvent(Event):
    def __init__(self, position):
        super(PlayerMoveEvent, self).__init__(EV_PLAYER_MOVE)
        self.position = position


class MouseMoveEvent(Event):
    def __init__(self, position):
        super(MouseMoveEvent, self).__init__(EV_MOUSE_MOVE)
        self.position = position


class NewGroupEvent(Event):
    def __init__(self, group):
        super(NewGroupEvent, self).__init__(EV_NEW_GROUP)
        self.group = group


class ScreenSizeEvent(Event):
    def __init__(self, dim):
        super(ScreenSizeEvent, self).__init__(EV_RESIZE)
        self.screen_dim = dim
        self.width = dim[0]
        self.height = dim[1]


class PlayerStatUpdate(Event):
    def __init__(self, health, stamina, mana):
        super(PlayerStatUpdate, self).__init__(EV_PLAYER_STATS)
        self.health = health
        self.stamina = stamina
        self.mana = mana


class MouseClickEvent(Event):
    def __init__(self, position, button, down_press):
        super(MouseClickEvent, self).__init__(EV_MOUSE_CLICK)
        self.position = position
        self.button = button
        self.down_press = down_press


class ModelShareEvent(Event):
    def __init__(self, space, all_sprites, player_sword, enemy_swords):
        super(ModelShareEvent, self).__init__(EV_MODEL_SHARE)
        self.space = space
        self.all_sprites = all_sprites
        self.player_sword = player_sword
        self.enemy_swords = enemy_swords


# class SwordSwing(Event):
#     def __init__(self, sword):
#         super(SwordSwing, self).__init__(EV_SWORD_SWING)
#         self.sword = sword
