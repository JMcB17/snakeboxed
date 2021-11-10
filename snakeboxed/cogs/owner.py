import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

import snakeboxed


UPDATE_FILE_PATH = Path('update.json')
REQUIREMENTS_FILE_PATH = Path('requirements.txt')


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot, pm2_name: str, pm2_binary: str):
        self.bot = bot
        self.pm2_name = pm2_name
        self.pm2_binary = pm2_binary

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner('You do not own this bot.')
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        await self.post_update()

    @commands.command(hidden=True, aliases=['u'])
    async def update(self, ctx: commands.Context, commit_id: Optional[str]):
        """Update the bot."""
        await ctx.send(snakeboxed.__version__)

        with open(UPDATE_FILE_PATH, 'w') as update_file:
            json.dump(
                {
                    'guild': ctx.guild.id,
                    'channel': ctx.channel.id,
                },
                update_file
            )

        pip_upgrade_command = [sys.executable, '-m', 'pip', 'install', '-r', str(REQUIREMENTS_FILE_PATH)]
        pull_command = [str(self.pm2_binary), 'pull', self.pm2_name]
        if commit_id is not None:
            pull_command.append(commit_id)

        for command in pip_upgrade_command, pull_command:
            await ctx.send(f"```bash\n{' '.join(command)}\n```")
            # capture all output in command result stdout together
            command_result_bytes = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            command_result = command_result_bytes.stdout.decode(encoding='utf-8')
            await ctx.send(f'```\n{command_result}\n```')

    async def post_update(self):
        if not UPDATE_FILE_PATH.is_file():
            return
        with open(UPDATE_FILE_PATH) as update_file:
            update_location_ids = json.load(update_file)
        UPDATE_FILE_PATH.unlink()

        update_guild: discord.Guild = self.bot.get_guild(update_location_ids['guild'])
        if update_guild is None:
            return

        update_channel: discord.TextChannel = discord.utils.get(
            update_guild.channels, id=update_location_ids['channel']
        )
        if update_channel is None:
            return

        return await update_channel.send(snakeboxed.__version__)
