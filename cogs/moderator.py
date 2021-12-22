#!/usr/bin/env python3

from typing import *
from discord.ext import commands

from utils.utilities import read_json
REACTION = read_json("data/json/reaction.json")

class Moderator(commands.Cog):
    """Commands for the administrators, moderators"""

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def clear(self, ctx: commands.Context, n: int = 1):
        """Removes n message"""

        await ctx.message.delete()
        await ctx.send(f"[{REACTION['loading']}]")
        await ctx.channel.purge(limit = n + 1)

def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))