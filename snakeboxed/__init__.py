"""Simple Discord bot for snekbox (sandboxed Python code execution), self-host or use a global instance."""


import logging
import sys
from pathlib import Path

import toml
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


__version__ = "1.7.1"


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
    with open(CONFIG_PATH, encoding="utf_8") as config_file:
        config = toml.load(config_file)
    return config


def main():
    """Run an instance of the bot with config loaded from the toml file."""
    config = get_config()

    snakeboxed_bot = snakeboxed.Snakeboxed(
        command_prefix=commands.when_mentioned_or(
            *config["settings"]["command_prefixes"]
        )
    )

    # add all relevant cogs
    owner_cog = snakeboxed.cogs.Owner(
        snakeboxed_bot,
        pm2_name=config["settings"]["pm2_name"],
        pm2_binary=config["settings"]["pm2_binary"],
    )
    snakeboxed_bot.add_cog(owner_cog)
    python_info_cog = snakeboxed.cogs.PythonInfo(snakeboxed_bot)
    snakeboxed_bot.add_cog(python_info_cog)
    snakeboxed_info_cog = snakeboxed.cogs.SnakeboxedInfo(snakeboxed_bot)
    snakeboxed_bot.add_cog(snakeboxed_info_cog)
    snekbox_cog = snakeboxed.cogs.Snekbox(
        snakeboxed_bot,
        snekbox_url=config["settings"]["snekbox_url"],
        snekbox_port=config["settings"]["snekbox_port"],
    )
    snakeboxed_bot.add_cog(snekbox_cog)

    snakeboxed_bot.run(config["auth"]["token"])


if __name__ == "__main__":
    main()
