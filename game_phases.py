from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Union, Awaitable

from menu_systems.time_select_view import TimedSelectView

if TYPE_CHECKING:
    from player import Player
    from menu_systems.vote_collector import VoteCollector
    from game import Game

from roles import Team, Role
from enum import Enum, auto

import discord


from menu_systems.vote_menu import send_player_vote_menu
from menu_systems.menus import send_menu, send_selection_menu


DEFAULT_ROLES_TIMEOUT = 25


class GamePhase(Enum):
    WEREWOLVES_TURN = auto()
    VILLAGE_WAKING_UP = auto()
    VILLAGERS_VOTE = auto()
    CUPIDON_TURN = auto()
    SEER_TURN = auto()
    WITCH_TURN = auto()

    async def execute(self, game: Game, on_continue):
        match self:
            case GamePhase.WEREWOLVES_TURN:
                print("Werewolves hunting")
                if not any(player.role.team == Team.WEREWOLF for player in game.players):
                    print("Skipping werewolf turn")
                    await on_continue()
                    return

                async def send_vote_result(vote_result: VoteCollector):
                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        await game.channel.send("Les loudivers se sont régalés ...")
                        player, _ = vote_result
                        game.schedule_kill_player(player)
                    else:
                        pass
                        # await game.channel.send("Les loudivers n'ont pas pu se décider cette nuit!")

                    print("Continuing")
                    await on_continue()
                    return

                werewolves_targets = [player for player in game.players]  # if player.role.team != Team.WEREWOLF

                def filter_werewolf(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.WEREWOLF): return None
                    return player

                await send_player_vote_menu(game.channel, game.players, "Les loudivers...",
                                            "...choisissent leur cible!",
                                            werewolves_targets,
                                            filter_werewolf, DEFAULT_ROLES_TIMEOUT, send_vote_result, display_votes=True)

            case GamePhase.VILLAGE_WAKING_UP:
                print("Waking up!")
                await game.channel.send("Cludivers se réveille!")
                await game.clear_death_list()
                await game.handle_victory(on_continue)
                return

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
                        await game.kill_player(player)  # stops here ?
                    else:
                        await game.channel.send("Les zumains n'ont pas réussi à choisir!")

                    await game.handle_victory(on_continue)
                    return

                await send_player_vote_menu(game.channel, game.players, "Les villageois...",
                                            "...choisissent un coupable!",
                                            game.players,
                                            filter_player, DEFAULT_ROLES_TIMEOUT, send_vote_result, 30, display_votes=True)

            case GamePhase.CUPIDON_TURN:
                print("Cupidon choosing")

                if not any(player.role == Role.CUPIDON for player in game.players):
                    print("Skipping cupidon's turn")
                    await on_continue()
                    return

                def filter_cupidon(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.CUPIDON): return None
                    return player

                async def send_vote_result(vote_result: VoteCollector):

                    vote_result = vote_result.get_single_most()
                    if vote_result:
                        chosen_lover, _ = vote_result

                        async def kill_lovers():
                            for lover in game.players:
                                if lover.is_in_love:
                                    await game.kill_player(lover, lambda p: f"{p.name} s'est donné la mort par amour.")

                        chosen_lover.is_in_love = True
                        chosen_lover.on_player_kill.insert(0, kill_lovers)

                    await on_continue()
                    return

                # We can't show only players that are not in love because other players will know otherwise :/

                await send_player_vote_menu(game.channel, game.players, "Cupidon...",
                                            "... pointe sa flêche vers un nouvel amoureux!",
                                            game.players,
                                            filter_cupidon, DEFAULT_ROLES_TIMEOUT, send_vote_result, 0)

            case GamePhase.SEER_TURN:
                print("Seer choosing")

                if not any(player.role == Role.SEER for player in game.players):
                    print("Skipping seer's turn")
                    await on_continue()
                    return

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
                    return

                await send_player_vote_menu(game.channel, game.players, "La voyante...",
                                            "... choisit qui observer!",
                                            game.players,
                                            filter_seer, DEFAULT_ROLES_TIMEOUT, send_vote_result)
            case GamePhase.WITCH_TURN:
                print("Witch choosing")
                if not any(player.role == Role.WITCH for player in game.players):
                    print("Skipping witch's turn")
                    await on_continue()
                    return

                def filter_witch(interaction: discord.Interaction) -> Player | None:
                    if not (player := game.get_player(interaction.user)): return None
                    if not (player.role == Role.WITCH): return None
                    return player
                def set_potion_choice(interaction, choice: Callable[[Player], Awaitable[None]]):
                    player = filter_witch(interaction)
                    if player is None: return
                    nonlocal witch_potion_choice
                    witch_potion_choice = choice

                witch_options = {
                    "Mort": lambda interaction: set_potion_choice(interaction, lambda player: player.game.schedule_kill_player(player)),
                    "Vie": lambda interaction: set_potion_choice(interaction, lambda player: player.game.unschedule_kill_player(player)),
                    "Rien": lambda interaction: set_potion_choice(interaction, lambda player: None)
                }

                witch_potion_choice: Callable[[Player], Awaitable[None]] = witch_options["Rien"]

                async def witch_throw_potion_at_player():
                    async def send_vote_result(vote_result: VoteCollector):
                        vote_result = vote_result.get_single_most()
                        if vote_result:
                            target_player, _ = vote_result
                            await witch_potion_choice(target_player)
                        else:
                            await game.channel.send("La sorcière n'a pas réussie à lancer sa potion.")

                        await on_continue()
                        return

                    await send_player_vote_menu(game.channel, game.players, "La sorcière utilise sa potion sur...",
                                                "...la maison de...",
                                                game.players,
                                                filter_witch, DEFAULT_ROLES_TIMEOUT, send_vote_result, 0)

                view = TimedSelectView(game.channel, timeout=DEFAULT_ROLES_TIMEOUT, on_time_over=witch_throw_potion_at_player,
                                       remaining_time_on_end=0)

                async def death_list_reveal_button(interaction: discord.Interaction):
                    witch = filter_witch(interaction)
                    if witch is None: return
                    await interaction.response.send_message("\n".join(player.name for player in witch.game.on_death_list), ephemeral=True)

                await send_menu(game.channel, "La sorcièce se concentre et découvre...", '...qui sont les victimes de cette nuit',
                                death_list_reveal_button)

                await send_selection_menu(game.channel, "La sorcière prépare son chaudron...", "...à l'intérieur il y une potion de...",
                                          list(witch_options.items()), view)
                pass
