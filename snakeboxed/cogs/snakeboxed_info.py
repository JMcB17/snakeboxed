import asyncio
from pathlib import Path

import discord
from discord.ext import commands

import snakeboxed


GITHUB_LINK = 'https://github.com/JMcB17/snakeboxed'
CREATOR_DISCORD_NAME = 'JMcB#7918'
BOT_PERMISSIONS = {
    'read_messages': True,
    'send_messages': True,
    'add_reactions': True,
    'attach_files': True,
    'manage_messages': True,
}
CREDITS = """\
As with any programming, most of the work was done for me.

Snekbox:
<https://github.com/python-discord/snekbox>
Code taken from python-discord/bot under the \
[Expat License/MIT License](https://github.com/JMcB17/snakeboxed/blob/main/LICENSE-THIRD-PARTY):
<https://github.com/python-discord/bot>
<https://github.com/python-discord/bot/blob/main/bot/exts/utils/snekbox.py>
"""
SECRET_PATH = Path('assets/secret/')


class SnakeboxedInfo(commands.Cog):
    """Information about Snakeboxed bot."""
    qualified_name = 'Snakeboxed Info'

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='github', aliases=['github-link', 'git', 'source'])
    async def send_github_link(self, ctx: commands.Context):
        """Send the GitHub link for this bot's source code."""
        return await ctx.send(f'<{GITHUB_LINK}>')

    @commands.command(name='bugs', aliases=['bug', 'report-bug', 'report-bugs', 'bug-report'])
    async def send_bug_report_links(self, ctx: commands.Context):
        """Send info on reporting bugs."""
        bug_report_msg = (
            'Message me on Discord: \n'
            f'{CREATOR_DISCORD_NAME}\n '
            'Open an issue on GitHub:\n '
            f'<{GITHUB_LINK}/issues/new>'
        )
        return await ctx.send(bug_report_msg)

    @commands.command(name='version', aliases=['V'])
    async def send_version_number(self, ctx: commands.Context):
        """Send the current version number for this bot."""
        return await ctx.send(snakeboxed.__version__)

    @commands.command()
    async def credits(self, ctx: commands.Context):
        """Send credits for this bot."""
        embed = discord.Embed(description=CREDITS)
        return await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def coolsville(self, ctx: commands.Context):
        """I think Coolsville sucks!

        No! Hey! You're doing that thing again where you take everything I say out of context!
        You're trying to make it look like I think Coolsville sucks! No! Don't record that!
        """
        return await ctx.send('You think Coolsville sucks?', file=discord.File('assets/secret/coolsville.png'))

    @commands.command(name='poggers', aliases=['pog', 'lilianpoggers', 'lilianpog' 'lp'], hidden=True)
    async def lilian_poggers(self, ctx: commands.Context, f: str = 'ogg'):
        """???"""
        fp_no_suffix = SECRET_PATH / 'lilian_poggers'
        # ppl might use .mp4 for example
        f = f.strip('.')
        fp = fp_no_suffix.with_suffix(f'.{f}')

        if fp.is_file():
            return await ctx.send(file=discord.File(fp))

    @commands.command(hidden=True)
    async def has(self, ctx: commands.Context):
        """what"""
        if await ctx.bot.is_owner(ctx.author):
            return await ctx.send('yeah I do lol')
        else:
            return await ctx.send('what')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content.casefold() == 'el muchacho':
            return await message.channel.send('https://youtu.be/GdtuG-j9Xog')

    @commands.command(hidden=True, name='updateday')
    async def update_day(self, ctx: commands.Context):
        """Matt! Update day! New Wii titles!

        Super Mario RPG
        Sonic the Hedgehog, Donkey Kong 3
        Adventures of Lolo 1 and 2
        King's Knight, Dig Dug, Chew Man Fu

        Harvest Moon
        League Puzzle Pokémon
        ToeJam & Earl in Panic on Funkotron

        Castlevania, Fatal Fury, Ninja JaJaMaru-kun
        ActRaiser, Blazing Lazers, Bases Loaded, Mega Turrican
        Cybernator, Rolling Thunder, Dynastic Hero
        Bubble Bobble, Double Dribble, Double Dragon, F-Zero

        F-Zero X, and
        Donkey Kong Jr. Math!

        Ninja Gaiden 1
        Ninja Gaiden 2
        Ninja Gaiden 3
        Cruis'n USA
        """
        fp = SECRET_PATH / 'update_day.ogg'

        if ctx.author.voice is not None and ctx.author.voice.channel is not None:
            source = await discord.FFmpegOpusAudio.from_probe(fp)
            voice_client = await ctx.author.voice.channel.connect()

            def after(error: Exception):
                if error is not None:
                    raise error
                asyncio.run(voice_client.disconnect())
            voice_client.play(source, after=after)

    @commands.command(name='prefix', aliases=['prefixes', 'bot-prefix', 'bot-prefixes'])
    async def send_bot_prefixes(self, ctx: commands.Context):
        """Send the command prefixes for this bot.

        Command prefixes are separated by newlines.
        """
        prefixes_list = ctx.bot.command_prefix(ctx.bot, ctx.message)
        prefixes_list_no_role = [p for p in prefixes_list if '<@!' not in p]
        prefixes = '\n'.join(prefixes_list_no_role)
        return await ctx.send(prefixes)

    @commands.command(name='invite', aliases=['bot-invite', 'invite-bot'])
    async def send_bot_invite(self, ctx: commands.Context):
        """Send a Discord bot invite for this bot.

        Uses the bot's current client id and some required permissions.
        """
        app_info = await self.bot.application_info()
        client_id = app_info.id

        permissions = discord.Permissions()
        permissions.update(**BOT_PERMISSIONS)

        invite_url = discord.utils.oauth_url(client_id, permissions, ctx.guild)
        await ctx.send(invite_url)
