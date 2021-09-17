import io
from typing import List, Optional, Tuple, Union
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
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: discord.VoiceState, after: discord.VoiceState):
        if member == self.bot.user:
            if after.channel == None:
                self.bot.queue.clear()

    @staticmethod
    async def compute(url: str) -> Optional[Tuple[str, FFmpegPCMAudio]]:
        executable = "ffmpeg" if "win" not in sys.platform else "avconv"
        arg = url if url.startswith("https://") and len(url.split()) == 1 else f"ytsearch1:{url}"
        print(arg)
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{arg}\" --skip-download --get-title",
            stdout = asyncio.subprocess.PIPE
        )
        title, _ = await proc.communicate()
        print(title)
        if not title:
            return
        title = title.decode().split("\n")[0]
        proc = await asyncio.create_subprocess_shell(
            f"youtube-dl \"{arg}\" -f 251 -o -",
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

    @commands.command(aliases=["dc", "leave"])
    @commands.guild_only()
    async def disconnect(self, ctx: commands.Context):
        voice_client: Optional[discord.VoiceClient] = ctx.voice_client
        if not voice_client:
            return await ctx.send("Not in a voice channel")
        author_vc = ctx.author.voice
        if author_vc.channel is not None and author_vc.channel == voice_client.channel:
            return await voice_client.disconnect()
        await ctx.send("You're not connected to a voice channel")
    
    @commands.command(aliases=["q"])
    @commands.guild_only()
    async def queue(self, ctx: commands.Context):
        queue: List[Tuple[str, FFmpegPCMAudio, Union[discord.User, discord.Member]]] = list(self.bot.queue)
        desc = "\n".join(f"{c+1}. **{t[0]}** requested by **{t[2].mention}({t[2]})**" for c,t in enumerate(queue))
        embed = discord.Embed(
            color = ctx.author.color,
            title = "Music Queue",
            description = desc or "\*cricket noise\*"
        )
        await ctx.send(embed=embed)


    @commands.command()
    @commands.guild_only()
    @commands.check(in_vc)
    async def play(self, ctx: commands.Context, *, url: str):
        voice_client: Optional[discord.VoiceClient] = ctx.voice_client

        def after(err: Optional[Exception]) -> None:
            if err:
                return print(repr(err))
            queue = self.bot.queue
            if len(queue):
                _, next_music, _ = queue.popleft()
                voice_client.play(next_music, after=after)

        if voice_client.is_playing():
            if len(self.bot.queue) >= 20:
                return await ctx.send("Queue is full!")
            
            await ctx.reply("Fetching video data....")
            await ctx.trigger_typing()
            ret = await self.compute(url)
            if not ret:
                return await ctx.send("Not found")
            title, src = ret
            await ctx.send(f"Added **{title}** to queue")
            if len(self.bot.queue) or voice_client.is_playing():
                return self.bot.queue.append((title, src, ctx.author))
            return voice_client.play(src, after=after)
        
        await ctx.reply("Fetching video data....")
        await ctx.trigger_typing()
        ret = await self.compute(url)
        if not ret:
            return await ctx.send("Not found")
        title, src = ret
        await ctx.send(f"Added **{title}** to queue")
        voice_client.play(src, after=after)
    
    @commands.command()
    @commands.guild_only()
    async def skip(self, ctx: commands.Context):
        voice_client: Optional[discord.VoiceClient] = ctx.voice_client
        if not voice_client:
            return await ctx.send("Not in any voice channel")
        
        elif not voice_client.is_playing():
            return await ctx.send("Not playing anything")
        voice_client.stop()
        await ctx.send("Skipped")

def setup(bot):
    bot.add_cog(Music(bot))
    print("Loaded music")
