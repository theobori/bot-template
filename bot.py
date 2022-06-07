"""Overriding commands.Bot"""

from typing import *
from configparser import ConfigParser
from discord.ext import commands
import discord, logging

from utils.database import CursorDB

LOG: logging.Logger = logging.getLogger(__name__)
CONFIG = ConfigParser()
CONFIG.read("config.ini")

extensions: Tuple[str] = (
    "cogs.moderator",
    "cogs.log"
)

class Bot(commands.Bot, CursorDB):
    """Pirmary class that contains the bot object to run"""

    def __init__(self):
        self.bot_options = {}

        self._get_options()
        super().__init__(**self.bot_options)
        CursorDB.__init__(self)

        for extension in extensions:
            try:
                self.load_extension(extension)
                LOG.info(f"Loaded the extension {extension}")
            except:
                LOG.warning(f"Failed to load the extension {extension}")

    def _get_options(self):
        for k, v in CONFIG.items("BOT"):
            k = k.lower()
            if (v):
                self.bot_options[k] = eval(v)

    async def on_ready(self):
        LOG.info(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.change_presence(activity=discord.Game(name = "a game"))

    async def close(self):
        LOG.critical("Closing")
        await self.close()

    async def on_command(self, ctx: commands.Context):
        dest = [f"#{ctx.channel} ({ctx.guild})", "DM"][not ctx.guild]
        LOG.info(f"{ctx.author} used command in {dest}: {ctx.message.content}")

        name = ctx.command.name
        self.execute(f"""INSERT INTO command_stat (guild_id, name)
                VALUES({ctx.guild.id}, '{name}')
                ON DUPLICATE KEY
                UPDATE count = count + 1""")

    async def on_guild_join(self, guild: discord.Guild):
        LOG.warning(f"{self.user} (ID: {self.user.id}) has joined {guild.name} (ID: {guild.id})")

        self.execute(f"""INSERT INTO guild_log_permission (guild_id) VALUES({guild.id})""")
        self.execute(f"""INSERT INTO guild_log_channel (guild_id) VALUES({guild.id})""")

    async def on_guild_remove(self, guild: discord.Guild):
        LOG.warning(f"{self.user} (ID: {self.user.id}) has left {guild.name} (ID: {guild.id})")

        self.execute(f"""DELETE FROM guild_log_permission WHERE guild_id={guild.id}""")
