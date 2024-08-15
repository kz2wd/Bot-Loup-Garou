import discord
from discord.ui import Button

from menu_systems.time_select_view import TimedSelectView


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
    view.add_item(Button(label="Afficher les votes actuels"))

    # Send the message with the select menu
    message = await channel.send(content=name, view=view)
    view.message = message

