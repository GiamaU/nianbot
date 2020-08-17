import discord
from discord.ext import commands
from utils import dataIO


class eventsHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = dataIO.get_Info("config.json")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        no_faction = member.guild.get_role(self.config.faction_roles[-1])

        try:
            if self.bot.ww.dbh.get_document_by_id("users", member.id) is None:
                self.bot.ww.dbh.add_user(member)
            await member.add_roles(no_faction, member.guild.get_role(713745424690970686))

            embed = discord.Embed(title=f"Welcome to KyoStinV Server {member.name} ",
                                  description="This is a To-Do-List to unlock all chat channel \n"
                                              "- first go to the #rules read them \n"
                                              "- secondly find the confirmation word\n"
                                              "- thirdly go to #confirmation \n"
                                              "- at last paste the word in chat and send it\n"
                                              "with that you unlock all channel \n"
                                              "have a great time here and have fun", color=discord.Color.red())
            if not member.dm_channel:
                await member.create_dm()
            await member.dm_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print(f"Failed to send welcome message to {member.name} ")
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.bot.log_channel.send(f'```❗{user} HAS BEEN BANNED```')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        muted_role = after.guild.get_role(691265959302004797)

        if muted_role in after.roles and muted_role not in before.roles:
            await self.bot.log_channel.send(f'```❗{after} HAS BEEN MUTED```')
        elif muted_role in before.roles and muted_role not in after.roles:
            await self.bot.log_channel.send(f'```❗{after} HAS BEEN UNMUTED```')

    @commands.Cog.listener()
    async def on_user_update(self, before, after):

        if before.name != after.name:
            self.bot.ww.dbh.update_user_name_by_id(after.id, after.name)


def setup(bot):
    bot.add_cog(eventsHandler(bot))
