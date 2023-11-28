from discord.ext import commands


PYTHON_RESOURCES_HELP = """\
https://www.python.org/
Official Tutorial:
<https://docs.python.org/3/tutorial/>
Built-ins:
<https://docs.python.org/3/library/functions.html>
<https://docs.python.org/3/library/stdtypes.html>
<https://docs.python.org/3/library/exceptions.html>
<https://docs.python.org/3/library/index.html>

https://www.pythondiscord.com/resources/
"""


class PythonInfo(commands.Cog):
    """Information about the Python programming language like resources and docs lookup."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    qualified_name = "Python Info"

    @commands.command(name="resources", aliases=["python-resources", "pr", "r"])
    async def python_resources(self, ctx: commands.Context):
        """Send some links to Python tutorials, documentation etc."""
        return await ctx.send(PYTHON_RESOURCES_HELP)
