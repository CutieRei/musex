from discord.ext import commands
import os

bot = commands.Bot(command_prefix="musex.")

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
