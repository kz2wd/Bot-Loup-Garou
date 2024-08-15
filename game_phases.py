from enum import Enum, auto

import discord

from menu_systems.vote_collector import VoteCollector
from menu_systems.vote_menu import send_player_vote_menu
from player import Player
from roles import Team, Role


class GamePhase(Enum):
    WEREWOLVES_TURN = auto()
    VILLAGE_WAKING_UP = auto()
    VILLAGERS_VOTE = auto()

    async def execute(self, game, on_continue):
        match self:
            case GamePhase.WEREWOLVES_TURN:
                print("Werewolves hunting")
                werewolves = [player for player in game.players if player.role.team == Team.WEREWOLF]
                if not werewolves:
                    await on_continue()

                async def send_vote_result(vote_result: VoteCollector):
                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        await game.channel.send("Les loudivers se sont régalés ...")
                        player, _ = vote_result
                        game.schedule_kill_player(player)
                    else:
                        await game.channel.send("Les loudivers n'ont pas pu se décider cette nuit!")

                    await on_continue()

                werewolves_targets = [player for player in game.players]  # if player.role.team != Team.WEREWOLF

                def filter_werewolf(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.WEREWOLF): return None
                    return player

                await send_player_vote_menu(game.channel, game.players, "Les loudivers...",
                                            "...choisissent leur cible!",
                                            werewolves_targets,
                                            filter_werewolf, 15, send_vote_result)

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

                    await on_continue()

                await send_player_vote_menu(game.channel, game.players, "Les villageois",
                                            "...choisissent un coupable!",
                                            game.players,
                                            filter_player, 45, send_vote_result)



