from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player
    from menu_systems.vote_collector import VoteCollector

from roles import Team, Role
from enum import Enum, auto

import discord


from menu_systems.vote_menu import send_player_vote_menu
from menu_systems.menus import send_menu


class GamePhase(Enum):
    WEREWOLVES_TURN = auto()
    VILLAGE_WAKING_UP = auto()
    VILLAGERS_VOTE = auto()
    CUPIDON_TURN = auto()
    SEER_TURN = auto()
    WITCH_TURN = auto()

    async def execute(self, game, on_continue):
        match self:
            case GamePhase.WEREWOLVES_TURN:
                print("Werewolves hunting")
                werewolves = [player for player in game.players if player.role.team == Team.WEREWOLF]
                if not werewolves:
                    print("Continuing")
                    await on_continue()

                async def send_vote_result(vote_result: VoteCollector):
                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        await game.channel.send("Les loudivers se sont régalés ...")
                        player, _ = vote_result
                        game.schedule_kill_player(player)
                    else:
                        await game.channel.send("Les loudivers n'ont pas pu se décider cette nuit!")

                    print("Continuing")
                    await on_continue()

                werewolves_targets = [player for player in game.players]  # if player.role.team != Team.WEREWOLF

                def filter_werewolf(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.WEREWOLF): return None
                    return player

                await send_player_vote_menu(game.channel, game.players, "Les loudivers...",
                                            "...choisissent leur cible!",
                                            werewolves_targets,
                                            filter_werewolf, 10, send_vote_result)

            case GamePhase.VILLAGE_WAKING_UP:
                print("Waking up!")
                await game.channel.send("Cludivers se réveille!")
                await game.clear_death_list()
                await game.handle_victory(on_continue)

            case GamePhase.VILLAGERS_VOTE:
                print("Villagers voting")

                def filter_player(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    return player

                async def send_vote_result(vote_result: VoteCollector):
                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        await game.channel.send("Les zumains ont fait leur choix!")
                        player, _ = vote_result
                        await game.kill_player(player)
                    else:
                        await game.channel.send("Les zumains n'ont pas réussi à choisir!")

                    await game.handle_victory(on_continue)

                await send_player_vote_menu(game.channel, game.players, "Les villageois...",
                                            "...choisissent un coupable!",
                                            game.players,
                                            filter_player, 10, send_vote_result)

            case GamePhase.CUPIDON_TURN:
                print("Cupidon choosing")

                def filter_cupidon(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.CUPIDON): return None
                    return player

                async def send_vote_result(vote_result: VoteCollector):

                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        looked_player, _ = vote_result

                    chosen_lovers = []
                    async def kill_lovers():
                        for l in chosen_lovers:
                            game.kill_player(l, lambda p: f"{p.name} s'est donné la mort par amour.")

                    for lover in chosen_lovers:
                        lover.on_player_kill.insert(0, kill_lovers)

                    await on_continue()

                await send_player_vote_menu(game.channel, game.players, "La voyante...",
                                            "... choisit qui observer!",
                                            game.players,
                                            filter_cupidon, 10, send_vote_result)

            case GamePhase.SEER_TURN:
                print("Seer choosing")
                def filter_seer(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.SEER): return None
                    return player

                async def send_vote_result(vote_result: VoteCollector):
                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        looked_player, _ = vote_result

                        async def seer_reveal(interaction: discord.Interaction):
                            p = filter_seer(interaction)
                            if not p: return
                            await interaction.response.send_message(f"{looked_player.name} est {looked_player.role.name}", ephemeral=True)

                        await send_menu(game.channel, "La voyante se concentre,", "La boule magique indique...",
                                        seer_reveal)

                    await on_continue()

                await send_player_vote_menu(game.channel, game.players, "La voyante...",
                                            "... choisit qui observer!",
                                            game.players,
                                            filter_seer, 10, send_vote_result)
            case GamePhase.WITCH_TURN:
                print("Witch choosing")
                pass
