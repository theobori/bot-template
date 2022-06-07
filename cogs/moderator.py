"""moderation cog"""

from discord.ext import commands
import discord

from utils.database import CursorDB
from utils.page import Pages, make_groups
from utils.utilities import basic_frame, basic_message

from utils.reactions import Reactions

class Moderator(commands.Cog, CursorDB, Pages):
    """
        Commands for the administrators, moderators
    """

    def __init__(self, bot):
        CursorDB.__init__(self)
        Pages.__init__(self)

        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: object, user: object):
        if not reaction.message.author.bot or user.bot:
            return

        await reaction.remove(user)
        await self.handler(reaction, user)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def clear(self, ctx: commands.Context, n: int = 1):
        """
            Removes n message
        """

        await ctx.message.delete()
        await ctx.send(Reactions.LOADING)
        await ctx.channel.purge(limit = n + 1)

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["command_stats"])
    async def cs(self, ctx: commands.Context):
        """
            Show how many times each commands has been used
        """

        self.execute(f"""SELECT name, count FROM command_stat
            WHERE guild_id={ctx.guild.id}""")

        response = self.cursor.fetchall()

        if not response:
            return (await basic_message(ctx, "❌ Empty"))
        
        response = sorted(response, key=lambda item: int(item["count"]))[::-1]
        data = {item["name"]: item["count"] for item in response}
        page_content = basic_frame(data).split("\n")
        page_content = make_groups(page_content, 10)

        await self.create(ctx, page_content)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def warn(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason given"):
        """
            Warn an user on a Discord guild
        """

        self.execute(f"""INSERT INTO warn (guild_id, user_id)
            VALUES({ctx.guild.id}, {member.id})
            ON DUPLICATE KEY
            UPDATE count = count + 1""")
        
        await basic_message(
            ctx,
            f"⚠️ {member.mention} has been warned by `{ctx.author}`",
            f"Reason: {reason}"
        )
    
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["warn_stats"])
    async def ws(self, ctx: commands.Context):
        """
            Show every user warned
        """

        data = {}

        self.execute(f"""SELECT user_id, count FROM warn
            WHERE guild_id={ctx.guild.id}""")
        response = self.cursor.fetchall()

        if not response:
            return await basic_message(ctx, "❌ Empty")
        
        for item in response:
            user_id = int(item["user_id"])
            user = await self.bot.fetch_user(user_id)
            key = f"{user} ({user_id})"

            data[key] = item["count"]

        page_content = basic_frame(data).split("\n")
        pages = make_groups(page_content, 10)

        await self.create(ctx, pages)

def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))
