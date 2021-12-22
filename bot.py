#!/usr/bin/env python3

from typing import *
from discord.ext import commands
import discord, logging

from cogs.sql import SQLCursor

log: logging.Logger = logging.getLogger(__name__)

extensions: Tuple[str] = (
    "cogs.moderator",
    "cogs.log"
)

class Bot(commands.Bot, SQLCursor):
    """Pirmary class that contains the bot object to run"""

    def __init__(self):
        super().__init__(command_prefix=["."], help_command=commands.MinimalHelpCommand())
        SQLCursor.__init__(self)

        for extension in extensions:
            try:
                self.load_extension(extension)
                log.info(f"Loaded the extension {extension}")
            except:
                log.warning(f"Failed to load the extension {extension}")

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name = "a game"))

    async def close(self):
        log.info("Closing")
        await self.close()

    async def on_command(self, ctx: commands.Context):
        dest = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        log.info(f"{ctx.author} used command in {dest}: {ctx.message.content}")

    async def on_guild_join(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has joined {guild.name} (ID: {guild.id})")

        self.execute(f"""INSERT INTO guild_log_permission (guild_id)
            VALUES({guild.id})""")
        self.execute(f"""INSERT INTO guild_log_channel (guild_id)
            VALUES({guild.id})""")

    async def on_guild_remove(self, guild: discord.Guild):
        log.warning(f"{self.user} (ID: {self.user.id}) has left {guild.name} (ID: {guild.id})")

        self.execute(f"""DELETE FROM guild_log_permission WHERE guild_id={guild.id}""")
