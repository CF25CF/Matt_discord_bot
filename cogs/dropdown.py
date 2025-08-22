import discord
from discord.ext import commands
from discord.commands import slash_command

class Dropdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def lieblingsspiel(self, ctx):
        await ctx.respond("Wähle dein Lieblingsspiel aus", view=DropdownView())



class DropdownView(discord.ui.View):
    options = [
        discord.SelectOption(label="Minecraft", description="Block-Game", emoji="⛏️", value="minecraft"),
        discord.SelectOption(label="Overwatch", description="Team-Shooter", emoji="🔫", value="overwatch"),
        discord.SelectOption(label="Fortnite", description="Battle Royale", emoji="🚌", value="fortnite")
    ]

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder="Was ist dein Lieblingsspiel?",
        options=options

    )
    async def select_callback(self, select, interaction):
        string = ""
        for auswahl in select.values:
            string += f"- {auswahl}\n"

        await interaction.response.send_message(f"Du hast folgendes Spiel ausgewählt:\n{string}")



        lieblingsspiel = select.values[0]
        user = interaction.user
        guild = interaction.guild

        rollen_mapping = {
            "minecraft": 1367458080329175070,
            "overwatch": 1367458208033013790,
            "fortnite": 1367458309426385006
        }

        neue_rollen_id = rollen_mapping.get(lieblingsspiel)
        neue_rolle = guild.get_role(neue_rollen_id)

        for rolle_value in rollen_mapping.values():
            rolle = guild.get_role(rolle_value)
            if rolle in user.roles and rolle != neue_rolle:
                await user.remove_roles(rolle)


        await user.add_roles(neue_rolle)








def setup(bot):
    bot.add_cog(Dropdown(bot))

