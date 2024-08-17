from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Awaitable

if TYPE_CHECKING:
    from game import Game

from roles import Role, Team

import discord
from unittest.mock import Mock


class Player:
    def __init__(self, user: discord.User, game: Game):
        self.user: discord.user = user
        self.role: Role | None = None
        self.game: Game = game
        self.name: str = m.display_name if (m := game.channel.guild.get_member(user.id)) else user.name
        self.on_player_kill: list[Callable[[], Awaitable[None]]] = []  # Warning : if the function blocks the execution, game will be broken.
        self.is_in_love = False

    def assign_role(self, role: Role):
        self.role = role
        if self.role.on_player_kill:
            self.on_player_kill.append(lambda: self.role.on_player_kill(self))

    def reveal_role(self) -> str:
        role_msg = f"Vous êtes {self.role.name}!"

        if self.role == Role.WEREWOLF:
            other_wolves = self.game.get_players_of_team(Team.WEREWOLF)
            other_wolves = [player for player in other_wolves if player != self]
            if len(other_wolves) == 0:
                role_msg += "\nVous êtes un loup solitaire."
            else:
                role_msg += "\nLes autres loups sont " + ", ".join(p.name for p in other_wolves)

        return role_msg


class FakePlayer(Player):
    id = 123456789

    def __init__(self, name, game):
        mock_user = Mock(spec=discord.User)
        mock_user.id = FakePlayer.id
        FakePlayer.id += 1
        mock_user.name = "fake_" + name
        mock_user.display_name = name

        super().__init__(mock_user, game)