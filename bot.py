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

token = os.getenv("TOKEN")
if not token:
    import dotenv
    dotenv.load_dotenv()
    token = os.environ["TOKEN"]

if __name__ == "__main__":
    bot.run(token)
