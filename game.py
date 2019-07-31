import roles


class Game:
    def __init__(self, main_channel, number_of_roles):
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
        self.number_of_roles = number_of_roles
        self.role_list = [roles.Role(0, 0, "x") for i in range(number_of_roles)]
        self.max_player = 20


class Player:
    def __init__(self, discord_id):
        self.discord_id = discord_id  # discord id of the player
        self.role = "none"  # object role of the player
        self.alive = True  # is player alive ?
        self.in_love = [0]  # id of player in love with, 0 for none


class Channel:
    def __init__(self, location, role_allowed):
        self.location = location  # id of the discord channel
        self.role_allowed = role_allowed  # list of all roles allowed to interact with the channel
