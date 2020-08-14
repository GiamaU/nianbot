import time
import discord
import timeago as timesince
from io import BytesIO

# todo split prettyResults() function  


def timetext(name):
    return f"{name}_{int(time.time())}.txt"


def timeago(target):
    return timesince.format(target)


def date(target, clock=True):
    if clock is False:
        return target.strftime("%d %B %Y")
    return target.strftime("%d %B %Y, %H:%M")


def responsible(target, reason):
    responsible = f"[ {target} ]"
    if reason is None:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case, time: str=None, mass=False):
    output = f"**{case}** the member for {time}" if time is not None else f"**{case}** the member"

    if mass is True:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def prettyResults(ctx, filename: str = "Results", resultmsg: str = "Here's the results:", loop=None):
    if not loop:
        return await ctx.send("No results")

    cogs_not_to_trim = ('Administration', 'Moderation', 'General')

    limit = 14
    loop = loop if ctx.command.cog_name in cogs_not_to_trim else loop[:limit]
    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) <= limit:
        return await ctx.send(f"{resultmsg}" + (f', here are the first **__{len(loop)}__** results' if len(loop) == limit and ctx.command.cog_name not in cogs_not_to_trim else ''), embed=discord.Embed(color=discord.Colour.red(), description=f'\n{pretty}'))
    else:
        data = BytesIO(pretty.encode('utf-8'))
        await ctx.send(
            content=resultmsg,
            file=discord.File(data, filename=timetext(filename.title()))
        )
