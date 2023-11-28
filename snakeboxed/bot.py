import logging
from typing import Optional

import aiohttp
from discord import Intents
from discord.ext import commands

import snakeboxed

log = logging.getLogger(__name__)

INTENTS = Intents.default()
INTENTS.message_content = True


class Snakeboxed(commands.Bot):
    """Custom Bot class for the Snekbox cog.

    Adds http_session as an attribute, which is an aiohttp.ClientSession required by the Snekbox cog.
    Also uses a help command with a custom no_category.
    """

    def __init__(self, snekbox_url: str, *args, **kwargs):
        self.snekbox_url = snekbox_url
        # assigned in on_ready for async
        self.http_session: Optional[aiohttp.ClientSession] = None

        kwargs.setdefault(
            "help_command", commands.DefaultHelpCommand(no_category="Help")
        )
        super().__init__(*args, **kwargs, intents=INTENTS)

    async def setup_hook(self):
        self.http_session = aiohttp.ClientSession()

        # add all relevant cogs
        owner_cog = snakeboxed.cogs.Owner(self)
        await self.add_cog(owner_cog)
        python_info_cog = snakeboxed.cogs.PythonInfo(self)
        await self.add_cog(python_info_cog)
        snakeboxed_info_cog = snakeboxed.cogs.SnakeboxedInfo(self)
        await self.add_cog(snakeboxed_info_cog)
        snekbox_cog = snakeboxed.cogs.Snekbox(self, snekbox_url=self.snekbox_url)
        await self.add_cog(snekbox_cog)

    async def on_ready(self):
        log.info(f"ready as {self.user.name}")

    async def close(self):
        await self.http_session.close()
        await super().close()
