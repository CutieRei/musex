import asyncio
import aiohttp
from discord.ext import commands
import os

extensions = [
    "music"
]
bot = commands.Bot(command_prefix="mx.")
bot.load_extension("jishaku")

for ext in extensions:
    bot.load_extension(f"ext.{ext}")

@bot.listen()
async def on_ready():
    print("Logged in as", str(bot.user))

async def _job():
    async with aiohttp.ClientSession() as sess:
        await sess.post("http://localhost:8000/restart", data={"token": bot.http.token})

@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting....")
    asyncio.create_task(_job())

token = os.getenv("TOKEN")
if not token:
    import dotenv
    dotenv.load_dotenv()
    token = os.environ["TOKEN"]

if __name__ == "__main__":
    bot.run(token)
