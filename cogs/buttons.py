import discord.ui
from discord.ext import commands
from discord.commands import slash_command


class Button(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def richtig_klicken(self, ctx):
        await ctx.respond("Bitte richtig klicken!", view=TutorialView())

    @slash_command()
    async def geheim(self, ctx):
        button = discord.ui.Button(label="😳", url="https://www.youtube.com/watch?v=xvFZjo5PgG0")
        view = discord.ui.View()
        view.add_item(button)

        await ctx.respond("Bist du sicher?", view=view)




class TutorialView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="nicht klicken ", style=discord.ButtonStyle.primary, emoji="😳", custom_id="button1")
    async def button_callback1(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.response.edit_message(view=self)

        user = interaction.user
        await interaction.followup.send(f"{user.mention} hat falsch geklickt! 🙄👏")

    @discord.ui.button(label="hier klicken", style=discord.ButtonStyle.primary, emoji="😀", custom_id="button2")
    async def button_callback2(self,  button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        await interaction.response.edit_message(view=self)

        user = interaction.user
        await interaction.followup.send(f"{user.mention} hat richtig geklickt! 😄👌")


def setup(bot):
    bot.add_cog(Button(bot))
