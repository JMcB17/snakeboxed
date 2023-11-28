"""Simple Discord bot for snekbox (sandboxed Python code execution), self-host or use a global instance."""


import logging
import sys
import tomllib
from pathlib import Path

from discord.ext import commands

import snakeboxed.cogs
from snakeboxed.bot import Snakeboxed

# todo: make class for config
# todo: settings system for global hosting
#       where to allow/disallow eval: channel, user, role
#       docs lookup sources
# todo: python resources commands
#       port docs lookup
#       stackoverflow error search
# todo: allow message links as eval input
# todo: create privileged eval command for owner only
# todo: docker image
# todo: setup.py
# todo: bug fix 3


__version__ = "1.8.0"


CONFIG_PATH = Path("config.toml")
LOG_PATH = Path("info.log")


stream_handler = logging.StreamHandler(stream=sys.stdout)
file_handler = logging.FileHandler(LOG_PATH, encoding="utf_8")
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        stream_handler,
        file_handler,
    ],
)
log = logging.getLogger(__name__)


def get_config() -> dict:
    with open(CONFIG_PATH, "rb") as config_file:
        config = tomllib.load(config_file)
    return config


def main():
    """Run an instance of the bot with config loaded from the toml file."""
    config = get_config()

    snakeboxed_bot = snakeboxed.Snakeboxed(
        snekbox_url=config["settings"]["snekbox_url"],
        command_prefix=commands.when_mentioned_or(
            *config["settings"]["command_prefixes"]
        ),
    )

    snakeboxed_bot.run(config["auth"]["token"])


if __name__ == "__main__":
    main()
