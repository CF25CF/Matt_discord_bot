from discord.ext import commands
from discord.commands import message_command, user_command

class Context(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @user_command()
    async def stups(self, ctx, member):
        await ctx.respond(f"{ctx.author.mention} hat {member.mention} **angestupst!**")


def setup(bot):
    bot.add_cog(Context(bot))