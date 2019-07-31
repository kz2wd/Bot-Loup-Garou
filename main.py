import discord

import msg
import game
import reactions

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

            for h in range(len(lg_game.role_list)):
                if lg_game.state == lg_game.role_list[h].menu.active_state:
                    for i, item_id in enumerate(lg_game.role_list[h].menu.allowed_id):
                        if user.id == item_id:
                            print("id allowed")
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    check = True
                                    print("reaction found")
                                    for k in range(lg_game.role_list[h].menu.number_of_response):
                                        if check:
                                            if lg_game.role_list[h].menu.result_list[i][k + 1] == -1:
                                                print("operating change")
                                                lg_game.role_list[h].menu.result_list[i][k + 1] = j
                                                print(lg_game.role_list[h].menu.result_list)
                                                check = False

    async def on_reaction_remove(self, reaction, user):
        if user.id != self.user.id:
            if lg_game.state == 1:
                if reaction.emoji == reactions.start:
                    for i, item_id in enumerate(lg_game.players):
                        if item_id.discord_id == user.id:
                            del lg_game.players[i]
                    print(", ".join(str(i.discord_id) for i in lg_game.players))

            for h in range(len(lg_game.role_list)):
                if lg_game.state == lg_game.role_list[h].menu.active_state:
                    for i, item_id in enumerate(lg_game.role_list[h].menu.allowed_id):
                        if user.id == item_id:
                            for j, item in enumerate(reactions.menu):
                                if item == reaction.emoji:
                                    for k in range(lg_game.role_list[h].menu.number_of_response):
                                        if lg_game.role_list[h].menu.result_list[i][k + 1] == j:
                                            lg_game.role_list[h].menu.result_list[i][k + 1] = -1
                                            print(lg_game.role_list[h].menu.result_list)


lg_game = game.Game(0, 3)
lg_game.state = 0

client = Bot()

client.run(mytoken.token)
