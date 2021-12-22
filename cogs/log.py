#!/usr/bin/env python3

from typing import *
from discord import channel
from discord.ext import commands
import logging, discord, datetime, os

from cogs.sql import LogRequest
from utils.utilities import bmessage, bframe

log = logging.getLogger(__name__)

def has_log(func) -> callable:
    """Decorator that will call func"""

    async def inner(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except:
            log.info("Failed to send log")
    return (inner)

def fill_min(*args: Tuple[list]) -> list:
    """Set every list with the same length"""

    length = len(max(*args, key=len))
    args = list(args)
    
    for i in range(len(args)):
        args[i] += (length - len(args[i])) * [" "]
    return (args)


class Log(commands.Cog, LogRequest):
    """Guild log controller"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        LogRequest.__init__(self)

    async def setlog(self, ctx: commands.Context, category: str = None, channel_id: str = None):
        """Link channel id with a log category"""

        if not category or not channel_id:
            return

        try:
            channel_id = int(channel_id)
            self.execute(f"""INSERT INTO guild_log_channel (guild_id, {category})
                VALUES({ctx.guild.id}, {channel_id})
                ON DUPLICATE KEY
                UPDATE {category} = {channel_id}""")
        except:
            return (await bmessage(ctx, f"❌ Failed to set log", "See help for put"))

        if not channel_id in map(lambda x: x.id, ctx.guild.text_channels):
            return (await bmessage(ctx, "❌ Unauthorized channel"))

        channel = self.bot.get_channel(channel_id)
        if (not channel):
            return (await bmessage(ctx, "❌ Channel doesn't exist"))
        await (bmessage(ctx, f"✅ Set `{category}` logs with the channel {channel.mention}", f"Channel ID: {channel_id}"))

    async def setpermission(self, ctx: commands.Context, event: str = None, state: str = None):
        """Enable or disable log for a specific event"""

        if not event or not state in map(str, range(2)):
            return
        
        try:
            self.execute(f"""UPDATE guild_log_permission
                SET {event} = {state}
                WHERE guild_id = {ctx.guild.id}""")
        except:
            return (await bmessage(ctx, f"❌ Failed to set permission", "See help for put"))
        await (bmessage(ctx, f"{['🔓 Enabled', '🔒 Disabled'][not int(state)]} `{event}`"))

    def generate_linker(self) -> Dict[str, callable]:
        return ({
                "log": {
                    "set": self.setlog,
                    "show": self.get_log_channels
                },
                "permission": {
                    "set": self.setpermission,
                    "show": self.get_log_permissions
                }
            })

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def put(self, ctx: commands.Context, modify: str = None, key: str = None, value: str = None):
        """
            Change informations like log channel, permissions state, etc...

            key must be `log` or `permission`

        __**Logs category**__
            value must be a channel id

            **Available categories**:
            - `messages`
            - `roles`
        
        __**Permissions**__
            value can be 0 or 1

            **Available events**:
            - `message_delete`
            - `message_edit`
            - `role_create`
            - `role_delete`
            - `role_update`"""

        if not modify or not key or not value:
            return

        linker: Dict[str, callable] = self.generate_linker()

        if not modify in linker.keys():
            return (await bmessage(ctx, "❌ Failed", "See help for set"))
        await linker[modify]["set"](ctx, key, value)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def show(self, ctx: commands.Context, key: str = None):
        """Show informations about log, log permissions, etc ...
        
        key must be `log` or `permission`"""

        linker: Dict[str, callable] = self.generate_linker()
        if not key in linker.keys():
            return (await bmessage(ctx, "❌ Failed", "See help for sho"))

        frame = bframe(linker[key]["show"](ctx.guild.id))
        await bmessage(ctx, f"```{frame}```")

    async def attachment_handler(self, msg: discord.Message, embed: discord.Embed):
        """If there is an attachment, it adds it to the embed"""
        file = None

        if not msg.attachments:
            return (file)

        attachment = msg.attachments[0]
        name = attachment.filename
    
        with open(name, "wb") as f:
            await attachment.save(f, use_cached=True)
            file = discord.File(name, filename=name)
            embed.set_image(url=f'attachment://{name}')
            os.remove(name)

        return (file)

    @has_log
    async def store_message(self, message: discord.Message, state: str):
        """Send the message informations in the selected log channel"""

        channel_id = self.resolve_log(message.guild.id, "messages")

        embed = discord.Embed(title=state,
            description=message.content, color=0x000000,
            timestamp=datetime.datetime.now())
        embed.set_footer(text=f"ID: {message.id}")

        author = message.author
        embed.set_author(name=f"{author} - #{message.channel}",
            icon_url=author.avatar_url_as(format="png"))

        file = await self.attachment_handler(message, embed)
        await self.bot.get_channel(int(channel_id)).send(file=file, embed=embed)

    @has_log
    async def store_role(self, role: discord.Role, state: str):
        """Send the role informations in the selected log channel"""

        channel_id = self.resolve_log(role.guild.id, "roles")

        permissions = filter(lambda x: x[1], role.permissions)
        permissions = "\n".join(map(lambda x: x[0], permissions))

        embed = discord.Embed(title=state,
        description=f"""`{role.name}` - ID: `{role.id}`
        
        **Color**
        {role.colour.value}

        **Permissions**
        {permissions}""", color=0x000000,
        timestamp=datetime.datetime.now())
    
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