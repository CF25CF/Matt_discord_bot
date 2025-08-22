import datetime
import zoneinfo

import discord
from discord.ext import commands, tasks




class Task(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="Christian"),
            status=discord.Status.online
        )

        self.hour_check.start()

    @tasks.loop(seconds=60)
    async def hour_check(self):
        germany = zoneinfo.ZoneInfo("Europe/Berlin")
        current_time = datetime.datetime.now(tz=germany)
        formatted_time = current_time.strftime("%H:%M")

        channel = await self.bot.fetch_channel(1364961455065272333)

        #if current_time.minute == 0:
        #    await channel.send(f"🕒 Es wurde jetzt **{formatted_time}** Uhr")



def setup(bot):
    bot.add_cog(Task(bot))