import re
from pathlib import Path

import discord
import toml
from discord.ext import commands


# todo: sublicense as gnu gplv3
# todo: make class for config


__version__ = '0.1.0'


ESCAPE_REGEX = re.compile("[`\u202E\u200B]{3,}")
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"        # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"    # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"                        # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all code inside the markup
    r"\s*"                                  # any more whitespace before the end of the code markup
    r"(?P=delim)",                          # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE               # "." also matches newlines, case insensitive
)
RAW_CODE_REGEX = re.compile(
    r"^(?:[ \t]*\n)*"                       # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all the rest as code
    r"\s*$",                                # any trailing whitespace until the end of the string
    re.DOTALL                               # "." also matches newlines
)

MAX_PASTE_LEN = 10000

CONFIG_PATH = Path('config.toml')


class SnakeboxedBot(commands.Bot):
    async def on_ready(self):
        print(f'ready as {self.user.name}')


def main():
    with open(CONFIG_PATH) as config_file:
        config = toml.load(config_file)

    bot = SnakeboxedBot(command_prefix='!')
    bot.run(config['auth']['token'])


if __name__ == '__main__':
    main()
