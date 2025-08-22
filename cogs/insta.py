from discord.ext import commands, tasks
from instagrapi import Client
import json
from datetime import datetime
import os



class Insta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dateiname = "time.json"
        self.cl = Client()
        self.cl.login(os.getenv("INSTA_USERNAME"), os.getenv("INSTA_PASSWORD"))
        self.channel_id = 1364969535798640670
        self.check_dms_task.start()

    def load(self):
        try:
            with open(self.dateiname, 'r') as datei:
                inhalt = json.load(datei)
                return datetime.fromisoformat(inhalt["last_check"])
        except:
            return datetime.now()

    def save(self):
        now = datetime.now()
        data = {"last_check": now.isoformat()}
        with open(self.dateiname, 'w') as datei:
            json.dump(data, datei)

    @tasks.loop(seconds=30)
    async def check_dms_task(self):
        await self.check_dms()


    async def check_dms(self):
        threads = self.cl.direct_threads(amount=5)
        last_check = self.load()

        for thread in threads:
            user_map = {}
            for u in thread.users:
                user_map[u.pk] = u.username

            for msg in thread.messages[:20]:
                if msg.timestamp > last_check:
                    if msg.media_share:
                        media = msg.media_share


                        if media.media_type == 2 and media.product_type == "clips":
                            print(f"Reel gefunden von: {msg.user_id}")
                            print(f"Reel ID: {media.pk}")


                            try:
                                self.cl.video_download(media.pk, folder='dm_reels/')
                                print(f"✓ Reel heruntergeladen: {media.pk}")
                            except Exception as e:
                                print(f"Fehler beim Download: {e}")

        self.save()


def setup(bot):
    bot.add_cog(Insta(bot))