class Game:
    def __init__(self, main_channel):
        self.players = []  # list of object player
        self.state = 1  # state of the game
        """
        state statues:
        0 not initialized
        1 game initialized
        """
        self.night = 0  # number of night of the game
        self.channels = [0]  # list of object channel
        self.channels[0] = main_channel


class Player:
    def __init__(self, discord_id):
        self.id = discord_id  # discord id of the player
        self.role = "none"  # object role of the player
        self.alive = True


class Channel:
    def __init__(self, location, role_allowed):
        self.location = location  # id of the discord channel
        self.role_allowed = role_allowed  # list of all roles allowed to interact with the channel
