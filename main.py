from typing import Any, Dict
import fastapi
import importlib
import bot
import asyncio

config: Dict[str, Any] = {
    "app": None,
    "bot": None
}

async def start():
    importlib.reload(bot)
    bot.bot.config = config
    asyncio.create_task(bot.bot.start(bot.token))
    await bot.bot.wait_until_ready()
    config["bot"] = bot.bot

async def stop():
    _bot: bot.commands.Bot = config.get("bot")
    if _bot:
        await _bot.close()
        config["bot"] = None

app = fastapi.FastAPI(on_startup=[start], on_shutdown=[stop])
config["app"] = app

@app.get("/ping")
def ping():
    return {
        "msg": "PONG!"
    }

@app.post("/restart")
async def restart(token: str = fastapi.Form(...)):
    _bot: bot.commands.Bot = config.get("bot")
    if not _bot:
        return {
            "status": 503,
            "msg": "Service Unavailable"
        }
    if token != _bot.http.token:
        return {
            "status": 403,
            "msg": "forbidden"
        }
    await stop()
    await start()
    return {
        "status": 200,
        "msg": "Ok"
    }