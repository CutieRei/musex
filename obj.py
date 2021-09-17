from typing import Any, Dict, Tuple, Union
from discord import User, Member
from discord.ext import commands
from collections import deque
from discord.player import FFmpegPCMAudio
from typing import Deque

class Musex(commands.Bot):

    queue: Deque[Tuple[str, FFmpegPCMAudio, Union[User, Member]]]
    config: Dict[str, Any]

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.queue = deque()
