import asyncio
import contextlib
import datetime
import io
import logging
import re
import textwrap
from functools import partial
from signal import Signals
from typing import Optional, Tuple

import discord
from discord.ext import commands

from snakeboxed.bot import Snakeboxed

ESCAPE_REGEX = re.compile("[`\u202E\u200B]{3,}")
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"  # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"  # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all code inside the markup
    r"\s*"  # any more whitespace before the end of the code markup
    r"(?P=delim)",  # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE,  # '.' also matches newlines, case insensitive
)
RAW_CODE_REGEX = re.compile(
    r"^(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all the rest as code
    r"\s*$",  # any trailing whitespace until the end of the string
    re.DOTALL,  # '.' also matches newlines
)
PYTHON_CONTENT_TYPE = re.compile("text/x-python; charset=([a-z0-9-_]+)")

SIGKILL = 9
REEVAL_EMOJI = "\U0001f501"  # :repeat:
REEVAL_TIMEOUT = 30

MAX_DISCORD_FILE_LENGTH_BYTES = 8 * (10**6)  # 8MB
DISCORD_FILE_NAME = "output.txt"


log = logging.getLogger(__name__)


class Snekbox(commands.Cog):
    """Safe evaluation of Python code using Snekbox."""

    qualified_name = "Snekbox"

    def __init__(self, bot: Snakeboxed, snekbox_url: str):
        self.bot = bot
        self.jobs = {}

        self.snekbox_url = snekbox_url
        self.snekbox_eval_api_url = f"{self.snekbox_url}/eval"

    async def post_eval(self, code: str) -> dict:
        """Send a POST request to the Snekbox API to evaluate code and return the results."""
        url = self.snekbox_eval_api_url
        data = {"input": code}
        async with self.bot.http_session.post(
            url, json=data, raise_for_status=True
        ) as resp:
            return await resp.json()

    @staticmethod
    async def output_to_discord_file(output: str) -> Optional[discord.File]:
        """Upload the eval output to a Discord file and return it if successful."""
        log.info("Uploading full output to Discord file...")

        output_bytes = output.encode(encoding="utf_8")
        if len(output_bytes) > MAX_DISCORD_FILE_LENGTH_BYTES:
            log.info("Full output is too long to upload")
            output_bytes = b"too long to upload"

        output_bytes_io = io.BytesIO(output_bytes)
        output_bytes_io.seek(0)
        output_discord_file = discord.File(output_bytes_io, filename=DISCORD_FILE_NAME)

        return output_discord_file

    @staticmethod
    async def code_from_attachments(message: discord.Message) -> Optional[str]:
        for attachment in message.attachments:
            content_type_match = re.match(PYTHON_CONTENT_TYPE, attachment.content_type)
            if content_type_match:
                encoding = content_type_match.group(1)
                attachment_bytes = await attachment.read()
                return attachment_bytes.decode(encoding=encoding)

    @staticmethod
    def prepare_input(code: str) -> str:
        """
        Extract code from the Markdown, format it, and insert it into the code template.
        If there is any code block, ignore text outside the code block.
        Use the first code block, but prefer a fenced code block.
        If there are several fenced code blocks, concatenate only the fenced code blocks.
        """
        if match := list(FORMATTED_CODE_REGEX.finditer(code)):
            blocks = [block for block in match if block.group("block")]

            if len(blocks) > 1:
                code = "\n".join(block.group("code") for block in blocks)
                info = "several code blocks"
            else:
                match = match[0] if len(blocks) == 0 else blocks[0]
                code, block, lang, delim = match.group("code", "block", "lang", "delim")
                if block:
                    info = (
                        f"'{lang}' highlighted" if lang else "plain"
                    ) + " code block"
                else:
                    info = f"{delim}-enclosed inline code"
        else:
            code = RAW_CODE_REGEX.fullmatch(code).group("code")
            info = "unformatted or badly formatted code"

        code = textwrap.dedent(code)
        log.info(f"Extracted {info} for evaluation:\n{code}")
        return code

    @staticmethod
    def get_results_message(results: dict) -> Tuple[str, str]:
        """Return a user-friendly message and error corresponding to the process's return code."""
        stdout, returncode = results["stdout"], results["returncode"]
        msg = f"Your eval job has completed with return code {returncode}"
        error = ""

        if returncode is None:
            msg = "Your eval job has failed"
            error = stdout.strip()
        elif returncode == 128 + SIGKILL:
            msg = "Your eval job timed out or ran out of memory"
        elif returncode == 255:
            msg = "Your eval job has failed"
            error = "A fatal NsJail error occurred"
        else:
            # Try to append signal's name if one exists
            try:
                name = Signals(returncode - 128).name
                msg = f"{msg} ({name})"
            except ValueError:
                pass

        return msg, error

    @staticmethod
    def get_status_emoji(results: dict) -> str:
        """Return an emoji corresponding to the status code or lack of output in result."""
        if not results["stdout"].strip():  # No output
            return ":warning:"
        elif results["returncode"] == 0:  # No error
            return ":white_check_mark:"
        else:  # Exception
            return ":x:"

    async def format_output(self, output: str) -> Tuple[str, Optional[discord.File]]:
        """
        Format the output and return a tuple of the formatted output and a URL to the full output.
        Prepend each line with a line number. Truncate if there are over 10 lines or 1000 characters
        and upload the full output to a Discord file.
        """
        log.info("Formatting output...")

        output = output.rstrip("\n")
        original_output = output  # To be uploaded to a Discord file if needed
        discord_file = None

        if "<@" in output:
            output = output.replace("<@", "<@\u200B")  # Zero-width space

        if "<!@" in output:
            output = output.replace("<!@", "<!@\u200B")  # Zero-width space

        if ESCAPE_REGEX.findall(output):
            discord_file = await self.output_to_discord_file(original_output)
            return (
                "Code block escape attempt detected; will not output result",
                discord_file,
            )

        truncated = False
        lines = output.count("\n")

        if lines > 0:
            output = [
                f"{i:03d} | {line}" for i, line in enumerate(output.split("\n"), 1)
            ]
            output = output[:11]  # Limiting to only 11 lines
            output = "\n".join(output)

        if lines > 10:
            truncated = True
            if len(output) >= 1000:
                output = "... (truncated - too long, too many lines)"
            else:
                output = "... (truncated - too many lines)"
        elif len(output) >= 1000:
            truncated = True
            output = "... (truncated - too long)"

        if truncated:
            discord_file = await self.output_to_discord_file(original_output)

        output = output or "[No output]"

        return output, discord_file

    async def send_eval(self, ctx: commands.Context, code: str) -> discord.Message:
        """
        Evaluate code, format it, and send the output to the corresponding channel.
        Return the bot response.
        """
        async with ctx.typing():
            results = await self.post_eval(code)
            msg, error = self.get_results_message(results)

            if error:
                output, discord_file = error, None
            else:
                output, discord_file = await self.format_output(results["stdout"])

            icon = self.get_status_emoji(results)
            msg = f"{ctx.author.mention} {icon} {msg}.\n\n```\n{output}\n```"
            if discord_file:
                response = await ctx.send(f"{msg}\nFull output: ", file=discord_file)
            else:
                response = await ctx.send(msg)

            log.info(f"{ctx.author}'s job had a return code of {results['returncode']}")
        return response

    async def continue_eval(
        self, ctx: commands.Context, response: discord.Message
    ) -> Optional[str]:
        """
        Check if the eval session should continue.
        Return the new code to evaluate or None if the eval session should be terminated.
        """
        _predicate_eval_message_edit = partial(predicate_eval_message_edit, ctx)
        _predicate_emoji_reaction = partial(predicate_eval_emoji_reaction, ctx)

        with contextlib.suppress(discord.NotFound):
            try:
                _, new_message = await self.bot.wait_for(
                    "message_edit",
                    check=_predicate_eval_message_edit,
                    timeout=REEVAL_TIMEOUT,
                )
                await ctx.message.add_reaction(REEVAL_EMOJI)
                await self.bot.wait_for(
                    "reaction_add", check=_predicate_emoji_reaction, timeout=10
                )

                code = await self.get_code(new_message)
                await ctx.message.clear_reaction(REEVAL_EMOJI)
                with contextlib.suppress(discord.HTTPException):
                    await response.delete()

            except asyncio.TimeoutError:
                await ctx.message.clear_reaction(REEVAL_EMOJI)
                return None

            return code

    async def get_code(self, message: discord.Message) -> Optional[str]:
        """
        Return the code from `message` to be evaluated.
        If the message is an invocation of the eval command, return the first argument or None if it
        doesn't exist. Otherwise, return the full content of the message.
        """
        log.info(f"Getting context for message {message.id}.")
        new_ctx = await self.bot.get_context(message)

        if new_ctx.command is self.eval_command:
            log.info(f"Message {message.id} invokes eval command.")
            split = message.content.split(maxsplit=1)
            code = split[1] if len(split) > 1 else None
        else:
            log.info(f"Message {message.id} does not invoke eval command.")
            code = message.content

        return code

    @commands.command(name="eval", aliases=("e", "exec"))
    async def eval_command(self, ctx: commands.Context, *, code: str = None):
        """
        Run Python code and get the results.
        This command supports multiple lines of code, including code wrapped inside a formatted code
        block. Code can be re-evaluated by editing the original message within 10 seconds and
        clicking the reaction that subsequently appears.
        We've done our best to make this sandboxed, but do let us know if you manage to find an
        issue with it!
        """
        if ctx.author.id in self.jobs:
            await ctx.send(
                f"{ctx.author.mention} You've already got a job running - "
                "please wait for it to finish!"
            )
            return

        skip_input_prep = False
        if not code:
            code = await self.code_from_attachments(ctx.message)
            skip_input_prep = True

        if not code:  # None or empty string
            return await ctx.send_help(ctx.command)

        log.info(
            f"Received code from "
            f"{ctx.author} ({ctx.author.id}) "
            f"in {ctx.guild} ({ctx.guild.id}) for evaluation:\n"
            f"{code}"
        )

        while True:
            self.jobs[ctx.author.id] = datetime.datetime.now()
            if not skip_input_prep:
                code = self.prepare_input(code)
            try:
                response = await self.send_eval(ctx, code)
            finally:
                del self.jobs[ctx.author.id]

            code = await self.continue_eval(ctx, response)
            if not code:
                break
            log.info(f"Re-evaluating code from message {ctx.message.id}:\n{code}")


def predicate_eval_message_edit(
    ctx: commands.Context, old_msg: discord.Message, new_msg: discord.Message
) -> bool:
    """Return True if the edited message is the context message and the content was indeed modified."""
    return new_msg.id == ctx.message.id and old_msg.content != new_msg.content


def predicate_eval_emoji_reaction(
    ctx: commands.Context, reaction: discord.Reaction, user: discord.User
) -> bool:
    """Return True if the reaction REEVAL_EMOJI was added by the context message author on this message."""
    return (
        reaction.message.id == ctx.message.id
        and user.id == ctx.author.id
        and str(reaction) == REEVAL_EMOJI
    )
