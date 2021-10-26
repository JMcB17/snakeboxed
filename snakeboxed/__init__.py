"""Simple Discord bot for snekbox (sandboxed Python code execution), self-host or use a global instance."""


import sys
import logging as log
from pathlib import Path


import toml
from discord.ext import commands

import snakeboxed.cogs
from snakeboxed.bot import Snakeboxed


# todo: sublicense as gnu gplv3
# todo: make class for config
# todo: settings system for global hosting
#       where to allow/disallow eval: channel, user, role
#       docs lookup sources
# todo: 'bug fix'
# todo: python resources commands
#       link to tutorial and stuff
#       port docs lookup
#       stackoverflow error search
# todo: exec as alias of eval
# todo: credits command
# todo: allow .py text files as eval input
# todo: allow message links as eval input
# todo: lazy log formatting? ehhhh
# todo: create privileged eval command for owner only
# todo: fix update command using pm2 pull
# todo: docker image
# todo: expand readme
#       installation instructions
#       usage instructions
#       credits - as with any programming, most the work was done for me


__version__ = '1.5.1'


CONFIG_PATH = Path('config.toml')
LOG_PATH = Path('info.log')


stream_handler = log.StreamHandler(stream=sys.stdout)
file_handler = log.FileHandler(LOG_PATH, encoding='utf_8')
log.basicConfig(
    level=log.INFO,
    handlers=[
        stream_handler,
        file_handler,
    ]
)


def get_config() -> dict:
    with open(CONFIG_PATH, encoding='utf_8') as config_file:
        config = toml.load(config_file)
    return config


def main():
    """Run an instance of the bot with config loaded from the toml file."""
    config = get_config()

    bot = snakeboxed.bot.Snakeboxed(
        command_prefix=commands.when_mentioned_or(*config['settings']['command_prefixes'])
    )

    snekbox_cog = snakeboxed.cogs.Snekbox(
        bot,
        snekbox_url=config['settings']['snekbox_url'],
        snekbox_port=config['settings']['snekbox_port']
    )
    bot.add_cog(snekbox_cog)
    info_cog = snakeboxed.cogs.SnakeboxedInfo(bot)
    bot.add_cog(info_cog)

    bot.run(config['auth']['token'])


if __name__ == '__main__':
    main()
