import discord
from discord.ext import commands



class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener() #delete message
    async def on_message_delete(self, msg):
        await msg.channel.send(f"*{msg.author} hat eine Nachricht gelöscht*")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        user_role = member.guild.get_role(1367460824016486410)
        await member.add_roles(user_role)
        embed = discord.Embed(
            title = "Willkommen!",
            description = f"Hey {member.mention} 👋",
            color=discord.Color.green()
        )

        channel = await self.bot.fetch_channel(1364961455065272333)
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))