from discord.ext import commands
from discord.commands import slash_command
import asyncio



class Base(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command()
    async def wait(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel


        await ctx.respond("Gib eine Zahl an")

        while True:
            try:
                answer = await self.bot.wait_for("message", timeout=10.0, check=check)
                if answer.content.isdigit():
                    await ctx.send(f"du hast die Zahl **{answer.content}** geschrieben")
                    break
                else:
                    await ctx.send("das war keine gültige Zahl!")
            except asyncio.TimeoutError:
                await ctx.send("🙄 Du warst zu langsam")
                break









def setup(bot):
    bot.add_cog(Base(bot))