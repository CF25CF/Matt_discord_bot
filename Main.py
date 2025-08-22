import discord, os
from dotenv import load_dotenv
from cogs.buttons import TutorialView
from datetime import datetime

load_dotenv()


intents = discord.Intents.default()
intents.members = True  #member events
intents.message_content = True #message readable




Matt = discord.Bot(intents=intents,
                   status = discord.Status.online,
                   debug_guilds=[int(os.getenv("DEBUG_GUILD"))])



@Matt.event
async  def on_ready():
    print(f"[{datetime.now()}] Matt ist online")

    Matt.add_view(TutorialView())




if __name__ == "__main__":
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            Matt.load_extension(f"cogs.{filename[:-3]}")

    load_dotenv()
    Matt.run(os.getenv("TOKEN"))