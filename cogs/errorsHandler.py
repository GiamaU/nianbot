import discord
import psutil
import os
from discord.ext import commands
from discord.ext.commands import errors
from utils import utils, dataIO
from utils import permissions

# todo fix missing permissions alert
# improved errors handler?


class errorsHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")
        self.process = psutil.Process(os.getpid())

        self.__old_on_error = bot.on_error
        bot.on_error = self.on_error

    def cog_unload(self):
        self.bot.on_error = self.__old_on_error

    async def on_error(self, event_method, *args, **kwargs):
        print(f'Error in on_{event_method}')
        print(event_method.error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):

        if not isinstance(ctx.channel, discord.channel.DMChannel) and ctx.channel.id != 684786580937900043:
            if not any(role.id in self.config.moderator_roles for role in ctx.author.roles) and not await permissions.check_guild_permissions(ctx, {'ban_members': True}):
                return

        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await ctx.send(f'Invalid argument')

        elif isinstance(err, errors.MissingPermissions):
            pass
            """
            await ctx.send(
                f'you don\'t have permissions to {ctx.command}'
            )
            """

        elif isinstance(err, errors.CommandInvokeError):
            error = err.original

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    f"You attempted to make the command display more than 2,000 characters...\n"
                    f"Both error and command will be ignored."
                )

            # await ctx.send(
            #    f"There was an error processing the command, report it to our devs: \n" + "\r".join([f"{data}" for data in self.config.owners])
            # )
            print(error)

        elif isinstance(err, errors.CommandNotFound):
            await ctx.send(
                f'Command not found'
            )

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CheckFailure):
            pass


def setup(bot):
    bot.add_cog(errorsHandler(bot))
