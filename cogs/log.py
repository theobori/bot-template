"""log manager"""

import logging, discord, datetime, os

from typing import Dict
from discord.ext import commands

from utils.database import LogRequest
from utils.utilities import basic_message, basic_frame
from utils.binds import Binds

LOG = logging.getLogger(__name__)

def has_log(func) -> callable:
    """
        Decorator that will call func
    """

    async def inner(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except:
            LOG.info("Failed to send log")

    return inner

class Log(commands.Cog, LogRequest, Binds):
    """
        Guild logs controller
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        LogRequest.__init__(self)
        Binds.__init__(self)
        self.init_binds()

    def init_binds(self):
        """
            Initializes binds
        """

        self.add_bind("log_set", self.setlog)
        self.add_bind("log_show", self.get_channels)
        self.add_bind("permission_set", self.setpermission)
        self.add_bind("permission_show", self.get_permissions)

    async def setlog(self, ctx: commands.Context, category: str = None, channel_id: str = None):
        """
            Link channel id with a log category
        """

        if not category or not channel_id:
            return

        try:
            channel_id = int(channel_id)

            if not channel_id in map(lambda x: x.id, ctx.guild.text_channels):
                return await basic_message(ctx, "❌ Unauthorized channel")

            self.execute(f"""INSERT INTO guild_log_channel (guild_id, {category})
                VALUES({ctx.guild.id}, {channel_id})
                ON DUPLICATE KEY
                UPDATE {category} = {channel_id}""")
        except:
            return await basic_message(ctx, f"❌ Failed to set log", "See help for put")


        channel = self.bot.get_channel(channel_id)
        if not channel:
            return await basic_message(ctx, "❌ Channel doesn't exist")
    
        await basic_message(
            ctx,
            f"✅ Set `{category}` logs with the channel {channel.mention}",
            f"Channel ID: {channel_id}"
        )

    async def setpermission(self, ctx: commands.Context, event: str = None, state: str = None):
        """
            Enable or disable log for a specific event
        """

        if not event or not state in map(str, range(2)):
            return
        
        try:
            self.execute(f"""UPDATE guild_log_permission
                SET {event} = {state}
                WHERE guild_id = {ctx.guild.id}""")
        except:
            return await basic_message(ctx, f"❌ Failed to set permission", "See help for put")

        await basic_message(
            ctx,
            f"{['🔓 Enabled', '🔒 Disabled'][not int(state)]} `{event}`"
        )


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
            - `role_update`
        """

        if not modify or not key or not value:
            return

        bind_key = modify + "_set"
        if not bind_key in self.key_binding.keys():
            return await basic_message(ctx, "❌ Failed", "See help for set")

        await self.try_call_from_bind(bind_key, ctx, key, value)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def show(self, ctx: commands.Context, key: str = None):
        """
            Show informations about log, log permissions, etc ...

            key must be `log` or `permission`
        """

        bind_key = key + "_show"

        if not bind_key in self.key_binding.keys():
            return await basic_message(ctx, "❌ Failed", "See help for show")

        data = await self.try_call_from_bind(bind_key, ctx.guild.id)
        frame = basic_frame(data)
        
        await basic_message(ctx, f"```{frame}```")

    async def attachment_handler(self, msg: discord.Message, embed: discord.Embed):
        """
            If there is an attachment, it adds it to the embed
        """
        
        file = None

        if not msg.attachments:
            return file

        attachment = msg.attachments[0]
        name = attachment.filename
    
        with open(name, "wb") as f:
            await attachment.save(f, use_cached=True)
            file = discord.File(name, filename=name)
            embed.set_image(url=f'attachment://{name}')
            os.remove(name)

        return file

    @has_log
    async def store_message(self, message: discord.Message, state: str):
        """
            Sends the message informations in the selected log channel
        """

        channel_id = self.resolve(message.guild.id, "messages")
        author = message.author
        embed = discord.Embed(title=state,
            description=message.content, color=0x000000,
            timestamp=datetime.datetime.now())

        embed.set_footer(text=f"ID: {message.id}")
        embed.set_author(name=f"{author} - #{message.channel}",
            icon_url=author.avatar_url_as(format="png"))

        file = await self.attachment_handler(message, embed)
        await self.bot.get_channel(int(channel_id)).send(file=file, embed=embed)

    @has_log
    async def store_role(self, role: discord.Role, state: str):
        """
            Send the role informations in the selected log channel
        """

        channel_id = self.resolve(role.guild.id, "roles")

        permissions = filter(lambda x: x[1], role.permissions)
        permissions = "\n".join(map(lambda x: x[0], permissions))

        embed = discord.Embed(title=state,
        description=f"""`{role.name}` - ID: `{role.id}`
        
        **Color**
        {role.colour.value}

        **Permissions**
        {permissions}""", color=0x000000,
        timestamp=datetime.datetime.now())
    
        await self.bot.get_channel(int(channel_id)).send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        if not self.get_permission(message.guild.id, "message_delete"):
            return

        await self.store_message(message, "Message deleted")

    @commands.Cog.listener()
    async def on_message_edit(self, previous: discord.Message, new: discord.Message):
        if previous.author.bot:
            return
        if not self.get_permission(previous.guild.id, "message_edit"):
            return

        await self.store_message(previous, "Message before the edit")
        await self.store_message(new, "Message after the edit")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if not self.get_permission(role.guild.id, "role_create"):
            return

        await self.store_role(role, "Role created")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        if not self.get_permission(role.guild.id, "role_delete"):
            return

        await self.store_role(role, "Role deleted")
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, previous: discord.Role, new: discord.Role):
        if not self.get_permission(previous.guild.id, "role_update"):
            return

        await self.store_role(previous, "Role before the update")
        await self.store_role(new, "Role after the update")

def setup(bot: commands.Bot):
    bot.add_cog(Log(bot))
