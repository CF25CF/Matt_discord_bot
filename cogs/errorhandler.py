from discord.ext import commands



class Errorhandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            seconds = round(error.retry_after)
            await ctx.respond(f"⏳Dieser Befehl kann erst in **{seconds} Sekunden** wieder benutzt werden!", ephemeral=True)
            return

        else:
            await ctx.respond(f"🛑 Es ist ein Fehler aufgetreten: ```{error}```", ephemeral=True)

def setup(bot):
    bot.add_cog(Errorhandler(bot))
