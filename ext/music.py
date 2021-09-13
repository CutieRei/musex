import io
from discord.ext import commands
import asyncio

from discord.player import FFmpegPCMAudio

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def compute(url: str):
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{url}\" -f 251 -o -",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        stdout, _ = proc.communicate()
        proc.kill()
        proc = await asyncio.create_subprocess_shell(
            "ffmpeg -f webm -i pipe:0 -f mp3 pipe:1",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        await proc.wait()
        source = FFmpegPCMAudio(io.BytesIO(stdout))
        return source



    @commands.is_owner()
    @commands.command()
    async def play(self, ctx, url):
        await ctx.send(self.compute(url))


def setup(bot):
    bot.add_cog(Music)
    print("Loaded music")
