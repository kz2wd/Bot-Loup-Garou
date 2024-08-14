from __future__ import annotations

import operator

import discord
from discord import Member
from discord.ext import commands, tasks
from enum import Enum, auto
import random
import threading
import asyncio

import bot_token


class Team(Enum):
    WEREWOLF = auto()
    VILLAGER = auto()

class Role(Enum):
    WEREWOLF = ("Loup Garou", Team.WEREWOLF)
    VILLAGER = ("Villageois", Team.VILLAGER)

    def __init__(self, name, team):
        self._name = name
        self._team = team

    @property
    def name(self):
        return self._name

    @property
    def team(self):
        return self._team


class Player:
    def __init__(self, user: discord.User, game: Game):
        self.user: discord.user = user
        self.role: Role = None
        self.game: Game = game
        self.name: str = m.display_name if (m := game.channel.guild.get_member(user.id)) else user.name

    def assign_role(self, role: Role):
        self.role = role


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

players = []
current_game : None | Game = None
join_game_message = None


class Game:
    def __init__(self, owner: discord.User, channel: discord.TextChannel):

        self.channel: discord.TextChannel = channel
        # Define player after the channel is known
        self.owner: Player = Player(owner, self)
        self.players: list[Player] = [self.owner]

    def add_player(self, user: discord.User):
        self.players.append(Player(user, self))

    def is_player_registered(self, user: discord.User):
        return any(player.user == user for player in self.players)

    def get_player(self, user: discord.user) -> Player | None :
        res = [player for player in self.players if player.user == user]
        if len(res) == 1 :
            return res[0]
        return None

    async def start(self):
        num_players = len(self.players)
        num_werewolves = max(1, num_players // 3)

        roles = [Role.WEREWOLF] * num_werewolves + [Role.VILLAGER] * (num_players - num_werewolves)
        random.shuffle(roles)

        for p, role in zip(self.players, roles):
            p.assign_role(role)

        async def role_reveal_button(interaction: discord.Interaction):
            if not (player := self.get_player(interaction.user)): return
            await interaction.response.send_message(f"Rôle : {player.role.name}", ephemeral=True)

        await send_menu(self.channel, "Cliquer pour réveler votre rôle", 'Réveler votre rôle!', role_reveal_button)

        werewolves_targets = [player for player in self.players] # if player.role.team != Team.WEREWOLF
        werewolf_votes = VoteCollector(werewolves_targets, [player for player in self.players if player.role.team == Team.WEREWOLF])

        async def send_vote_result():
            vote_result = werewolf_votes.get_single_most()
            if vote_result:
                player, amount = vote_result
                msg = f"Joueur éliminé par les loups d'hivers : ${player.name}!"
            else:
                msg = f"Les loups d'hivers n'ont pas pu se décider cette nuit!"
            await self.channel.send(msg)

        view = TimedSelectView(timeout=10, on_time_over=send_vote_result)

        def werewolf_select_player(selected_player: Player) -> callable:
            async def werewolf_select(interaction: discord.Interaction):
                if not (player := self.get_player(interaction.user)): return
                if not (player.role == Role.WEREWOLF): return
                await interaction.response.send_message(f"Vous avez voté pour : {selected_player.name}", ephemeral=True)
                everybody_voted = werewolf_votes.add_vote(selected_player, player)
                if everybody_voted:
                    await view.end()

            return werewolf_select

        await send_selection_menu(self.channel, "Les loups d'hivers...", "...choisissent leur cible!", [(player.name, werewolf_select_player(player)) for player in werewolves_targets], view)

        # await send_menu("Cliquer pour réveler votre rôle", 'Réveler votre rôle!', role_reveal_button)


class VoteCollector:
    def __init__(self, options, voters: list[Player]):
        self.options = {opt: 0 for opt in options}
        self.mutex = threading.Lock()
        self.allowed_voters = voters
        self.has_voted: set[Player] = set()
        self.expected_votes = len(voters)

    # CONSIDER THAT VOTER is included in the voters list!
    # Returns True if all voters have voted
    def add_vote(self, option, voter: Player) -> bool:
        with self.mutex:
            try:
                self.options[option] += 1
                self.expected_votes -= 0 if voter in self.has_voted else 1
                self.has_voted.add(voter)
            except KeyError as ignored:
                pass
        return self.expected_votes == 0

    def get_single_most(self) -> tuple(any, int) | None:
        max_votes = max(self.options.items(), key=operator.getitem(1))
        most_voted = [(choice, amount) for (choice, amount) in self.options.items() if amount == max_votes]
        if len(most_voted) == 1:
            return most_voted[0]


class TimedSelectView(discord.ui.View):
    def __init__(self, timeout: int, on_time_over: callable):
        super().__init__()
        self.timeout = timeout
        self.on_time_over = on_time_over
        self.timer_task = None  # Task reference for the timer
        self.message = None

        # Start the timer
        self.start_timer()

    def start_timer(self):
        # Start a background task to handle the timer
        self.timer_task = asyncio.create_task(self.update_timer())

    async def update_timer(self):
        while self.timeout > 0:
            await asyncio.sleep(1)
            self.timeout -= 1
            # Update the message with the remaining time
            if self.message:
                await self.message.edit(content=f"{self.message.content} \nTemps restant: {self.timeout} seconds")

        await self.end()

    async def end(self):
        if self.timer_task:
            self.timer_task.cancel()  # Cancel the timer task
            self.timer_task = None
            if self.message:
                await self.message.edit(content=f"{self.message.content} \nVote fini")

        try:
            await self.on_time_over()
        except TypeError as ignored:
            pass # Idk why it happens, and I don't care because it crashes when on_time_over has already been triggered one time, which is plenty enough!


async def send_menu(channel, name: str, action_name: str, action):
    view = discord.ui.View()
    it = discord.ui.Button(label=action_name)
    it.callback = action
    view.add_item(it)
    await channel.send(name, view=view)


async def send_selection_menu(channel, name: str, placeholder: str, options: list[tuple[str, callable]], view: TimedSelectView):
    select = discord.ui.Select(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=[discord.SelectOption(label=option[0]) for option in options]
        )

    async def select_callback(interaction: discord.Interaction):
        # Find the selected option's corresponding callable and execute it
        selected_option = next(opt for opt in options if opt[0] == select.values[0])
        await selected_option[1](interaction)  # Execute the callable

    # Set the callback for the select menu
    select.callback = select_callback

    view.add_item(select)

    # Send the message with the select menu
    message = await channel.send(content=name, view=view)
    view.message = message


class JoinGameView(discord.ui.View):
    @discord.ui.button(label="Rejoindre la partie", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global join_game_message, current_game
        game = current_game
        user = interaction.user
        if game:
            if not game.is_player_registered(user):
                game.add_player(user)
                await interaction.response.send_message(f"Vous avez rejoint la partie!", ephemeral=True)
                await join_game_message.edit(content=f"Joueurs: {', '.join(str(p.user.name) for p in game.players)}", view=self)

            else:
                pass
                # await interaction.response.send_message("You've already joined the game!", ephemeral=True)
        else:
            game = current_game = Game(user, interaction.channel)
            await interaction.response.send_message(f"Vous avez rejoint la partie!", ephemeral=True)

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.primary)
    async def start_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global current_game
        if interaction.user == current_game.owner.user:
            await interaction.response.send_message("La partie commence!", ephemeral=False)
            await current_game.start()
        else:
            await interaction.response.send_message("Seul l'hôte peut démarrer la partie!", ephemeral=True)


@bot.command(name="play")
async def start_game(ctx):
    global current_game, join_game_message
    if not current_game:
        view = JoinGameView()
        join_game_message = await ctx.send("Une nouvelle partie de loup d'hivers commence! Cliquer sur le bouton ci-dessous pour la rejoindre.", view=view)


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
