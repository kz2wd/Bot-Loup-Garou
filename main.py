import discord

import msg
import game
import menu
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
                lg_game.role_list[0].menu.channel = message.channel
                await lg_game.role_list[0].menu.display()
                lg_game.state = lg_game.role_list[0].menu.active_state
                # await lg_game.role_list[0].menu.get_response()

    async def on_reaction_add(self, reaction, user):
        if user != self:
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
        if user != self:
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
