import discord
from utils import permissions, dataIO, utils
import time
import psutil
import os
from datetime import datetime
from discord.ext import commands
import random

# todo improve join faction command (ensure future?)
# todo better info system
# todo general commands: {add here}


class RoleID(commands.Converter):
    async def convert(self, ctx, argument: str):
        faction_roles = dataIO.get_Info('config.json').faction_roles

        if argument.lower() in ('random', 'rand'):
            return random.choice(faction_roles)

        if argument.isdigit():
            faction_role = faction_roles[int(argument)-1] if int(argument) <= len(faction_roles) else 9999999999999999999999999999
            return faction_role

        args = argument.split(' ')
        ret = ''.join((args[0][0].upper() + args[0][1:].lower() + ' ' + args[1][0].upper() + args[1][1:].lower()) if len(args) > 1 else args[0][0].upper() + args[0][1:].lower())
        try:
            r = await commands.RoleConverter().convert(ctx, ret)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid role.") from None
        else:
            return r.id


class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.command(
        name='factions',
        help='shows current factions',
        description='The faction command!',
        aliases=['show factions', 'available factions']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _factions(self, ctx):
        if await permissions.check_guild_only(ctx):
            return

        faction_roles = [ctx.guild.get_role(role) for role in self.config.faction_roles]

        loop = [(
            f"***{str(role.name).upper()}***" if role.id != self.config.faction_roles[-1] else f"*{str(role.name)}* [if you don\'t want to join a faction]")
            for role in faction_roles]
        await utils.prettyResults(
            ctx, "name", f"There are **{len(loop)}** factions", loop
        )

    @commands.command(
        name='join',
        help='Join a faction!',
        description='The join command!',
        aliases=['faction', 'autorole']
    )
    @commands.cooldown(1, 4)
    @permissions.is_in_channel(684786580937900043)
    async def _join(self, ctx, *, faction: RoleID):
        if await permissions.check_guild_only(ctx):
            return

        if faction in self.config.faction_roles:
            role_to_add = ctx.guild.get_role(faction)
            faction_roles = [ctx.guild.get_role(role) for role in self.config.faction_roles]
            faction_roles.remove(role_to_add)
            if faction in tuple(r.id for r in ctx.author.roles):
                return await ctx.send(f'You are already in **__{role_to_add}__**')
            await ctx.send(f'{ctx.author.mention}You will join: **__{role_to_add}__** in a few seconds!')
            await ctx.author.add_roles(role_to_add)
            await ctx.author.remove_roles(*faction_roles)
        else:
            await ctx.send('Invalid faction')

    @commands.command(
        name='ping',
        help='Pong!',
        description='The ping command!',
        aliases=[]
    )
    @permissions.is_in_channel(684786580937900043)
    async def _ping(self, ctx):
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(
        name='info',
        help='Displays informations about the member',
        description='The info command!',
        aliases=['about', 'stats']
    )
    @permissions.is_in_channel(684786580937900043)
    async def _info(self, ctx, *, member: discord.Member = None):
        if await permissions.check_guild_only(ctx):
            return

        if member is None:
            embed = discord.Embed(colour=discord.Colour.green())

            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="Owner:", value=ctx.guild.owner.name)
            embed.add_field(name="Created at", value=ctx.guild.created_at.date())
            embed.add_field(name="Total messages sent:", value=self.bot.ww.dbh.get_all_sent_messages()[0]["totalAmount"])
            embed.add_field(name="Total Members:", value=str(len(ctx.guild.members)), inline=True)
            embed.add_field(name="Total Admins:", value=str(len([member for member in ctx.guild.members if any(role.id in self.config.admin_roles for role in member.roles)])), inline=True)
            embed.add_field(name="Total Mods:", value=str(len([member for member in ctx.guild.members if any(role.id in self.config.moderator_roles for role in member.roles)])), inline=True)

        elif member.id == self.bot.user.id:
            ramUsage = self.process.memory_full_info().rss / 1024 ** 2

            embed = discord.Embed(colour=discord.Colour.green())

            embed.set_thumbnail(url=ctx.bot.user.avatar_url)
            embed.add_field(name="Last boot", value=utils.timeago(datetime.now() - self.bot.uptime), inline=True)
            embed.add_field(name="Commands loaded", value=str(len([x.name for x in self.bot.commands])), inline=True)
            embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB", inline=True)
            embed.add_field(name='Version', value=self.config.version, inline=True)
            embed.add_field(name="Developer", value='GianMa-U', inline=True)
            embed.add_field(name="I love", value='Kyo', inline=True)
        else:
            embed = discord.Embed(colour=discord.Colour.red())
            user = self.bot.ww.dbh.get_document_by_id("users", member.id)
            #todo mettere owner
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="id", value=member.id, inline=True)
            embed.add_field(name="username", value=member.name, inline=True)
            embed.add_field(name="joined at", value=user["joined_at"].date(), inline=True)
            embed.add_field(name="messages sent", value=user["messages_sent"] if member.id != 310852581385699340 else '∞', inline=True)
            embed.add_field(name="commands used", value=(user["commands_used"] + 1 if ctx.author.id == member.id else user["commands_used"]) if member.id != 310852581385699340 else '∞', inline=True)
            embed.add_field(name="warned", value=f'{user["strikes"]} times', inline=True)

        await ctx.send(content=f"ℹ About **{(member.nick if member.nick is not None else member.name) if member is not None else 'This Guild'}**", embed=embed)


def setup(client):
    client.add_cog(General(client))
