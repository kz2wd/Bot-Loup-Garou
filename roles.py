from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from typing import TypeAlias
    Unit: TypeAlias = Callable[[None], None]

    from menu_systems.vote_collector import VoteCollector
    from player import Player


from enum import Enum

import discord

from menu_systems.vote_menu import send_player_vote_menu


class Team(Enum):
    NOBODY = (
        "Dans le plus total des chaos tout le monde est mort")  # used if for example everybody die / lose / leave ?
    WEREWOLF = ("Les loudivers remportent la partie!")
    VILLAGER = ("Les zumains assouvissent leur dominance sur Cludivers!")
    LOVERS = ("Les flêches de cupidon ont attendries le coeur des cludiveriens, l'homosexualité est si forte que la pagaille cesse.")

    def __init__(self, victory_message):
        self._victory_message = victory_message

    @property
    def victory_message(self):
        return self._victory_message


async def on_hunter_die(hunter: Player):
    game = hunter.game

    def filter_hunter(interaction: discord.Interaction):
        if not (player := game.get_player(interaction.user)): return None
        if not (player.role == Role.HUNTER): return None
        return player

    async def send_vote_result(vote_result: VoteCollector):
        vote_result = vote_result.get_single_most()
        if vote_result:
            aimed_player, _ = vote_result
            await game.kill_player(aimed_player, lambda p: f"{p.name} à été fusillé(e) par le chasseur!")
        else:
            await game.channel.send("Le chasseur n'a pu se résoudre à tirer.")

    await send_player_vote_menu(game.channel, game.players, "Le chasseur...",
                                "... pointe son arme!",
                                game.players,
                                filter_hunter, 10, send_vote_result)


class Role(Enum):
    WEREWOLF = ("un Loudivers", Team.WEREWOLF)
    VILLAGER = ("un Zumain", Team.VILLAGER)
    CUPIDON = ("Cupidon", Team.VILLAGER)
    HUNTER = ("le chasseur", Team.VILLAGER, on_hunter_die)
    SEER = ("la voyante", Team.VILLAGER)
    WITCH = ("la sorcière", Team.VILLAGER)

    def __init__(self, name: str, team: Team, on_player_kill=None):
        self._name = name
        self._team = team
        self._on_player_kill = on_player_kill

    @property
    def name(self) -> str:
        return self._name

    @property
    def team(self) -> Team:
        return self._team

    @property
    def on_player_kill(self) -> Callable[[Player], None]:
        return self._on_player_kill
