import logging

import aiohttp
from discord.ext import commands

log = logging.getLogger(__name__)


class Snakeboxed(commands.Bot):
    """Custom Bot class for the Snekbox cog.

    Adds http_session as an attribute, which is an aiohttp.ClientSession required by the Snekbox cog.
    Also uses a help command with a custom no_category.
    """

    def __init__(self, *args, **kwargs):
        # assigned in on_ready for async
        self.http_session = None

        kwargs.setdefault(
            "help_command", commands.DefaultHelpCommand(no_category="Help")
        )
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        self.http_session = aiohttp.ClientSession()
        log.info(f"ready as {self.user.name}")

    async def close(self):
        await super().close()
        if self.http_session is not None:
            await self.http_session.close()
