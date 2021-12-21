import discord
from typing import *
from dataclasses import dataclass
from discord.ext import commands

from utils.utilities import read_json
REACTION = read_json("json/reaction.json")

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
    """Class that manage Page objects"""

    def __init__(self):
        self.pages: Dict[int, Page] = {}
    
    def add_page(self, msg, author_id: str, pages: List[List[str]]):
        self.pages[msg.id] = Page(msg, author_id, pages, 0)

    async def change_page(self, r_dst: object, msg_id: str, r_src: str, move: int, user: object):
        """Go to previous or next page"""
        if (str(r_dst) != r_src): return
        if (not msg_id in list(self.pages.keys())): return

        obj: Page = self.pages[msg_id]
        if (obj.author_id != user.id): return

        # Check out of range
        if (obj.page + move < 0 or obj.page + move > len(obj.data) - 1):
            return

        # Change page
        obj.page += move

        # Edit msg with fancy display
        display: str = "```" + '\n'.join(obj.data[obj.page]) + "```"
        embed = discord.Embed(color = 0x000000, description = display)
        embed.set_footer(text = f"page {obj.page + 1} / {len(obj.data)}")
        await obj.msg.edit(embed = embed)

    async def check_for_pages(self, reaction: object, user: object):
        """Check reactions for 'resolve'"""
        _id: int = reaction.message.id
        page: Dict[str, str] = REACTION["pages"]
    
        await self.change_page(reaction, _id, page["previous"], -1, user)
        await self.change_page(reaction, _id, page["next"], 1, user)