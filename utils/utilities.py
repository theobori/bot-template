"""some util features"""

import discord
import pandas as pd

from typing import Tuple

async def basic_message(ctx: object, msg: str, footer: str = None) -> object:
    """
        Sends a message and returns the object
    """

    embed = discord.Embed(color=0x000000, description=msg)

    if (footer):
        embed.set_footer(text=footer)

    return await ctx.send(embed=embed)

def basic_frame(data: dict) -> str:
    """
        Returns a basic frame (name, value)
    """

    data = data or {"--": "--"}
    data = {
        "Name": data.keys(),
        "Value": data.values()
    }

    return pd.DataFrame(data=data).to_string(index=False)

def fill_min(*args: Tuple[list]) -> list:
    """
        Set every list with the same length
    """

    length = len(max(*args, key=len))
    args = list(args)
    
    for i in range(len(args)):
        args[i] += (length - len(args[i])) * [" "]

    return args
