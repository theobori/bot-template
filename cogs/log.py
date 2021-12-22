#!/usr/bin/env python3

from typing import *
from discord.ext import commands
import logging, discord, datetime

from cogs.sql import LogRequest
from utils.utilities import bmessage

log = logging.getLogger(__name__)


def has_log(func):
    """Decorator that will call func"""

    async def inner(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except:
            log.info("Failed to send log")
    return (inner)

class Log(commands.Cog, LogRequest):
    """Guild log controller"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        LogRequest.__init__(self)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setlog(self, ctx: commands.Context, category: str = None, channel_id: int = None):
        """Link channel id with a log category
            
            **Available categories**:
            - `messages`
            - `voices`
            - `roles`"""

        if not category or not channel_id:
            return
        
        try:
            self.execute(f"""INSERT INTO guild_log (guild_id, {category})
                VALUES({ctx.guild.id}, {channel_id})
                ON DUPLICATE KEY
                UPDATE {category} = {channel_id}""")
        except:
            return (await bmessage(ctx, f"❌ Failed to set log", "See help for setlog"))
        await (bmessage(ctx, f"✅ Set `{category}` logs with channel id `{channel_id}`"))

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setpermission(self, ctx: commands.Context, event: str = None, state: str = None):
        """Enable or disable log for a specific event
            
            state can be 0 or 1

            **Available events**:
            - `message_delete`
            - `message_edit`
            - `role_create`
            - `role_delete`
            - `role_update`"""

        if not event or not state in map(str, range(2)):
            return
        
        try:
            self.execute(f"""UPDATE guild_log_permission
                SET {event} = {state}
                WHERE guild_id = {ctx.guild.id}""")
        except:
            return (await bmessage(ctx, f"❌ Failed to set permission", "See help for setpermission"))
        await (bmessage(ctx, f"{['🔓 Enabled', '🔒 Disabled'][not int(state)]} `{event}`"))

    @has_log
    async def store_message(self, message: discord.Message, state: str):
        """Send the message informations in the selected log channel"""

        channel_id = self.resolve_log(message.guild.id, "messages")

        embed = discord.Embed(title = state,
            description = message.content, color = 0x000000,
            timestamp = datetime.datetime.now())
        embed.set_footer(text = f"ID: {message.id}")
        author = message.author
        embed.set_author(name = f"{author} - #{message.channel}",
            icon_url = author.avatar_url_as(format = "png"))

        await self.bot.get_channel(int(channel_id)).send(embed = embed)

    @has_log
    async def store_role(self, role: discord.Role, state: str):
        """Send the role informations in the selected log channel"""

        channel_id = self.resolve_log(role.guild.id, "roles")

        permissions = filter(lambda x: x[1], role.permissions)
        permissions = "\n".join(map(lambda x: x[0], permissions))

        embed = discord.Embed(title = state,
        description = f"""`{role.name}` - ID: `{role.id}`
        
        **Color**
        {role.colour.value}

        **Permissions**
        {permissions}""", color = 0x000000,
        timestamp = datetime.datetime.now())
    
        await self.bot.get_channel(int(channel_id)).send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if (not self.get_log_permission(message.guild.id, "message_delete")):
            return
        await self.store_message(message, "Message deleted")

    @commands.Cog.listener()
    async def on_message_edit(self, previous: discord.Message, new: discord.Message):
        if (not self.get_log_permission(previous.guild.id, "message_edit")):
            return
        await self.store_message(previous, "Message before the edit")
        await self.store_message(new, "Message after the edit")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if (not self.get_log_permission(role.guild.id, "role_create")):
            return
        await self.store_role(role, "Role created")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if (not self.get_log_permission(role.guild.id, "role_delete")):
            return
        await self.store_role(role, "Role deleted")
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, previous: discord.Role, new: discord.Role):
        if (not self.get_log_permission(previous.guild.id, "role_update")):
            return
        await self.store_role(previous, "Role before the update")
        await self.store_role(new, "Role after the update")

def setup(bot: commands.Bot):
    bot.add_cog(Log(bot))