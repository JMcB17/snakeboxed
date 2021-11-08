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
    async def decode(self, ctx: commands.Context, *, public: str):
        """Reveal the private message hidden within a public message."""
        return await ctx.send(steganographr.decode(public))
