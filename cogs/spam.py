#!/usr/bin/env python3

from typing import *
from discord.ext import commands
from cogs.sql import SQLCursor

from utils.utilities import read_json
REACTION = read_json("data/json/reaction.json")
