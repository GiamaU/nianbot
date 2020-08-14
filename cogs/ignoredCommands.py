from utils import dataIO
from discord.ext import commands


class IgnoredCommands(commands.Cog): #qualcosa per farlo ????

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")

    @commands.command(
        name='qotd',
        help='',
        description='',
        aliases=[],
        hidden=True
    )
    async def _qotd_ignore(self, ctx):
        pass


def setup(client):
    client.add_cog(IgnoredCommands(client))
