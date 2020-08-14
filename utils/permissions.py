import discord
from utils import utils, dataIO
from discord.ext import commands

data = dataIO.get_Info('config.json')

# possible to shorten this?


def is_owner():
    def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        return ctx.author.id in data.owners

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        if any(role.id in data.admin_roles for role in ctx.author.roles) or await check_guild_permissions(ctx, {
            'manage_guild': True}):
            return True

        # await ctx.send(f'you don\'t have permission to {ctx.command}')
        return False

    return commands.check(predicate)


def is_mod():
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        if any(role.id in data.moderator_roles for role in ctx.author.roles) or await check_guild_permissions(ctx, {
            'ban_members': True}):
            return True
        # await ctx.send(f'you don\'t have permission to {ctx.command}')
        return False

    return commands.check(predicate)


def is_lil_mod():
    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        if any(role.id in data.lilmoderator_roles for role in ctx.author.roles) or await check_guild_permissions(ctx, {'manage_messages': True}):
            return True
        # await ctx.send(f'you don\'t have permission to {ctx.command}')
        return False

    return commands.check(predicate)


def is_mod_or_cooldown(rate, per, bucket_type=commands.BucketType.default):
    cd = commands.CooldownMapping.from_cooldown(rate, per, bucket_type)

    async def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            return False

        if any(role.id in data.moderator_roles for role in ctx.author.roles) or await check_guild_permissions(ctx, {
            'ban_members': True}):
            return True

        bucket = cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True

    return commands.check(predicate)


async def check_permissions(ctx, perms, *, check=all):
    if ctx.author.id in data.owners or ctx.author.id in data.admins:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


async def check_guild_permissions(ctx, perms, *, check=all):
    if ctx.author.id in data.owners or ctx.author.id in data.admins:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)

    return commands.check(pred)


async def check_priv(ctx, member):
    try:
        if member == ctx.author:
            return await ctx.send(f"You can't {ctx.command.name} yourself")
        if member.id == ctx.bot.user.id:
            return await ctx.send(f"Are you trying to {ctx.command.name} me?! D:")

        if ctx.author.id == ctx.guild.owner.id:
            return False

        if member.id in data.owners:
            if ctx.author.id not in data.owners:
                return await ctx.send(f"I can't {ctx.command.name} my creator :3")
            else:
                pass
        if member.id == ctx.guild.owner.id:
            return await ctx.send(f"You can't {ctx.command.name} Lord {ctx.guild.owner.nick if not None else ctx.guild.owner.name}, the server's owner")
        if ctx.author.top_role == member.top_role and ctx.author.id not in data.admins:
            return await ctx.send(f"You can't {ctx.command.name} someone who has the same permissions as you...")
        if ctx.author.top_role < member.top_role and ctx.author.id not in data.admins:
            return await ctx.send(f"Nop, you can't {ctx.command.name} your who has higher permissions than you...")
    except Exception:
        pass


async def check_guild_only(ctx):
    try:
        if ctx.guild is None:
            return await ctx.send(f"You must be in the guild to use this command!")
    except Exception:
        pass


def is_in_channel(channel_id):
    async def predicate(ctx):

        if isinstance(ctx.channel, discord.channel.DMChannel):
            return True

        if any(role.id in data.moderator_roles for role in ctx.author.roles) or await check_guild_permissions(ctx, {'manage_messages': True}):
            return True

        return ctx.channel.id == channel_id

    return commands.check(predicate)


def is_nsfw(ctx):
    return isinstance(ctx.channel, discord.DMChannel) or ctx.channel.is_nsfw()
