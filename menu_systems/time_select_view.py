import asyncio

import discord


class TimedSelectView(discord.ui.View):
    def __init__(self, timeout: int, on_time_over: callable):
        super().__init__()
        self.timeout = timeout
        self.on_time_over = on_time_over
        self.timer_task = None  # Task reference for the timer
        self.message = None

        # Start the timer
        self.start_timer()

    def start_timer(self):
        # Start a background task to handle the timer
        self.timer_task = asyncio.create_task(self.update_timer())

    async def update_timer(self):
        while self.timeout > 0:
            await asyncio.sleep(1)
            self.timeout -= 1
            # Update the message with the remaining time
            if self.message:
                await self.message.edit(content=f"Temps restant: {self.timeout} seconds\n\n{self.message.content}")

        # For some reason, call self.end() here breaks after the message edit
        await self.on_time_over()

    async def end(self):
        if self.timer_task:
            self.timer_task.cancel()  # Cancel the timer task
            self.timer_task = None
            if self.message:
                await self.message.edit(content=f"Vote fini\n\n{self.message.content}")
        try:
            await self.on_time_over()
        except TypeError as ignored:
            pass # Idk why it happens, and I don't care because it crashes when on_time_over has already been triggered one time, which is plenty enough!
