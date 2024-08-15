from __future__ import annotations

import discord
from discord.ext import commands

import bot_token
import game
from menu_systems.join_game_view import JoinGameView

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

players = []
current_game: game.Game | None = None
join_game_message = None

def on_game_over():
    global current_game
    current_game = None

@bot.command(name="play")
async def start_game(ctx):
    global current_game
    if not current_game:
        current_game = game.Game(ctx, on_game_over)
        view = JoinGameView(current_game)
        join_game_message = await ctx.send("Une nouvelle partie de loup d'hivers commence! Cliquer sur le bouton ci-dessous pour la rejoindre.", view=view)
        view.message = join_game_message


@bot.command(name="end")
async def end_game(ctx):
    global game_started, players, join_game_message, game_starter

    if game_started:
        game_started = False
        players = []
        join_game_message = None
        game_starter = None
        await ctx.send("La partie est terminée.")
    else:
        await ctx.send("Il n'y actuellement aucune partie en cours.")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


bot.run(bot_token.token)
