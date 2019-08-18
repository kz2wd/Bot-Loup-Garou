import discord
import time

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
        self.turn = 0
        self.turn_role = []
        self.is_coupdetat_planned = False
        self.short_time = 20
        self.long_time = 10

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

                    perm = self.lg_perm(lg_counter)

                    lg_channel = await self.channels[0].guild.create_text_channel('Loup Garou', overwrites=perm)
                    i.role.channel.append(lg_channel)
                    self.channels.append(lg_channel)
                else:
                    i.role.channel.append(lg_channel)

    async def play_night(self):

        players_to_watch = []
        players_name = []
        players_eatable = []
        lg = []
        for i in self.players:
            players_name.append(self.channels[0].guild.get_member(i.discord_id).name)

            if i.role.role_id != 6 and i.role.role_id != 7 and i.role.role_id != 8:
                players_eatable.append(i)
            else:
                lg.append(i.discord_id)

        for i, item in enumerate(self.players):
            item.name = players_name[i]

        # turn before lg

        # get players decisions
        for i in self.players:

            if 0 == i.role.role_id:  # if there is cupidon
                if self.night == 0:  # if it is the first night
                    await self.channels[0].send(msg.cupidon_play)
                    i.role.menu = menu.Menu(players_name, [i.discord_id], i.role.channel[0], 2, self.state)
                    await i.role.menu.display()
                    await i.role.menu.validate()

            elif 2 == i.role.role_id:  # if there is voyante

                for j in self.players:
                    if j.role.role_id != 2:
                        players_to_watch.append(j)

                await self.channels[0].send(msg.voyante_play)
                i.role.menu = menu.Menu([i.name for i in players_to_watch], [i.discord_id], i.role.channel[0], 1,
                                        self.state)
                await i.role.menu.display()
                await i.role.menu.validate()

        await self.wait_next_turn(1, self.short_time)

        # processing turn before lg
        for i in self.players:

            if 0 == i.role.role_id and self.night == 0:

                lover_1 = self.players[i.role.menu.result_list[0][1]]
                lover_2 = self.players[i.role.menu.result_list[0][2]]

                lover_1.in_love = [lover_2]
                lover_2.in_love = [lover_1]

                perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        self.channels[0].guild.get_member(lover_1.discord_id):
                            discord.PermissionOverwrite(read_messages=True),
                        self.channels[0].guild.get_member(lover_2.discord_id):
                            discord.PermissionOverwrite(read_messages=True)}

                x = await self.channels[0].guild.create_text_channel('Amoureux', overwrites=perm)

                await x.send("{}, {} et {}, {} êtes désormais amoureux".format(
                    lover_1.name, lover_1.role.name, lover_2.name, lover_2.role.name))

            elif 2 == i.role.role_id and len(players_to_watch) > 0:

                target = players_to_watch[i.role.menu.result_list[0][1]]
                await i.role.channel[0].send("Vous avez observé {}, qui est {}".format(target.name, target.role.name))

        # lg turn
        lg_did_not_played = True
        for i in self.players:

            if 6 == i.role.role_id or 7 == i.role.role_id or 8 == i.role.role_id:
                if lg_did_not_played:
                    lg_did_not_played = False
                    await self.channels[0].send(msg.lg_play)  # lg play
                    players_eatable_names = [i.name for i in players_eatable]

                    i.role.menu = menu.Menu(players_eatable_names, lg, i.role.channel[-1], 1, self.state)
                    await i.role.menu.display()
                    await i.role.menu.validate()

            if 6 == i.role.role_id and i.role.ability == 1:  # if there is loup noir
                await self.channels[0].send(msg.loup_noir_play)
                await i.role.channel[0].send("Voullez vous infecter la victime de ce soir ?")
                i.role.other_menu.append(menu.Menu(["Oui", "Non"], lg, i.role.channel[0], 1, self.state))
                await i.role.other_menu[0].display()
                await i.role.other_menu[0].validate()

        await self.wait_next_turn(2, self.short_time)

        # processing lg turn
        lg_not_processed = True
        for i in self.players:

            if 6 == i.role.role_id or 7 == i.role.role_id or 8 == i.role.role_id and lg_not_processed:
                lg_not_processed = False

                if len(players_eatable) > 0:
                    vote_counter = [0 for i in range(len(players_eatable))]
                    for j in i.role.menu.result_list:
                        vote_counter[j[1]] += 1

                    lg_target = [0, 0]  # list : [number of votes, location]
                    for j, item in enumerate(vote_counter):
                        if lg_target[0] < item:
                            lg_target[0] = item
                            lg_target[1] = j
                        elif lg_target[0] == item and random.randint(0, 1) == 1:
                            lg_target[0] = item
                            lg_target[1] = j

                    self.list_of_dead.append(players_eatable[lg_target[1]])

            if 6 == i.role.role_id and i.role.ability == 1:
                if i.role.other_menu[0].result_list[0][1] == 0:  # if the player want to use his ability
                    i.role.ability = 0
                    self.list_of_dead.remove(players_eatable[lg_target[1]])
                    for j in self.players:
                        if j.discord_id == players_eatable[lg_target[1]].discord_id:
                            j.role = roles.Role(1, 8, "Loup Garou", 0)
                            j.role.channel.append(i.role.channel[0])
                            lg.append(players_eatable[lg_target[1]].discord_id)

                            perm = self.lg_perm(lg)
                            lg_channel = await self.channels[0].guild.edit_channel_permission('Loup Garou',
                                                                                              overwrites=perm)

        #  turn after lg
        for i in self.players:

            if 1 == i.role.role_id and i.role.ability > 0:  # if there is sorciere
                await self.channels[0].send(msg.sorciere_play)

                if len(self.list_of_dead) > 0 and i.role.ability > 2:
                    await i.role.channel[0].send(
                        "Cette nuit {} a été dévoré par les loups\nQue souhaitez vous faire ?".format(
                            self.list_of_dead[0].name))
                    choix_sorciere = ["Ne rien faire", "Soigner {}".format(self.list_of_dead[0].name)] + [
                        "Tuer " + i.name for i in self.players]
                    sorciere_can_heal = True

                elif i.role.ability == 1 or i.role.ability == 3:
                    await i.role.channel[0].send("Personne n'a été tué cette nuit")
                    choix_sorciere = ["Ne rien faire"] + ["Tuer " + i.name for i in self.players]
                    sorciere_can_heal = False

                i.role.menu = menu.Menu(choix_sorciere, [i.discord_id], i.role.channel[0], 1, self.state)
                await i.role.menu.display()
                await i.role.menu.validate()

            elif 4 == i.role.role_id and i.role.ability == 1:  # if there is dictateur
                await self.channels[0].send(msg.dictateur_play)
                choix_dictateur = ["Ne rien faire", "Faire un coup d'état demain"]

                i.role.menu = menu.Menu(choix_dictateur, [i.discord_id], i.role.channel[0], 1, self.state)
                await i.role.menu.display()
                await i.role.menu.validate()

        await self.wait_next_turn(3, self.short_time)

        # processing turn after lg
        for i in self.players:

            if i.role.role_id == 1:
                if i.role.ability > 2:

                    if i.role.menu.result_list[0][1] == 1 and sorciere_can_heal:
                        i.role.ability = 1
                        del self.list_of_dead[0]

                    elif i.role.menu.result_list[0][1] > 1 and sorciere_can_heal:
                        i.role.ability = 2
                        self.list_of_dead.append(self.players[i.role.menu.result_list[0][1] - 2])

                    elif i.role.menu.result_list[0][1] > 0 and sorciere_can_heal == False:
                        i.role.ability = 2
                        self.list_of_dead.append(self.players[i.role.menu.result_list[0][1] - 1])

            if i.role.role_id == 4 and i.role.ability == 1:
                if i.role.menu.result_list == 1:
                    self.is_coupdetat_planned = True
                    i.role.ability = 0

        self.night += 1
        self.turn = 0

    def check_turn(self):

        if self.turn == 0:
            if self.night == 0:
                self.turn_role = [0, 2]
            else:
                self.turn_role = [2]
        elif self.turn == 2:
            self.turn_role = [6, 7, 8]
        else:
            self.turn_role = [1, 4]

        roles_played = True
        for i in self.players:
            for j in self.turn_role:
                if i.role.role_id == j:
                    if i.role.menu.active_state > 0:
                        roles_played = False

        if roles_played:
            self.turn += 1
            print("turn :")
            print(self.turn)

    async def wait_next_turn(self, next_turn, sec):

        time_counter = 0

        while self.turn != next_turn:
            self.check_turn()
            time.sleep(1)
            time_counter += 1

            if time_counter == sec:
                self.turn += 1
                print("end choice time")

                for i in self.players:
                    for j in self.turn_role:
                        if i.role.role_id == j and i.role.menu.active_state > 0:
                            for k in range(len(i.role.menu.allowed_id)):
                                for l in range(i.role.menu.number_of_response):
                                    if i.role.menu.result_list[k][l + 1] == -1:
                                        i.role.menu.result_list[k][l + 1] = random.randint(0, len(i.role.menu.choice))
                                        await i.role.channel[0]. \
                                            send("Vous avez mis trop de temps à choisir. Le hasard a décidé pour vous")

    async def play_morning(self):

        if len(self.list_of_dead) > 0:
            deads = [i.name for i in self.list_of_dead]
            await self.channels[0].send(
                "Le village se réveille sans " + ", ".join(
                    deads[i] + "qui était " + self.list_of_dead[i].role.name for i in range(len(deads))))

            while len(self.list_of_dead) > 0:
                await self.check_lover_death()
                self.kill_players()
                await self.dying_player_action()

        else:
            await self.channels[0].send(msg.day_start)

    async def play_vote(self):

        await self.channels[0].send(msg.vote)

        if len(self.menu_list) == 1:
            self.menu_list.append(menu.Menu([i.name for i in self.players], [i.discord_id for i in self.players],
                                            self.channels[0], 1, self.state))
        else:
            self.menu_list[1] = menu.Menu([i.name for i in self.players], [i.discord_id for i in self.players],
                                          self.channels[0], 1, self.state)

        await self.menu_list[1].display()
        await self.menu_list[1].validate()

        await self.wait_next_turn(1, self.long_time)

        # processing
        vote_result = [0 for i in range(len(self.players))]
        for i in self.menu_list[1].result_list:
            vote_result[i[1]] += 1

        two_equals_values = False
        best_vote = [-1, -1]  # value, location

        for i, value in enumerate(vote_result):

            if value > best_vote[0]:
                two_equals_values = False
                best_vote[0] = value
                best_vote[1] = i

            elif value == best_vote[0]:
                two_equals_values = True

        if two_equals_values == False:
            self.list_of_dead.append(self.players[best_vote[1]])
            await self.channels[0].send("{}, qui était {} ".format(self.players[best_vote[1]].name, self.players[
                best_vote[1]].role.name) + msg.death_mix)
        else:
            await self.channels[0].send("Le village n'a pas pu se décider")

        while len(self.list_of_dead) > 0:
            await self.check_lover_death()
            self.kill_players()
            await self.dying_player_action()

        self.turn = 0

    async def dying_player_action(self):
        # display
        for i in self.list_of_dead:

            if i.role.role_id == 3:
                await self.channels[0].send(
                    "Dans son dernier souffle, le chasseur va choisir s'il fait usage de son arme")
                i.role.menu = menu.Menu(["Ne rien faire"] + [i.name for i in self.players], [i.discord_id],
                                        self.channels[0], 1, self.state)

                await i.role.menu.display()
                await i.role.menu.validate()

            elif i.role.role_id == 5:
                await self.channels[0].send(
                    "Dans son dernier souffle, le fossoyeur va désigner deux personnes de camps opposés")
                i.role.menu = menu.Menu([i.name for i in self.players], [i.discord_id],
                                        self.channels[0], 1, self.state)

                await i.role.menu.display()
                await i.role.menu.validate()

        await self.wait_next_turn(1, self.short_time)

        # processing
        chasseur_shooted = False
        for i in self.list_of_dead:

            if i.role.role_id == 3:
                if i.role.menu.result_list[0][1] > 0:
                    target_of_chasseur = i.role.menu.result_list[0][1] - 1
                    chasseur_shooted = True
                    await self.channels[0].send("{} qui était {} ".format(self.players[target].name, self.players[
                        target].role.name) + msg.death_mix)

            elif i.role.role_id == 5:
                target = i.role.menu.result_list[0][1]
                team = self.players[target].role.team

                enemy_list = []
                if team == 2:
                    for j in self.players:
                        if j.role.team != team:
                            enemy_list.append(j)
                else:
                    for j in self.players:
                        if j.role.team == 2:
                            enemy_list.append(j)
                await self.channels[0].send("{} et {} n'ont pas les crocs de même longueur ..."
                                            .format(self.players[target].name, random.choice(enemy_list).name))

        self.list_of_dead = []
        if chasseur_shooted:
            self.list_of_dead = [self.players[target_of_chasseur]]
        self.turn = 0

    async def check_lover_death(self):
        for i in self.list_of_dead:
            if i.in_love[0] != 0:
                for j in self.players:
                    if j.discord_id == i.in_love[0]:
                        self.list_of_dead.append(j)
                        await self.channels[0].send(
                            "Par chagrin amoureux, {}, qui était {}, rejoint {} dans sa tombe"
                                .format(j.name, j.role.name, i.name))

    def kill_players(self):
        for i in self.players:
            for j in self.list_of_dead:
                if i == j:
                    self.players.remove(i)

    def lg_perm(self, lg_counter):

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
        elif len(lg_counter) == 4:
            perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    self.channels[0].guild.get_member(lg_counter[0]):
                        discord.PermissionOverwrite(read_messages=True),
                    self.channels[0].guild.get_member(lg_counter[1]):
                        discord.PermissionOverwrite(read_messages=True),
                    self.channels[0].guild.get_member(lg_counter[2]):
                        discord.PermissionOverwrite(read_messages=True),
                    self.channels[0].guild.get_member(lg_counter[3]):
                        discord.PermissionOverwrite(read_messages=True)}
            print("4 lg")
        else:
            perm = {self.channels[0].guild.default_role: discord.PermissionOverwrite(read_messages=False)}
            print("Too much lg for this program, consider add more options")

        return perm

    def check_winner(self):
        winner = 0

        team_counter = [0, 0, 0]  # 3 differents teams, change that if you add more teams
        for i in self.players:
            team_counter[i.role.team - 1] += 1
        dead_team_counter = 0
        for i in team_counter:
            if i == 0:
                dead_team_counter += 1

        if dead_team_counter < 2:
            if len(self.players) == 2:
                if self.players[0].in_love[0] == self.players[1].discord_id:
                    winner = 4  # lovers win
        elif dead_team_counter == 2:
            for i, value in enumerate(team_counter):
                if value != 0:
                    winner = i + 1  # id of winning team
        elif dead_team_counter == 3:
            winner = 5  # everybody is dead

        return winner

    async def display_winner(self, winner):
        if winner == 1:
            await self.channels[0].send(msg.lg_win)
        elif winner == 2:
            await self.channels[0].send(msg.innocent_win)
        elif winner == 3:
            await self.channels[0].send(msg.loup_blanc_win)
        elif winner == 4:
            await self.channels[0].send(msg.lovers_win)
        elif winner == 5:
            await self.channels[0].send(msg.nobody_win)


class Player:
    def __init__(self, discord_id):
        self.discord_id = discord_id  # discord id of the player
        self.role = roles.Role(-10, -10, "None", -10)  # object role of the player
        self.alive = True  # is player alive ?
        self.in_love = [0]  # id of player in love with, 0 for none
        self.name = "name"


class Channel:
    def __init__(self, location, role_allowed):
        self.location = location  # id of the discord channel
        self.role_allowed = role_allowed  # list of all roles allowed to interact with the channel
