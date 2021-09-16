import io
from typing import Optional, Tuple
import discord
from discord.ext import commands
import asyncio
import sys
from discord.member import Member
from discord.player import FFmpegPCMAudio
from obj import Musex

emoji = "\U00002705"

async def in_vc(ctx: commands.Context):
    vc = ctx.voice_client
    if not vc:
        author_vc = ctx.author.voice
        if author_vc:
            if isinstance(author_vc.channel, discord.VoiceChannel):
                await author_vc.channel.connect()
                return True
    elif ctx.author.voice and ctx.author.voice.channel != vc.channel:
        return False
    return True

class Music(commands.Cog):

    bot: Musex

    def __init__(self, bot: Musex):
        self.bot = bot

    @staticmethod
    async def compute(url: str) -> Optional[Tuple[str, FFmpegPCMAudio]]:
        executable = "ffmpeg" if "win" not in sys.platform else "avconv"
        arg = url if url.startswith("https://") and len(url.split() == 1) else f"ytsearch1:{url}"
        print(arg)
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{arg}\" --skip-download --get-title",
            stderr = asyncio.subprocess.PIPE
        )
        _, title = await proc.communicate()
        print(title, _)
        if not title:
            return
        title = title.decode().split("\n")[0]
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{arg}\" -f 251 -o -",
            stdin = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        # proc = await asyncio.create_subprocess_shell(
        #     f"{executable} -f webm -i pipe:0 -f mp3 pipe:1",
        #     stdin=asyncio.subprocess.PIPE,
        #     stdout=asyncio.subprocess.PIPE
        # )
        # stdout, _ = await proc.communicate(stdout)
        source = FFmpegPCMAudio(io.BytesIO(stdout), executable=executable, pipe=True)
        return title, source

    @commands.command()
    @commands.guild_only()
    @commands.check(in_vc)
    async def play(self, ctx: commands.Context, *, url: str):
        voice_client: discord.VoiceClient = ctx.voice_client

        if voice_client.is_playing():
            ret = await self.compute(url)
            if not ret:
                return await ctx.send("Not found")
            title, src = ret
            await ctx.send(f"Added **{title}** to queue")
            return self.bot.queue.append(src)

        def after(err: Optional[Exception]) -> None:
            if err:
                return print(repr(err))
            queue = self.bot.queue
            if len(queue):
                next_music = queue.popleft()
                voice_client.play(next_music, after=after)
        
        ret = await self.compute(url)
        if not ret:
            return await ctx.send("Not found")
        title, src = ret
        await ctx.send(f"Added **{title}** to queue")
        voice_client.play(src, after=after)
    
    # @commands.command()
    # @commands.guild_only()
    # async def skip(self, ctx: commands.Context):
    #     voice_client: Optional[discord.VoiceClient] = ctx.voice_client
    #     if not voice_client:
    #         return await ctx.send("Not in any voice channel")
        
    #     elif not voice_client.is_playing():
    #         return await ctx.send("Not playing anything")
        
    #     channel: discord.VoiceChannel = voice_client.channel
    #     members = channel.members
    #     members.remove(ctx.me)
    #     count = len(members)-1
    #     n = 0
    #     if not n < count:
    #         fmt = "Skip? ({}/{})"
    #         msg = await ctx.send(fmt.format(n, count))
    #         while count > 0:
    #             event = await self.bot.wait_for("reaction_add", lambda r, u: hasattr(u, "guild") and r.message == msg and str(r.emoji) == emoji)
    #             reaction: discord.Reaction = event[0]
    #             member: discord.Member = event[1]
    #             await msg.edit(fmt.format(n, count))
    #     await ctx.send("Skipping")


def setup(bot):
    bot.add_cog(Music(bot))
    print("Loaded music")
