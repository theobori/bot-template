"""main file"""

from bot import Bot
from configparser import ConfigParser
import asyncio, logging, sys

from utils.utilities import *

# Setup log system
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

FORMATTER = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")

# Logger for a file
f = logging.FileHandler("logs/bot.log", "a", encoding="utf-8")
f.setLevel(logging.INFO)
f.setFormatter(FORMATTER)
LOG.addHandler(f)

# Logger for stdout
screen = logging.StreamHandler(sys.stdout)
screen.setLevel(logging.INFO)
screen.setFormatter(FORMATTER)
LOG.addHandler(screen)

# Get environment variables (config.ini)
CONFIG = ConfigParser()
CONFIG.read("config.ini")

async def main():
    bot = Bot()
    await bot.start(CONFIG.get("DISCORD", "TOKEN"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
