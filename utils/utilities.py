#!/usr/bin/env python3

import json, datetime, discord
import pandas as pd

def read_json(path: str) -> list:
    data = ""

    with open(path, "r") as f:
        data = json.load(f)
    return data

def get_date() -> str:
    return str(datetime.datetime.now())[:-7]

async def bmessage(ctx: object, msg: str, footer: str = None) -> object:
    embed = discord.Embed(color=0x000000, description=msg)
    if (footer):
        embed.set_footer(text=footer)
    return await ctx.send(embed=embed)

def bframe(data: dict) -> str:
    """Return a basic frame (name, value)"""

    data = data or {"--": "--"}
    data = {
        "Name": data.keys(),
        "Value": data.values()
    }
    return (pd.DataFrame(data=data).to_string(index=False))