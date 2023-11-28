import json
import sys
from pathlib import Path

import discord
from discord.ext import commands

import snakeboxed

UPDATE_FILE_PATH = Path("update.json")


class Owner(commands.Cog):
    # todo cog base superclass with bot attribute
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You do not own this bot.")
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        await self.post_update()

    @commands.command(hidden=True, aliases=["u"])
    async def update(self, ctx: commands.Context, exit_code: int = 0):
        """Update the bot."""
        await ctx.send(snakeboxed.__version__)

        with open(UPDATE_FILE_PATH, "w") as update_file:
            json.dump(
                {
                    "guild": ctx.guild.id,
                    "channel": ctx.channel.id,
                },
                update_file,
            )

        # todo use bot.close instead maybe?
        #      or handle SystemExit in runner
        sys.exit(exit_code)

    async def post_update(self):
        if not UPDATE_FILE_PATH.is_file():
            return
        with open(UPDATE_FILE_PATH) as update_file:
            update_location_ids = json.load(update_file)
        UPDATE_FILE_PATH.unlink()

        update_guild: discord.Guild = self.bot.get_guild(update_location_ids["guild"])
        if update_guild is None:
            return

        update_channel: discord.TextChannel = discord.utils.get(
            update_guild.channels, id=update_location_ids["channel"]
        )
        if update_channel is None:
            return

        return await update_channel.send(snakeboxed.__version__)
