import random

import discord

from game_phases import GamePhase
from menu_systems.menus import send_menu
from menu_systems.vote_collector import VoteCollector
from menu_systems.vote_menu import send_player_vote_menu
from player import Player, FakePlayer
from roles import Role, Team


class Game:

    def __init__(self, channel: discord.TextChannel, on_game_over):
        self.phases = [GamePhase.WEREWOLVES_TURN, GamePhase.VILLAGE_WAKING_UP, GamePhase.VILLAGERS_VOTE]
        self.channel: discord.TextChannel = channel
        # Define player after the channel is known
        self.owner: Player | None = None
        self.players: list[Player] = [FakePlayer("P1", self)]
        self.on_game_over = on_game_over
        self.on_death_list: list[Player] = []
        self.current_phase_index = 0

    def set_owner(self, owner: discord.User):
        self.owner = Player(owner, self)
        self.players.append(self.owner)

    def add_player(self, user: discord.User):
        self.players.append(Player(user, self))

    def is_player_registered(self, user: discord.User):
        return any(player.user == user for player in self.players)

    def get_player(self, user: discord.user) -> Player | None:
        res = [player for player in self.players if player.user == user]
        if len(res) == 1:
            return res[0]
        return None

    def get_players_of_team(self, team) -> list[Player]:
        return [player for player in self.players if player.role.team == team]

    def get_winning_team(self) -> Team | None:
        if len(self.players) == 0: return Team.NOBODY
        teams = {player.role.team for player in self.players}
        if len(teams) == 1: return teams.pop()
        return None

    async def clear_death_list(self):
        if not self.on_death_list:
            await self.channel.send("Personne n'est mort cette nuit!")
            return
        random.shuffle(self.on_death_list)
        for player in self.on_death_list:
            await self.kill_player(player)
        self.on_death_list = []

    def schedule_kill_player(self, player: Player):
        self.on_death_list.append(player)

    async def kill_player(self, player: Player, kill_message: callable = lambda player: f"{player.name} est mort."):
        await self.channel.send(kill_message(player))
        self.players.remove(player)
        if player.on_player_kill is not None:
            player.on_player_kill()

    async def handle_victory(self, continue_game: callable):
        winner = self.get_winning_team()
        if winner is None:
            await continue_game()
            return
        await self.channel.send(f"La partie est terminée!\n\n{winner.victory_message}")
        self.on_game_over()

    async def start(self):
        num_players = len(self.players)
        num_werewolves = max(1, num_players // 3)

        roles = [Role.WEREWOLF] * num_werewolves + [Role.VILLAGER] * (num_players - num_werewolves)
        random.shuffle(roles)

        for p, role in zip(self.players, roles):
            p.assign_role(role)

        async def role_reveal_button(interaction: discord.Interaction):
            if not (player := self.get_player(interaction.user)): return
            await interaction.response.send_message(player.reveal_role(), ephemeral=True)

        await send_menu(self.channel, "Cliquer pour réveler votre rôle", 'Réveler votre rôle!', role_reveal_button)

        await self.play_phase_and_go_to_next()

    async def play_phase_and_go_to_next(self):
        phase_to_play = self.current_phase_index
        print(f"Playing phase {phase_to_play}")
        self.current_phase_index = (self.current_phase_index + 1) % len(self.phases)

        await self.phases[phase_to_play].execute(self, self.play_phase_and_go_to_next)

