import discord
from typing import *
from dataclasses import dataclass
from discord.ext import commands

from utils.utilities import read_json
REACTION = read_json("data/json/reaction.json")

def make_groups(arr: Any, size: int) -> list:
    return [arr[i:i + size] for i in range(0, len(arr), size)]

@dataclass
class Page:
    """Structure used to store clients"""

    msg: commands.Context
    author_id: int
    data: List[List[str]]
    page: int

class Pages:
    """Manage Page objects"""

    def __init__(self):
        self.pages: Dict[int, Page] = {}
    
    def __add_page(self, msg: discord.Message, author_id: str, pages: List[List[str]]):
        """Add a page to self.pages"""

        self.pages[msg.id] = Page(msg, author_id, pages, 0)

    async def send_first_page(self, ctx: commands.Context, pages: List[List[str]]):
        """Create and send the first page"""

        embed = discord.Embed(
            color       = 0x000000,
            description = "```" + '\n'.join(pages[0]) + "```"
        )
        embed.set_footer(text=f"page 1 / {len(pages)}")

        msg = await ctx.send(embed=embed)
        for _, v in REACTION["pages"].items():
            await msg.add_reaction(v)

        self.__add_page(msg, ctx.author.id, pages)

    def __get_obj(self, r_dst: object, msg_id: str, r_src: str, user: object) -> bool:
        """If the user click on the right emoji + the message id exists,
        then it will return the associated object"""

        if (str(r_dst) != r_src):
            return (None)

        if (not msg_id in list(self.pages.keys())):
            return (None)

        obj: Page = self.pages[msg_id]
        if (obj.author_id != user.id):
            return (None)

        return (obj)

    async def __change_page(self, r_dst: object, msg_id: str, r_src: str, move: int, user: object):
        """Go to previous or next page"""

        obj = self.__get_obj(r_dst, msg_id, r_src, user)
        if (not obj):
            return

        if (obj.page + move < 0 or obj.page + move > len(obj.data) - 1):
            return

        obj.page += move

        display = "```" + '\n'.join(obj.data[obj.page]) + "```"
        embed = discord.Embed(color=0x000000, description=display)
        embed.set_footer(text=f"page {obj.page + 1} / {len(obj.data)}")
        await obj.msg.edit(embed=embed)

    async def __delete(self, r_dst: object, msg_id: str, r_src: str, user: object):
        """Delete the author message"""

        obj = self.__get_obj(r_dst, msg_id, r_src, user)
        if (not obj):
            return
        
        await obj.msg.delete()
        del self.pages[msg_id]

    async def check_for_pages(self, reaction: object, user: object):
        """Check reactions"""

        _id = reaction.message.id
        page = REACTION["pages"]
    
        await self.__change_page(reaction, _id, page["previous"], -1, user)
        await self.__change_page(reaction, _id, page["next"], 1, user)
        await self.__delete(reaction, _id, page["delete"], user)