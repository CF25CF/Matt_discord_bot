import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ext.pages import Paginator, Page



class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command()
    async def userliste(self, ctx):
        members = ctx.guild.members
        pages = []
        description = ""

        for index, member in enumerate(members):
            description += f"`{index +1}.` {member}\n"

            if (index +1) % 10 == 0:
                embed = discord.Embed(title="Userliste", description=description, color=discord.Color.blue())
                page = Page(embeds=[embed])
                pages.append(page)
                description = ""

        if description:
            embed = discord.Embed(title="Userliste", description=description, color=discord.Color.blue())
            embed.set_thumbnail(url=ctx.guild.icon.url)
            pages.append(Page(embeds=[embed]))

        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction, ephemeral=True)


def setup(bot):
    bot.add_cog(Embed(bot))