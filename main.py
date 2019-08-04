import discord

import msg
import game
import reactions
import menu
import roles

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
                            lg_game.menu_list.append(menu.Menu(msg.role_list, [lg_game.players[0].discord_id]
                                                               , lg_game.channels[0], len(lg_game.players), 2))
                            lg_game.state = 2
                            print("state = 2")
                            await lg_game.menu_list[0].display()
                            await lg_game.menu_list[0].validate()
            elif lg_game.state == 2:
                if reaction.emoji == reactions.go_forward and user.id == lg_game.players[0].discord_id:
                    check = True
                    for i in lg_game.menu_list[0].result_list[0]:
                        if i == -1:
                            check = False
                    if check:
                        lg_game.repartitor()

                        print("roles attributed")
                        print(", ".join("{} : {}".format(i.discord_id, i.role) for i in lg_game.players))
                        lg_game.state = 3
                        print("state = 3")
                        await lg_game.channels[0].send(msg.end_of_day)

            for h in lg_game.menu_list:
                if lg_game.state == h.active_state:
                    for i, item_id in enumerate(h.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    check = True
                                    print("reaction found")
                                    for k in range(h.number_of_response):
                                        if check:
                                            if h.result_list[i][k + 1] == -1:
                                                print("operating change")
                                                h.result_list[i][k + 1] = j
                                                print(h.result_list)
                                                check = False

            # only for roles
            for h in lg_game.role_list:
                if lg_game.state == h.menu.active_state:
                    for i, item_id in enumerate(h.menu.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    check = True
                                    print("reaction found")
                                    for k in range(h.menu.number_of_response):
                                        if check:
                                            if h.menu.result_list[i][k + 1] == -1:
                                                print("operating change")
                                                h.menu.result_list[i][k + 1] = j
                                                print(h.menu.result_list)
                                                check = False

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
