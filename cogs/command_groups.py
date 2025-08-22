import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup



class CommandGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    drink = SlashCommandGroup("trink", "den Durst stillen")

    @drink.command()
    async def wasser(self, ctx):
        await ctx.respond(f"{ctx.author.mention} hat Wasser getrunken 💧")

    @drink.command()
    async def cola(self, ctx):
        await ctx.respond(f"{ctx.author.mention} hat Cola getrunken 🥤")

    @drink.command()
    async def bier(self, ctx):
        await ctx.respond(f"{ctx.author.mention} hat Bier getrunken 🍺")







def setup(bot):
    bot.add_cog(CommandGroup(bot))
