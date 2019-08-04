import roles
import random


class Game:
    def __init__(self, main_channel, number_of_roles):
        self.players = []  # list of object player
        self.state = 1  # state of the game
        """
        state statues:
        0 not initialized
        1 game initialized
        2 role selection
        """
        self.night = 0  # number of night of the game
        self.channels = [0]  # list of object channel
        self.channels[0] = main_channel
        self.number_of_roles = number_of_roles
        self.role_list = [roles.Role(0, 0, "x") for i in range(number_of_roles)]
        self.max_player = 26
        self.list_of_dead = []
        self.menu_list = []

    def repartitor(self):
        print(self.menu_list[0].result_list)
        del self.menu_list[0].result_list[0][0]
        random.shuffle(self.menu_list[0].result_list[0])
        for i, item in enumerate(self.players):
            item.role = self.menu_list[0].result_list[0][i]
        return self.players

    def set_roles(self):
        for i in self.players:
            if i.role == 0:
                i.role = roles.cupidon
            elif i.role == 1:
                i.role = roles.sorciere
            elif i.role == 2:
                i.role = roles.voyante
            elif i.role == 3:
                i.role = roles.chasseur
            elif i.role == 4:
                i.role = roles.dictateur
            elif i.role == 5:
                i.role = roles.fossoyeur
            elif i.role == 6:
                i.role = roles.loup_noir
            elif i.role == 7:
                i.role = roles.loup_blanc
            elif 7 < i.role < 12:
                i.role = roles.loup
            elif 11 < i.role < 16:
                i.role = roles.villageois



class Player:
    def __init__(self, discord_id):
        self.discord_id = discord_id  # discord id of the player
        self.role = -1  # object role of the player
        self.alive = True  # is player alive ?
        self.in_love = [0]  # id of player in love with, 0 for none


class Channel:
    def __init__(self, location, role_allowed):
        self.location = location  # id of the discord channel
        self.role_allowed = role_allowed  # list of all roles allowed to interact with the channel
