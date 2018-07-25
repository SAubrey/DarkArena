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


class Event(object):
    def __init__(self):
        self.name = "Generic Event"

    def __str__(self):
        return self.name


class EventManager:
    def __init__(self):
        self.listeners = Wkd()

    def add_listener(self, listener, name):
        self.listeners[name] = listener

    def remove_listener(self, listener):
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event):
        if event.name != EV_TICK and event.name != EV_PLAYER_MOVE:
            pass
            #print(type(event))

        try:
            # All listeners
            if event.name == EV_TICK or \
                    event.name == EV_QUIT or \
                    event.name == EV_INIT or \
                    event.name == EV_RESIZE:
                for val in self.listeners.values():
                    val.notify(event)
            # Game Engine only
            elif event.name == EV_INPUT or event.name == EV_MOUSE_MOVE or event.name == EV_MOUSE_CLICK:
                self.listeners["Game Engine"].notify(event)
            # Renderer only
            elif event.name == EV_PLAYER_MOVE or event.name == EV_PLAYER_STATS or event.name == EV_MODEL_SHARE:
                self.listeners["Renderer"].notify(event)

        except KeyError as ke:
            print("Error:", ke.message)


class TickEvent(Event):
    def __init__(self):
        super(TickEvent, self).__init__()
        self.name = EV_TICK


class QuitEvent(Event):
    def __init__(self):
        super(QuitEvent, self).__init__()
        self.name = EV_QUIT


class InputEvent(Event):
    def __init__(self, key, down_press):
        super(InputEvent, self).__init__()
        self.name = EV_INPUT
        self.key = key
        self.down_press = down_press


class InitializeEvent(Event):
    def __init__(self):
        self.name = EV_INIT


class PlayerMoveEvent(Event):
    def __init__(self, position):
        self.name = EV_PLAYER_MOVE
        self.position = position


class MouseMoveEvent(Event):
    def __init__(self, position):
        self.name = EV_MOUSE_MOVE
        self.position = position


class NewGroupEvent(Event):
    def __init__(self, group):
        self.name = EV_NEW_GROUP
        self.group = group


class ScreenSizeEvent(Event):
    def __init__(self, dim):
        self.name = EV_RESIZE
        self.screen_dim = dim
        self.width = dim[0]
        self.height = dim[1]


class PlayerStatUpdate(Event):
    def __init__(self, health, stamina, mana):
        self.name = EV_PLAYER_STATS
        self.health = health
        self.stamina = stamina
        self.mana = mana


class MouseClickEvent(Event):
    def __init__(self, position, button):
        self.name = EV_MOUSE_CLICK
        self.position = position
        self.button = button

class ModelShareEvent(Event):
    def __init__(self, space, all_sprites):
        self.name = EV_MODEL_SHARE
        self.space = space
        self.all_sprites = all_sprites
