#!/usr/bin/env python3

from bot import Bot
from configparser import ConfigParser
import asyncio, logging, sys

from utils.utilities import *

# Setup log system
log = logging.getLogger()
log.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")

# Logger for a file
f = logging.FileHandler("logs/bot.log", "a", encoding="utf-8")
f.setLevel(logging.INFO)
f.setFormatter(formatter)
log.addHandler(f)

# Logger for stdout
screen = logging.StreamHandler(sys.stdout)
screen.setLevel(logging.INFO)
screen.setFormatter(formatter)
log.addHandler(screen)

# Get environment variables (config.ini)
config = ConfigParser()
config.read("config.ini")

async def main():
    bot = Bot()
    await bot.start(config.get("DISCORD", "TOKEN"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())