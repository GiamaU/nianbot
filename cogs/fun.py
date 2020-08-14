import argparse
import json
import random
import shlex
import discord
import googletrans
from discord.ext import commands
from googletrans import LANGUAGES
from utils import permissions, dataIO, utils

lng = "\n".join([lang + "-" + LANGUAGES[lang] for lang in LANGUAGES])


# todo filter text on translate + improve
# todo better hotcalc cheat system (xd)
# todo fun commands: {add here}

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")
        self.trans = googletrans.Translator()

    @commands.command(
        name='coinflip',
        help='What will you get? *heads* or *tails*?',
        description='The coinflip command!',
        aliases=['flip', 'coin', 'cf']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _coinflip(self, ctx):
        coinsides = ['Heads', 'Tails']
        await ctx.send(f"**{ctx.author.mention}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command(
        name='randomwaifu',
        help='Returns a random waifu *emoji*',
        description='The randomwaifu command!',
        hidden=True,
        aliases=['rw'],
    )
    @permissions.is_in_channel(684786580937900043)
    async def _randomwaifu(self, ctx):
        await ctx.send("*Command removed*")
        """
        waifu_emotes = [ctx.bot.get_emoji(emoji.id) for emoji in self.bot.emojis if 'waifu' in emoji.name.lower()]
        try:
            await ctx.send(f"**{ctx.author.mention}** you got {random.choice(waifu_emotes)}")
        except:
            await ctx.send(f"Are there any waifu emojis?")
        """
    @commands.command(
        name='hotcalc',
        help='Returns a random percent for how hot a member is',
        description='The hotcalc command!',
        aliases=['howhot', 'hot']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _hotcalc(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author
        random.seed(user.id)
        r = random.randint(1, 100)
        hot = 100000000 if user.id == self.bot.user.id else r / 1.17

        if user.id == 464426467032301568:
            hot = -1

        if user.id == 310852581385699340:
            hot = 95.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.nick if user.nick is not None else user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(
        name='reverse',
        help='Everything you type after reverse will be reversed',
        description='!dnammoc esrever ehT',
        aliases=[]
    )
    @permissions.is_in_channel(684786580937900043)
    async def _reverse(self, ctx, *, text: str):
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command(
        name='translate',
        help=f'Translates a message to English using Google translate.\nIf it doesn\'t work please type the message **between double quotes**.\nYou can type -s <source> and/or -d <destination> **after** the text to choose a language.\nSupported languages:\n{lng}',
        description='The translate command!',
        aliases=[]
    )
    @permissions.is_in_channel(684786580937900043)
    async def _translate(self, ctx, *, message: str):
        parser = argparse.ArgumentParser()
        parser.add_argument('text', nargs='+', type=str)
        parser.add_argument('-s', '--source', default='auto', type=str)
        parser.add_argument('-d', '--destination',  default='en', type=str)

        try:
            args = parser.parse_args(shlex.split(message))
        except SystemExit:
            return await ctx.send('Please use valid arguments')

        try:
            ret = self.trans.translate(" ".join(args.text), src=args.source, dest=args.destination)
        except json.JSONDecodeError:
            return await ctx.send('Invalid Text')
        except ValueError:
            return await ctx.send('invalid source language')
        except Exception as e:
            return print(f'An error occurred: {e.__class__.__name__}: {e}')

        embed = discord.Embed(title='Translated', colour=0x4284F3)
        src = googletrans.LANGUAGES.get(ret.src)
        dest = googletrans.LANGUAGES.get(ret.dest)
        embed.add_field(name=f'From {src.title() if src is not None else args.source}', value=ret.origin, inline=False)
        embed.add_field(name=f'To {dest.title()  if src is not None else args.destination}', value=ret.text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        name='msgleaderboard',
        help='shows the top 10 members, based on massages and commands used',
        description='The msgleaderboard command!',
        aliases=['msgtop10', 'msgl']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _msgleaderboard(self, ctx):
        members = list(self.bot.ww.dbh.get_top_10_users())
        for member in members:
            if member['_id'] == 310852581385699340:
                members.remove(member)
        members.insert(0, {'_id': 310852581385699340, 'messages_sent': '∞', 'commands_used': '∞'})
        loop = [f"**{(ctx.guild.get_member(member['_id']).nick or ctx.guild.get_member(member['_id']).name) if ctx.guild.get_member(member['_id']) is not None else member['name']}** - **__{member['messages_sent']}__** total sent messages | **__{member['commands_used']}__** total used commands" for member in members[:10]]
        await utils.prettyResults(
            ctx, "name", f"**Top 10 members**", loop
        )


def setup(client):
    client.add_cog(Fun(client))
