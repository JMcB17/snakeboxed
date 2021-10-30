import json
import logging
from pathlib import Path

import aiohttp
import discord.utils
from discord.ext import commands

import snakeboxed


UPDATE_FILE_PATH = Path('update.json')


log = logging.getLogger(__name__)


class Snakeboxed(commands.Bot):
    """Custom Bot class for the Snekbox cog.

    Adds http_session as an attribute, which is an aiohttp.ClientSession required by the Snekbox cog.
    Also uses a help command with a custom no_category.
    """

    def __init__(self, *args, **kwargs):
        # assigned in on_ready for async
        self.http_session = None

        kwargs.setdefault('help_command', commands.DefaultHelpCommand(no_category='Help'))
        super().__init__(*args, **kwargs)

    async def post_update(self):
        if not UPDATE_FILE_PATH.is_file():
            return
        with open(UPDATE_FILE_PATH) as update_file:
            update_location_ids = json.load(update_file)
        UPDATE_FILE_PATH.unlink()

        update_guild: discord.Guild = self.get_guild(update_location_ids['guild'])
        if update_guild is None:
            return

        update_channel: discord.TextChannel = discord.utils.get(
            update_guild.channels, id=update_location_ids['channel']
        )
        if update_channel is None:
            return

        return await update_channel.send(snakeboxed.__version__)

    async def on_ready(self):
        self.http_session = aiohttp.ClientSession()
        await self.post_update()
        log.info(f'ready as {self.user.name}')

    async def close(self):
        await super().close()
        if self.http_session is not None:
            await self.http_session.close()
