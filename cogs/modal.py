import discord
from discord import Interaction
from discord.ext import commands
from discord.commands import slash_command



class Modal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command()
    async def msg_an_admin(self, ctx, ):
        modal = TestModal(title="Erzeuge ein Embed")
        await ctx.send_modal(modal)



class TestModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Anliegen deiner Nachricht:",
                placeholder="Anliegen:"
            ),
            discord.ui.InputText(
                label="Beschreibe dein Anliegen genauer:",
                placeholder="Beschreibung:",
                style=discord.InputTextStyle.long
            ),


            *args,
            **kwargs
        )


    async  def callback(self, interaction: Interaction):
        embed = discord.Embed(
            title=self.children[0].value,
            description=f"{interaction.user.mention} schreibt:\n {self.children[1].value}",
            color=discord.Color.green()
        )

        channel_id = 1366892320007520267
        channel = interaction.client.get_channel(channel_id)
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Deine Nachricht wurde erfolgreich an den Admin geschickt", ephemeral = True)




def setup(bot):
    bot.add_cog(Modal(bot))

