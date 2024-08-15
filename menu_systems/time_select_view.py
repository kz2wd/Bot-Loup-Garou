from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


import asyncio

import discord


class TimedSelectView(discord.ui.View):
    def __init__(self, channel, timeout: int, on_time_over: callable):
        super().__init__()
        self.timeout = timeout
        self.on_time_over = on_time_over
        self.timer_task = None  # Task reference for the timer
        self.channel = channel
        self.timer_message = None

        # Start the timer
        self.start_timer()

    def start_timer(self):
        # Start a background task to handle the timer
        self.timer_task = asyncio.create_task(self.update_timer())

    async def update_timer(self):
        self.timer_message = await self.channel.send(f"Temps restant: {self.timeout} seconds")
        while self.timeout > 0:
            await asyncio.sleep(1)
            self.timeout -= 1
            # Update the message with the remaining time
            await self.timer_message.edit(content=f"Temps restant: {self.timeout} seconds")

        # For some reason, call self.end() here breaks after the message edit
        await self.on_time_over()

    async def end(self):
        if self.timer_task:
            self.timer_task.cancel()  # Cancel the timer task
            self.timer_task = None
            await self.timer_message.edit(content=f"Vote fini")
        try:
            await self.on_time_over()
        except TypeError as ignored:
            pass # Idk why it happens, and I don't care because it crashes when on_time_over has already been triggered one time, which is plenty enough!
