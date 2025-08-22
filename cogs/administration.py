import discord
from discord.ext import commands
from discord.commands import slash_command, Option


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="kicke einen User")
    @discord.default_permissions(administrator=True, kick_members=True)
    @discord.guild_only()
    async def kick(self, ctx, member: Option(discord.Member, "Wähle einen Member")):
        try:
            await member.kick()
        except (discord.Forbidden, discord.HTTPException):
            await ctx.respond(f"🛑 Ich habe keine Berechtigung, den User {member.mention} zu kicken!")
            return
        await ctx.respond(f"der User {member.mention}, wurde **gekickt**❗")




def setup(bot):
    bot.add_cog(Admin(bot))