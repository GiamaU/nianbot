import re
from discord.ext import commands
from utils import permissions, utils, dataIO

youtube_search_url = 'https://www.youtube.com/watch?v='
youtube_playlist_url = 'https://www.youtube.com/playlist?list='

# todo better search system (ex. cm for challenge mode, etc...)


class VideoLevel(commands.Converter):
    async def convert(self, ctx, argument: str):
        ret = argument.lower()
        re.escape(ret)

        if not re.match(r'[A-z-0-9]+', ret):
            raise commands.BadArgument(f'{argument} is not a valid level.') from None
        return ret


class Search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")

    @commands.command(
        name='video',
        help='Search for a Kyo video on his channel, the title must be close',
        description='You will get only one result',
        aliases=['vid']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _video(self, ctx, *, title: str):
        stored_videos = self.bot.ww.dbh.get_document_by_name('videos')
        words = title.split(' ')
        for video in stored_videos:
            if all(word.lower() in video["title"].lower() for word in words):
                return await ctx.send(youtube_search_url + video["_id"])

        await ctx.send('no results found')

    @commands.command(
        name='stage',
        help='Search for guides about that stage',
        description='Stage examples: "5-2", "H5-2" ...',
        aliases=['level', 'lv']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _level(self, ctx, *, level: VideoLevel):
        stored_videos = self.bot.ww.dbh.get_document_by_name('videos')
        levels = level.split(' ')
        loop = [f"{video['title']}\n{youtube_search_url}{video['_id']}" for video in stored_videos if
                all(text in video["title"].lower() for text in levels)]
        await utils.prettyResults(
            ctx, "name", f"Found **{len(loop)}** videos on your search for **{str(level)}**", loop
        )

    @commands.command(
        name='review',
        help='<title>',  # todo help <-->
        description='...',  # todo description
        aliases=[],
        hidden=True
    )
    @permissions.is_mod_or_cooldown(1, 2)
    @permissions.is_in_channel(684786580937900043)
    async def _review(self, ctx):
        pass

    @commands.command(
        name='playlist',
        help='<name>',  # todo help <-->
        description='...',  # todo description
        aliases=[],
        hidden=True
    )
    @permissions.is_mod_or_cooldown(1, 2)
    @permissions.is_in_channel(684786580937900043)
    async def _playlist(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Search(bot))
