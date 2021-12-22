#!/usr/bin/env python3

from typing import *
from discord.ext import commands
from cogs.sql import SQLCursor

from utils.utilities import read_json
REACTION = read_json("data/json/reaction.json")

class Moderator(commands.Cog, SQLCursor):
    """Commands for the administrators, moderators"""

    def __init__(self, bot):
        self.bot = bot
        SQLCursor.__init__(self)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def clear(self, ctx: commands.Context, n: int = 1):
        """Removes n message"""

        await ctx.message.delete()
        await ctx.send(f"[{REACTION['loading']}]")
        await ctx.channel.purge(limit = n + 1)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["command_stats"])
    async def cs(self, ctx: commands.Context):
        """Show how many times each commands has been used"""

        query = f"""SELECT name, count FROM command_stat
            WHERE guild_id={ctx.guild.id}"""
        self.execute(query)
        response = self.cursor.fetchall()
        
        print(response)

def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))