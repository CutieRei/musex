import io
import discord
from discord.ext import commands
import asyncio
import sys

from discord.player import FFmpegPCMAudio

async def in_vc(ctx: commands.Context):
    vc = ctx.voice_client
    if not vc:
        author_vc = ctx.author.voice
        if author_vc:
            if isinstance(author_vc.channel, discord.VoiceChannel):
                await author_vc.channel.connect()
                return True
    return False

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def compute(url: str):
        executable = "ffmpeg" if "win" not in sys.platform else "avconv"
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{url}\" -f 251 -o -",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        proc.kill()
        proc = await asyncio.create_subprocess_shell(
            f"{executable} -f webm -i pipe:0 -f mp3 pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate(stdout)
        source = FFmpegPCMAudio(io.BytesIO(stdout), executable=executable, pipe=True)
        return source

    @commands.command()
    @commands.check(in_vc)
    async def play(self, ctx: commands.Context, url: str):
        voice_client: discord.VoiceClient = ctx.voice_client
        voice_client.play(await self.compute(url))


def setup(bot):
    bot.add_cog(Music(bot))
    print("Loaded music")
