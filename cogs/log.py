#!/usr/bin/env python3

from typing import *
from discord.ext import commands
import logging, discord, datetime

from cogs.sql import SQLCursor

log = logging.getLogger(__name__)

class Log(commands.Cog, SQLCursor):
    """Guild log controller"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        SQLCursor.__init__(self)

    def has_setup(func):
        async def inner(*args, **kwargs):
            try:
                await func(args, kwargs)
            except:
                log.info("Failed to send log")
        return (inner)

    @has_setup
    async def store_message(self, message: discord.Message):

        query = f"""SELECT messages FROM guild_log WHERE
            guild_id={message.guild.id}"""

        self.execute(query)
        channel = self.cursor.fetchone()

        embed = discord.Embed(title=message.id, description = message.content, 
            color = 0x000000, timestamp = datetime.datetime.now())
        author = message.author
        embed.set_author(name = f"{author} - #{message.channel}",
            icon_url = author.avatar_url_as(format = "png"))

        chan = self.bot.get_channel(channel)
        await chan.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        await self.store_message(message)

def setup(bot: commands.Bot):
    bot.add_cog(Log(bot))