from nextcord.ext import commands
from .generate import Game


class ProjectBot(commands.Bot):
    def __init__(self):
        super().__init__(".")
        self.add_cog(Game(self))

    async def on_ready(self) -> None:
        print(f"Ready as {self.user} | {self.user.id}")
