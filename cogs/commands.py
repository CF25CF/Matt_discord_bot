import discord, datetime, zoneinfo
from discord import Option
from discord.ext import commands
from discord.commands import slash_command




class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Grüße ein User")
    async def greet(self, ctx, user: Option(discord.Member, "Wen möchtest du grüßen?")):
        await ctx.respond(f"Hallo {user.mention}")

    @slash_command(description="veranlasse, dass der Bot eine Nachricht schreibt")
    async def say(self, ctx,
                  text: Option(str, "was soll er sagen?"),
                  channel: Option(discord.TextChannel, "in welchen channel soll er es schreiben?")
                  ):
        await channel.send(text)
        await ctx.respond("Die Nachricht wurde versendet", ephemeral=True)

    @slash_command(description="Zeige Infos über einen User", name="userinfo")
    async def info(self, ctx,
                   alter: Option(int, "Das Alter", min_value=1, max_value=99),
                   user: Option(discord.Member, "Gib einen User an", default=None)
                   ):
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=f"Infos über {user.name}",
            description=f"Hier siehst du alle Details über {user.mention}",
            color=discord.Color.blue()
        )

        account_created = discord.utils.format_dt(user.created_at, "R")
        server_joined = discord.utils.format_dt(user.joined_at, "D")

        embed.add_field(name="Account erstellt", value=account_created, inline=False)
        embed.add_field(name="Alter", value=alter, inline=False)
        embed.add_field(name="Server beitritt", value=server_joined, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Das ist ein footer")

        await ctx.respond(embed=embed)


    @slash_command()
    @discord.default_permissions(administrator=True, kick_members=True)
    async def activity(self, ctx,
                       typ: Option(str,
                                   choices=["zocken", "schauen", "hören"],
                                   name="aktivität",
                                   description="was tut er?"),
                       name: Option(str,
                                    name="name",
                                    description="und was genau?")
                       ):

        if typ == "zocken":
            act = discord.Game(name=name)
        elif typ == "schauen":
            act = discord.Activity(type=discord.ActivityType.watching, name=name)
        elif typ == "hören":
            act = discord.Activity(type=discord.ActivityType.listening, name=name)
        else:
            act = None

        await self.bot.change_presence(activity=act, status=discord.Status.online)
        await ctx.respond("Der Status von " + f"<@{ctx.bot.user.id}> " + "wurde geändert! ✅")



    @slash_command(name="aktuelle_uhrzeit", description="Gebe dir die aktuelle Uhrzeit aus")
    @commands.cooldown(1, 60, commands.BucketType.channel)
    async def current_time(self, ctx):
        germany = zoneinfo.ZoneInfo("Europe/Berlin")
        time_in_germany = datetime.datetime.now(tz=germany)
        formatted_time = time_in_germany.strftime("%H:%M:%S")

        await ctx.respond(f"🕒 Aktuelle Uhrzeit: {formatted_time}")





def setup(bot):
    bot.add_cog(Commands(bot))