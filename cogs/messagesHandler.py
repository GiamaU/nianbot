import discord
import random
import asyncio
from discord.ext import commands
from utils import dataIO

confirmation_message = 'schwellagur'

# todo!important better way to increase separately commands counter and messages counter
# dynamic confirmation. message?


class messagesHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")
        self.auto_answers = dataIO.get_Info("auto_answers.json")
        self.answers_counter = 0

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if not self.bot.is_ready() or ctx.author.bot:
            return

        self.bot.ww.dbh.increase_used_commands_by_id(ctx.author.id)
        self.bot.ww.dbh.decrease_user_messages_by_id(ctx.author.id)

        print(f"{ctx.channel.name if not isinstance(ctx.channel, discord.channel.DMChannel) else 'Private message'} -- {ctx.author} -- {ctx.message.clean_content}")
        if ctx.command.cog_name in ('Administration', 'Moderation'):
            if ctx.command.name in ('warn', 'ban'):
                await self.bot.warn_channel.send(f'{ctx.channel.name} -- {ctx.author} -- {ctx.message.clean_content}')
            else:
                await self.bot.log_channel.send(f'{ctx.channel.name} -- {ctx.author} -- {ctx.message.clean_content}')

    @commands.Cog.listener()
    async def on_message(self, msg):
        if not self.bot.is_ready() or msg.author.bot or isinstance(msg.channel, discord.channel.DMChannel):
            return

        if msg.channel.id == 713743319448027317:
            m = None
            if not any(r.id == 713745424690970686 for r in msg.author.roles):
                m = await msg.channel.send(f'{msg.author.mention} you have been already confirmed')
            else:
                if msg.content.lower() == confirmation_message:
                    m = await msg.channel.send(f'{msg.author.mention} You\'ll be confirmed in a few seconds, remember to **respect the rules** and have fun!')
                    await asyncio.sleep(2)
                    await msg.author.remove_roles(msg.guild.get_role(713745424690970686))
                else:
                    m = await msg.channel.send(f'{msg.author.mention} invalid, please read the rules')
            await asyncio.sleep(2)
            try:
                await msg.delete()
                await m.delete()
            except:
                pass
            return
        elif msg.channel.id == 735536183043424287:
            self.answers_counter += 1

            if self.answers_counter == 30:
                await self.bot.iw.send_question()
                self.answers_counter = 0

        if msg.channel.id != 711218302214733834:
            self.bot.ww.dbh.increase_user_messages_by_id(msg.author.id)

        for question in self.auto_answers[0].question:
            if msg.content.lower() in question.text:
                await msg.channel.send(random.choice(question.answer if msg.author.id != 310852581385699340 else question.owanswer).format(author=msg.author.nick if msg.author.nick is not None else msg.author.name, emoji='<:FrostLeafLove:685151438040727710>'))


def setup(bot):
    bot.add_cog(messagesHandler(bot))