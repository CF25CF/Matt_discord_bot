import discord
from discord.ext import commands
from discord.commands import slash_command, Option

food = ["Brot 🍞"]

def get_food(ctx: discord.AutocompleteContext):
    guild = ctx.interaction.guild
    user = guild.get_member(ctx.interaction.user.id)
    role_ids = [role.id for role in user.roles]

    if 1367460392082604112 in role_ids:
        return food + ["Linseneintopf 🍲", "Steak 🥩"]

    elif 1367460824016486410 in role_ids:
        return food + ["Linseneintopf 🍲"]

    elif 1367195014475677716 in role_ids:
        return food



class AutoComplete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def essen(self, ctx, auswahl: Option(str, autocomplete=get_food)):

        await ctx.respond(f"{ctx.author.mention} hat ✨ **{auswahl}** ✨ gegessen 😋")



def setup(bot):
    bot.add_cog(AutoComplete(bot))