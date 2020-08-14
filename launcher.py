import asyncio
from utils import dataIO
from utils.help_format import HelpFormat
from core.nianbot import NianBot
import os


async def main():
    config = dataIO.get_Info('config.json')
    bot = NianBot(
        command_prefix=config.prefix,
        prefix=config.prefix,
        command_attrs=dict(hidden=True),
        case_insensitive=True,
        help_command=HelpFormat()
    )

    bot.discover_exts('cogs')
    # bot.load_extension('jishaku')
    await bot.start(os.getenv('token'))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
