import argparse
import io
import os
import sys
import time
import aiohttp
import discord
from discord.ext import commands
from utils import permissions, utils, dataIO


#  add guild_only ?

class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            return m.id


class ChannelID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            c = await commands.TextChannelConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid text channel") from None
        else:
            return c.id


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


class Administration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")

    @commands.command(
        name='load',
        help='Loads an extension.',
        description='The load command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _load(self, ctx, name: str):
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            print(e)
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command(
        name='unload',
        help='Unloads an extension.',
        description='The unload command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _unload(self, ctx, name: str):
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            print(e)
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.command(
        name='reload',
        help='Reloads an extension.',
        description='The reload command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _reload(self, ctx, name: str):
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            print(e)
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command(
        name='reloadall',
        help='Reloads all extensions.',
        description='The reload all command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _reloadall(self, ctx):
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, e]
                    )

        if error_collection:
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            print(f'reloaded all extensions, except: {output}')

        await ctx.send("Successfully reloaded all extensions")

    @commands.command(
        name='reboot',
        help='Reboot the bot.',
        description='The reboot all command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def reboot(self, ctx):
        await ctx.send('Rebooting now...')
        time.sleep(1)
        sys.exit(0)

    @commands.command(
        name='dm',
        help='DM the user',
        description='The direct message command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _dm(self, ctx, member: MemberID, *, message: str):
        user = self.bot.get_user(member)
        if not user:
            return await ctx.send(f"Could not find any UserID matching **{member}**")

        try:
            await user.send(message)
            await ctx.send(f"✉️ Sent a DM to **{member}**")
        except discord.Forbidden:
            await ctx.send("This user might be having DMs blocked or it's a bot account...")

    @commands.command(
        name='say',
        help='Says a message in a text channel',
        description='The say command!',
        aliases=['message', 'mess'],
    )
    @permissions.is_admin()
    async def _say(self, ctx, channel: ChannelID, *, msg: str):
        channel = self.bot.get_channel(channel)
        if not channel:
            return await ctx.send(f"Could not find any ChannelID matching **{channel}**")
        await channel.send(msg)

    @commands.command(
        name='send',
        help='sends an attachment in a text channel',
        description='The send command!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _send(self, ctx, channel: ChannelID):
        channel = self.bot.get_channel(channel)
        if not channel:
            return await ctx.send(f"Could not find any ChannelID matching **{channel}**")

        if len(ctx.message.attachments) == 0:
            return await ctx.send('You have to send an attachment!')

        try:
            for att in ctx.message.attachments:
                async with aiohttp.ClientSession() as session:
                    async with session.get(att.url) as resp:
                        if resp.status != 200:
                            return await ctx.send('Could not download file...')
                        data = io.BytesIO(await resp.read())
                        await channel.send(file=discord.File(data, 'img.png'))
        except:
            pass

    @commands.group(
        name='change',
        help='Changes a bot status',
        description='The change commands!',
        aliases=[],
    )
    @permissions.is_admin()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.channel.send(f'you haven\'t specified the argument! type {ctx.prefix}help {ctx.command.name}')

    @change.command(
        name='playing',
        help='<activity>',
        description='Changes the playing status.',
        aliases=[],
    )
    @permissions.is_admin()
    async def _change_playing(self, ctx, *, playing: str):

        if self.config.playing_type == "listening":
            playing_type = 2
        elif self.config.playing_type == "watching":
            playing_type = 3
        else:
            playing_type = 0

        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=playing_type, name=str(playing))  # todo remove cast
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(
        name='status',
        help='<status>',
        description='Changes the bot status',
        aliases=[],
    )
    @permissions.is_admin()
    async def _change_status(self, ctx, status: str):

        if status == "idle":
            status_type = discord.Status.idle
        elif status == "dnd":
            status_type = discord.Status.dnd
        elif status == "offline":
            status_type = discord.Status.offline
        elif status == "invisible":
            status_type = discord.Status.invisible
        else:
            status_type = discord.Status.online

        try:
            await self.bot.change_presence(
                status=status_type
            )
            dataIO.change_value("config.json", "status_type", status)
            await ctx.send(f"Successfully changed status to **{status}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(
        name='nickname',
        help='<new nickname>',
        description='Changes the nickname',
        aliases=[],
    )
    @permissions.is_admin()
    async def _change_nickname(self, ctx, *, name: str = None):
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @commands.group(
        name='lastid',
        help='shows/edit lastid of videos and tweets',
        description='The lastid commands!',
        aliases=[],
    )
    @permissions.is_admin()
    async def _lastid(self, ctx):
        if ctx.invoked_subcommand is None:
            await self._show_lastid(ctx)

    @_lastid.command(
        name='show',
        help='shows last ids',
        description='',
        aliases=[],
    )
    @permissions.is_admin()
    async def _show_lastid(self, ctx):
        loop = [f"last yt id: {self.bot.ww.last_youtube_id}", f"last tw id: {self.bot.ww.last_twitter_id}"]
        await utils.prettyResults(
            ctx, "name", f"Found **{len(loop)}** ids", loop
        )

    @_lastid.command(
        name='set',
        help='set youtube/twitter last id',
        description='',
        aliases=[],
    )
    @permissions.is_admin()
    async def _set_lastid(self, ctx, *, args: str):  # todo migliorare
        if len(args) == 0 or not len(args.split(' ')) == 2:
            return
        if args.split(' ')[0] == 'youtube':
            self.bot.ww.last_youtube_id = args.split(' ')[1]
        elif args.split(' ')[0] == 'twitter':
            self.bot.ww.last_twitter_id = args.split(' ')[1]

    @commands.command(
        name='update',
        help='Updates videos and tweets',
        description='The update command',
        aliases=['up'],
    )
    @permissions.is_admin()
    async def _update(self, ctx):
        await self.bot.ww.restart()

    @commands.command(
        name='updateroles',
        help='Updates guild roles',
        description='The updaterole command',
        aliases=[],
    )
    @permissions.is_admin()
    async def _updateroles(self, ctx):
        members = ctx.guild.members
        faction_roles = [ctx.guild.get_role(role) for role in self.config.faction_roles]
        for member in members:
            if len(member.roles) == 1 or all(role not in faction_roles for role in member.roles):
                if not member.bot:
                    try:
                        await member.add_roles(faction_roles[-1])
                    except:
                        await ctx.send('Unable to update roles')
                        return
        await ctx.send('successfully updated roles')


def setup(client):
    client.add_cog(Administration(client))