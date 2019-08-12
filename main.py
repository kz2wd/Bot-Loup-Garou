
# All the print are just for the tests and corrections

import discord

import msg
import game
import reactions
import menu

import mytoken


class Bot(discord.Client):
    async def on_ready(self):
        print("{}, {}, is ready".format(self.user.name, self.user.id))
        await client.change_presence(activity=discord.Game(name='!!info'))

    async def on_message(self, message):
        if message.content == "!!info":
            await message.channel.send(msg.info)
        elif message.content == "!!lg":
            if lg_game.state == 0:
                lg_game.__init__(message.channel, 3)
                print("start lg game")
                x = await message.channel.send(msg.start)
                await x.add_reaction(reactions.start)
                await x.add_reaction(reactions.go_forward)

                # lg_game.role_list[0].menu.channel = message.channel
                # await lg_game.role_list[0].menu.display()
                # lg_game.state = lg_game.role_list[0].menu.active_state

        elif message.content == "!!del channel":
            if len(lg_game.channels) > 1 and message.author.id == 250717160521859072:
                for i in range(len(lg_game.channels) - 1):
                    await message.channel.send("Channel deleted")
                    await lg_game.channels[-1].delete()
                    del lg_game.channels[-1]

            else:
                await message.channel.send("Can't delete any channel")
                print(len(lg_game.channels))

    async def on_reaction_add(self, reaction, user):
        if user.id != self.user.id:
            if lg_game.state == 1:
                if reaction.emoji == reactions.start:
                    if len(lg_game.players) < lg_game.max_player:
                        lg_game.players.append(game.Player(user.id))
                        print(", ".join(str(i.discord_id) for i in lg_game.players))
                elif reaction.emoji == reactions.go_forward:
                    if len(lg_game.players) > 0:
                        if user.id == lg_game.players[0].discord_id:
                            lg_game.menu_list.append(menu.Menu(msg.role_list, [lg_game.players[0].discord_id],
                                                               lg_game.channels[0], len(lg_game.players), 2))
                            lg_game.state = 2
                            print("state = 2")
                            await lg_game.menu_list[0].display()
                            await lg_game.menu_list[0].validate()
            elif lg_game.state == 2:
                if reaction.emoji == reactions.go_forward and user.id == lg_game.players[0].discord_id:

                    # check if there is a role for all players
                    check_role = True
                    for i in lg_game.menu_list[0].result_list[0]:
                        if i == -1:
                            check_role = False
                            print("Role missing")

                    # check if there is at least 2 roles from different team
                    check_team = True
                    team_innocent = 0
                    other_team = 0
                    for i in lg_game.menu_list[0].result_list[0]:
                        if 0 == i < 6 or 11 < i < 16:
                            team_innocent += 1
                        else:
                            other_team += 1
                    if team_innocent == 0 or other_team == 0:
                        check_team = False
                        print("Team missing")

                    check_team = True

                    if check_role and check_team:

                        del check_role, check_team, team_innocent, other_team  # free memory

                        lg_game.repartitor()  # mix the role list and attribute them to a player
                        lg_game.set_roles()  # insert roles objects in game object

                        print("roles attributed")
                        print(", ".join("{} : {}".format(i.discord_id, i.role.name) for i in lg_game.players))
                        print("state = 3")

                        lg_game.state = 3

                        await lg_game.channels[0].send(msg.end_of_day)

                        # create channels for roles
                        await lg_game.create_channels_for_roles()

                        # display actions for players
                        await lg_game.play_night()

            for h in lg_game.menu_list:
                if lg_game.state == h.active_state:
                    for i, item_id in enumerate(h.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    number_of_response_not_filled = True
                                    print("reaction found")
                                    for k in range(h.number_of_response):
                                        if number_of_response_not_filled:
                                            if h.result_list[i][k + 1] == -1:
                                                print("operating change")
                                                h.result_list[i][k + 1] = j
                                                print(h.result_list)
                                                number_of_response_not_filled = False

                        """# only for roles
            for h in lg_game.role_list:
                if lg_game.state == h.menu.active_state:
                    for i, item_id in enumerate(h.menu.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    number_of_response_not_filled = True
                                    print("reaction found")
                                    for k in range(h.menu.number_of_response):
                                        if number_of_response_not_filled:
                                            if h.menu.result_list[i][k + 1] == -1:
                                                print("operating change")
                                                h.menu.result_list[i][k + 1] = j
                                                print(h.menu.result_list)
                                                number_of_response_not_filled = False
                            if reaction.emoji == reactions.go_forward:
                                h.menu.active_state = -1
                                print("Choice validated")"""

            for i in lg_game.players:
                if lg_game.state == i.role.menu.active_state:
                    for j, item_id in enumerate(i.role.menu.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for k, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    number_of_response_not_filled = True
                                    print("reaction found")
                                    for l in range(i.role.menu.number_of_response):
                                        if number_of_response_not_filled and i.role.menu.result_list[j][l + 1] == -1:
                                            i.role.menu.result_list[j][l + 1] = k
                                            print(i.role.menu.result_list)
                                            number_of_response_not_filled = False

                            if reaction.emoji == reactions.go_forward:
                                all_ids_selected = True
                                for k in range(len(i.role.menu.allowed_id)):
                                    for l in range(i.role.menu.number_of_response):
                                        if i.role.menu.result_list[k][l + 1] == -1:
                                            all_ids_selected = False
                                if all_ids_selected:
                                    i.role.menu.active_state = -1
                                    await i.role.menu.channel.send("Choix validé")

    async def on_reaction_remove(self, reaction, user):
        if user.id != self.user.id:
            if lg_game.state == 1:
                if reaction.emoji == reactions.start:
                    for i, item_id in enumerate(lg_game.players):
                        if item_id.discord_id == user.id:
                            del lg_game.players[i]
                    print(", ".join(str(i.discord_id) for i in lg_game.players))

            for h in lg_game.menu_list:
                if lg_game.state == h.active_state:
                    for i, item_id in enumerate(h.allowed_id):
                        if user.id == item_id:
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    for k in range(h.number_of_response):
                                        if h.result_list[i][k + 1] == j:
                                            h.result_list[i][k + 1] = -1
                                            print(h.result_list)

            # for role only
            for h in lg_game.role_list:
                if lg_game.state == h.menu.active_state:
                    for i, item_id in enumerate(h.menu.allowed_id):
                        if user.id == item_id:
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    for k in range(h.menu.number_of_response):
                                        if h.menu.result_list[i][k + 1] == j:
                                            h.menu.result_list[i][k + 1] = -1
                                            print(h.menu.result_list)


lg_game = game.Game(0, 3)
lg_game.state = 0

client = Bot()

client.run(mytoken.token)
