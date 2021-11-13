from typing import Optional

import steganographr
from discord.ext import commands


class Steganographr(commands.Cog):
    """Hide text in plain sight using invisible zero-width characters."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def encode(self, ctx: commands.Context, public: str, private: str):
        """Hide a private message within a public message."""
        return await ctx.send(steganographr.encode(public, private))

    @commands.command()
    async def decode(self, ctx: commands.Context, *, public: Optional[str]):
        """Reveal the private message hidden within a public message."""
        if public is not None:
            pass
        elif ctx.message.reference:
            public = ctx.message.reference.resolved.content
        else:
            return

        return await ctx.send(steganographr.decode(public))
