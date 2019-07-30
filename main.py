import discord

import msg
import game
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
                lg_game.__init__(message.channel)
                print("start lg game")
                m = menu.Menu([i for i in range(10)], [250717160521859072], lg_game.channels[0])
                await m.display()

    async def on_reaction_add(self, reaction, user):
        print("yes")

    async def on_reaction_remove(self, reaction, user):
        print("yes")


lg_game = game.Game(0)
lg_game.state = 0

client = Bot()

client.run(mytoken.token)
