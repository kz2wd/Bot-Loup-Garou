
import discord

import roles
import random
import msg
import menu


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
        self.role_list = roles.role_list()
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
                i.role = self.role_list[0]
            elif i.role == 1:
                i.role = self.role_list[1]
            elif i.role == 2:
                i.role = self.role_list[2]
            elif i.role == 3:
                i.role = self.role_list[3]
            elif i.role == 4:
                i.role = self.role_list[4]
            elif i.role == 5:
                i.role = self.role_list[5]
            elif i.role == 6:
                i.role = self.role_list[6]
            elif i.role == 7:
                i.role = self.role_list[7]
            elif 7 < i.role < 12:
                i.role = self.role_list[8]
            elif 11 < i.role < 16:
                i.role = self.role_list[9]

    async def create_channels_for_roles(self):

        there_is_no_channel_for_lg = True
        lg_channel = 0

        for i in self.players:
            if i.role.role_id != 8:
                perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        self.channels[0].guild.get_member(i.discord_id):
                            discord.PermissionOverwrite(read_messages=True)}
                x = await self.channels[0].guild.create_text_channel(i.role.name, overwrites=perm)
                i.role.channel.append(x)
                self.channels.append(x)

            if i.role.role_id in [6, 7, 8]:  # list of role that need access to lg channel
                if there_is_no_channel_for_lg:  # create 1 channel for lg
                    there_is_no_channel_for_lg = False
                    lg_counter = []
                    for j in self.players:
                        if j.role.role_id in [6, 7, 8]:  # 2 in ?p
                            lg_counter.append(j.discord_id)
                    print("nb lg : {}".format(len(lg_counter)))

                    if len(lg_counter) == 1:
                        perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                self.channels[0].guild.get_member(lg_counter[0]):
                                    discord.PermissionOverwrite(read_messages=True)}
                        print("1 lg")
                    elif len(lg_counter) == 2:
                        perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                self.channels[0].guild.get_member(lg_counter[0]):
                                    discord.PermissionOverwrite(read_messages=True),
                                self.channels[0].guild.get_member(lg_counter[1]):
                                    discord.PermissionOverwrite(read_messages=True)}
                        print("2 lg")
                    elif len(lg_counter) == 3:
                        perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                self.channels[0].guild.get_member(lg_counter[0]):
                                    discord.PermissionOverwrite(read_messages=True),
                                self.channels[0].guild.get_member(lg_counter[1]):
                                    discord.PermissionOverwrite(read_messages=True),
                                self.channels[0].guild.get_member(lg_counter[2]):
                                    discord.PermissionOverwrite(read_messages=True)}
                        print("3 lg")
                    else:
                        perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False)}

                    lg_channel = await self.channels[0].guild.create_text_channel('Loup Garou', overwrites=perm)
                    i.role.channel.append(lg_channel)
                    self.channels.append(lg_channel)
                else:
                    i.role.channel.append(lg_channel)

    async def play_night(self):

        players_name = []
        players_eatable = []
        lg = []
        for i in self.players:
            players_name.append(self.channels[0].guild.get_member(i.discord_id).name)
            if i.role.role_id != 6 or i.role.role_id != 7 or i.role.role_id != 8:
                players_eatable.append(self.channels[0].guild.get_member(i.discord_id).name)
            else:
                lg.append(i.discord_id)

        # turn before lg
        for i in self.players:
            if 0 == i.role.role_id:  # if there is cupidon
                if self.night == 0:  # if it is the first night
                    await self.channels[0].send(msg.cupidon_play)
                    i.role.menu = menu.Menu(players_name, i.discord_id, i.role.channel[0], 2, self.state)
                    await i.role.menu.display()

            if 2 == i.role.role_id:  # if there is voyante

                players_to_watch = []
                for j in self.players:
                    if j.role.role_id != 2:
                        players_to_watch.append(self.channels[0].guild.get_member(i.discord_id).name)

                await self.channels[0].send(msg.voyante_play)
                i.role.menu = menu.Menu(players_to_watch, i.discord_id, i.role.channel[0], 1, self.state)
                await i.role.menu.display()

        # lg turn
        lg_did_not_played = True
        for i in self.players:
            if 6 == i.role.role_id or 7 == i.role.role_id or 8 == i.role.role_id and lg_did_not_played:
                lg_did_not_played = False
                await self.channels[0].send(msg.lg_play)  # lg play
                i.role.menu = menu.Menu(players_eatable, lg, i.role.channel[-1], 1, self.state)
                await i.role.menu.display()

            if 6 == i.role.role_id and i.role.ability == 1:  # if there is loup noir
                await self.channels[0].send(msg.loup_noir_play)
                await i.role.channel[0].send("Voullez vous infecter la victime de ce soir ?")
                i.role.menu = menu.Menu(["Oui", "Non"], lg, i.role.channel[0], 1, self.state)
                await i.role.menu.display()

        #  turn after lg
        for i in self.players:

            if 1 == i.role.role_id and i.role.ability > 0:  # if there is sorciere
                await self.channels[0].send(msg.sorciere_play)

            if 4 == i.role.role_id:  # if there is dictateur
                await self.channels[0].send(msg.dictateur_play)

        self.night += 1


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
