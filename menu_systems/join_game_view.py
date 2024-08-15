from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

import discord


class JoinGameView(discord.ui.View):
    def __init__(self, current_game):
        super().__init__()
        self.current_game = current_game

    @discord.ui.button(label="Rejoindre la partie", style=discord.ButtonStyle.primary)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if self.current_game:
            if not self.current_game.is_player_registered(user):
                if self.current_game.owner is None:
                    self.current_game.set_owner(user)
                else:
                    self.current_game.add_player(user)
                await interaction.response.send_message(f"Vous avez rejoint la partie!", ephemeral=True)
                if self.message:
                    await self.message.edit(content=f"Joueurs: {', '.join(str(p.user.name) for p in self.current_game.players)}", view=self)

            else:
                pass
                # await interaction.response.send_message("You've already joined the game!", ephemeral=True)

    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.primary)
    async def start_game_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user == self.current_game.owner.user:
            await interaction.response.send_message("La partie commence!", ephemeral=False)
            await self.current_game.start()
        else:
            await interaction.response.send_message("Seul l'hôte peut démarrer la partie!", ephemeral=True)
