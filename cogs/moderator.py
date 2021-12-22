#!/usr/bin/env python3

from typing import *
from discord.ext import commands
from cogs.sql import SQLCursor
from cogs.page import Pages, make_groups

from utils.utilities import bframe, bmessage, read_json
REACTION = read_json("data/json/reaction.json")

class Moderator(commands.Cog, SQLCursor, Pages):
    """Commands for the administrators, moderators"""

    def __init__(self, bot):
        SQLCursor.__init__(self)
        Pages.__init__(self)

        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if (not reaction.message.author.bot or user.bot):
            return
        await reaction.remove(user)
        await self.check_for_pages(reaction, user)

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

        if not response:
            return (await bmessage(ctx, "❌ Empty"))
        
        data = {item["name"]: item["count"] for item in response}
        frame = bframe(data)
        pages = make_groups(frame.split("\n"), 10)
        await self.send_first_page(ctx, pages)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def warn(self, ctx: commands.Context, reason: str = "No reason given"):
        """Warn an user"""

        # TODO
    

def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))