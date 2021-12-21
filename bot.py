#!/usr/bin/env python3

from typing import *
from discord.ext import commands
import discord, logging

log: logging.Logger = logging.getLogger(__name__)

extensions: Tuple[str] = (
    "cogs.moderator",
)

class Bot(commands.Bot):
    """Pirmary class that contains the bot object to run"""

    def __init__(self):
        super().__init__(command_prefix = ["."], help_command=commands.MinimalHelpCommand())

        for extension in extensions:
            try:
                self.load_extension(extension)
                log.info(f"Loaded the extension {extension}")
            except:
                log.warning(f"Failed to load the extension {extension}")
    
    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity = discord.Game(name = "a game"))

    async def close(self):
        log.info("Closing")
        await super().close()

    async def on_command(self, ctx: commands.Context):
        destination: str = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        log.info(f"{ctx.author} used command in {destination}: {ctx.message.content}")