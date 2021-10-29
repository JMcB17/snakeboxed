import subprocess
from typing import Optional

from discord.ext import commands

import snakeboxed


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot, pm2_name: str):
        self.bot = bot
        self.pm2_name = pm2_name

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('You do not own this bot.')
        return True

    @commands.command(hidden=True, aliases=['u'])
    async def update(self, ctx: commands.Context, commit_id: Optional[str]):
        """Update the bot."""
        await ctx.send(snakeboxed.__version__)

        pull_command_list = ['pm2', 'pull', self.pm2_name]
        if commit_id is not None:
            pull_command_list.append(commit_id)

        pull_command = ' '.join(pull_command_list)
        await ctx.send(f'```bash\n{pull_command}\n```')
        # capture all output in command result stdout together
        command_result_bytes = subprocess.run(
            pull_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        command_result = command_result_bytes.stdout.decode(encoding='utf_8')
        await ctx.send(f'```\n{command_result}\n```')
