from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player import Player

import discord

from menu_systems.menus import send_selection_menu
from menu_systems.time_select_view import TimedSelectView
from menu_systems.vote_collector import VoteCollector



async def send_player_vote_menu(channel, game_players: list[any], name: str, placeholder: str, vote_options: list[Player], get_valid_voter_player, timeout: int, on_time_over: callable, remaining_time_on_end = 5, display_votes=False):
    vote_system = VoteCollector(vote_options, [player for player in game_players if get_valid_voter_player(player) is not None])
    view = TimedSelectView(channel, timeout=timeout, on_time_over=lambda: on_time_over(vote_system), remaining_time_on_end=remaining_time_on_end)

    if display_votes:
        vote_result_message = await channel.send("Résultat du vote:\n")

    def menu_select_player(selected_player: Player) -> callable:
        async def chooser_selection(interaction: discord.Interaction):
            player = get_valid_voter_player(interaction)
            if player is None: return
            await interaction.response.send_message(f"Vous avez voté pour : {selected_player.name}", ephemeral=True)
            everybody_voted = await vote_system.add_vote(selected_player, player)
            if display_votes:
                await vote_result_message.edit(content="Résultat du vote:\n" + vote_system.get_current_votes())
            if everybody_voted:
                await view.premature_end()

        return chooser_selection

    await send_selection_menu(channel, name, placeholder,
                              [(player.name, menu_select_player(player)) for player in vote_options], view)
