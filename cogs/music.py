import discord
from discord.commands import Option
from discord.ext.pages import Paginator, Page
import yt_dlp
import random
import asyncio
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from base64 import b64encode
import spotipy
from discord.ext import commands
from discord.commands import slash_command
import os

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_access_token(client_id, client_secret, refresh_token):
    url = "https://accounts.spotify.com/api/token"
    auth_header = b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.voice_client = None
        self.volume = 1.0


    async def scrape_liked_songs(self, ACCESS_TOKEN):
        def get_liked_songs():
            sp = spotipy.Spotify(auth=ACCESS_TOKEN)

            offset = 0
            limit = 50
            tracks = []

            while True:
                response = sp.current_user_saved_tracks(limit=limit, offset=offset)
                items = response.get('items', [])
                if not items:
                    break
                tracks.extend(items)
                offset += limit

            titles = []
            for item in tracks:
                track = item.get('track')
                if track and isinstance(track, dict):
                    name = track.get('name')
                    artists = track.get('artists', [])
                    if name and artists:
                        artist_name = artists[0].get('name', 'Unbekannter Künstler')
                        titles.append({
                            'title': f"{name} – {artist_name}",
                            'url': f"ytsearch1:{name} {artist_name}"
                        })
            return titles

        titles = await asyncio.to_thread(get_liked_songs)

        return titles


    async def scrape_spotify(self, playlist_url):
        def get_titles():
            auth = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
            sp = spotipy.Spotify(auth_manager=auth)

            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            tracks = []
            offset = 0
            limit = 100

            while True:
                response = sp.playlist_items(playlist_id, limit=limit, offset=offset)
                items = response.get('items', [])
                if not items:
                    break
                tracks.extend(items)
                offset += limit

            titles = []
            for item in tracks:
                track = item.get('track')
                if track and isinstance(track, dict):
                    name = track.get('name')
                    artists = track.get('artists', [])
                    if name and artists:
                        artist_name = artists[0].get('name', 'Unbekannter Künstler')
                        titles.append({'title': f"{name} – {artist_name}", 'url': f"ytsearch1:{name} {artist_name}"})
            return titles

        titles = await asyncio.to_thread(get_titles)
        return titles


    async def connected(self, ctx):
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_connected:
            self.voice_client = vc
            return True
        else:
            return False


    async def scrape(self, song):
        is_link = song.startswith("http://") or song.startswith("https://")

        if is_link:
            ydl_options = {
                'format': 'bestaudio',
                'quiet': True,
                'extract_flat': False
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(song, download=False)

            video_id = info.get('id')
            title = info.get('title') or 'Unbekannter Titel'
            url = f"https://www.youtube.com/watch?v={video_id}"

            return {'title': title, 'url': url}



        else:
            ydl_options = {
                'format': 'bestaudio',
                'quiet': True,
                'extract_flat': True
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(f"ytsearch1:{song}", download=False)

                if 'entries' in info:
                    first = info['entries'][0]
                    url = first['url']
                    title = first.get('title')

                    return {'title': title, 'url': url}

                else:
                    video_id = info.get('id')
                    title = info.get('title') or 'Unbekannter Titel'
                    url = f"https://www.youtube.com/watch?v={video_id}"

                    return {'title': title, 'url': url}



    async def scrape_playlist(self, playlist_url):
        ydl_options = {
            'format': 'bestaudio',
            'quiet': True,
            'extract_flat': True,
            'default_search': 'auto'
        }

        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            results = []

            if 'entries' in info:
                for entry in info['entries']:
                    video_id = entry.get('id')
                    title = entry.get('title') or 'Unbekannter Titel'
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    results.append({'title': title, 'url': url})

            return results

    async def play_song(self, ctx):
        if not self.queue:
            await ctx.followup.send("📭 Warteschlange ist leer.")
            return

        ydl_options = {
            'format': 'bestaudio',
            'default_search': 'ytsearch',
            'quiet': True,
            'extract_flat': False
        }

        song = self.queue.pop(0)

        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(song['url'], download=False)

            if 'entries' in info:
                first = info['entries'][0]
                url = first['url']
                title = first.get('title')

            else:
                url = info['url']
                title = info.get('title')

        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
        source = discord.PCMVolumeTransformer(source, volume=self.volume)

        def song_loop(error):
            if self.queue:
                asyncio.run_coroutine_threadsafe(self.play_song(ctx), self.bot.loop)


        self.voice_client.play(source, after=song_loop)
        await ctx.followup.send(f"🎶 Spiele: **{title}**")

    @slash_command(name="join", description="lasse Matt deinem Voice-Chat joinen")
    async def join_command(self, ctx):
        if not await self.connected(ctx):
            self.voice_client = await ctx.author.voice.channel.connect()
            await ctx.respond("✅ Matt ist dem Voice-Chat beigetreten.")
        elif await self.connected(ctx) and self.voice_client.channel != ctx.author.voice.channel:
            await ctx.respond("❌ Matt ist bereits in einem Voice-Chat.")
        else:
            await ctx.respond("🔵 Matt ist bereits in deinem Voice-Chat.")

    async def join(self, ctx):
        if not await self.connected(ctx):
            self.voice_client = await ctx.author.voice.channel.connect()
            await ctx.respond("✅ Matt ist dem Voice-Chat beigetreten.")
        elif await self.connected(ctx) and self.voice_client.channel != ctx.author.voice.channel:
            await ctx.respond("❌ Matt ist bereits in einem Voice-Chat.")


    @slash_command(name="leave", description="lasse Matt den Voice-Chat verlassen")
    async def leave(self, ctx):
        if await self.connected(ctx):
            await self.voice_client.disconnect()
            self.voice_client = None
            await ctx.respond("👋 Matt hat den Voice-Chat verlassen")
        else:
            await ctx.respond("❌ Matt ist in keinem Voice-Chat.")



    @slash_command(name="play", description="Spiele ein Lied")
    async def play(self, ctx, query: Option(str, "YouTube-Link oder Suchbegriff", name="liedname")):
        await ctx.defer()

        await self.join(ctx)
        song = await self.scrape(query)
        self.queue.append(song)


        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)
        else:
            title = song['title']
            await ctx.followup.send(f"➕ **{title}** wurde der Warteschlange hinzugefügt.")

    @slash_command(name="next", description="Spiele ein Lied als nächstes")
    async def next(self, ctx, query: Option(str, "YouTube-Link oder Suchbegriff", name="liedname")):
        await ctx.defer()

        await self.join(ctx)
        song = await self.scrape(query)
        self.queue.insert(0, song)

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)
        else:
            title = song['title']
            await ctx.followup.send(f"➕ **{title}** wird als **nächstes** abgespielt.")

    @slash_command(name="pause", description="Pausiert oder setzt das aktuelle Lied fort")
    async def pause(self, ctx):
        if not await self.connected(ctx) or (not self.voice_client.is_playing() and not self.voice_client.is_paused()):
            await ctx.respond("❌ Es läuft gerade kein Lied.")
            return

        if self.voice_client.is_paused():
            self.voice_client.resume()
            await ctx.respond("▶️ Fortgesetzt.")
        else:
            self.voice_client.pause()
            await ctx.respond("⏸️ Pausiert.")

    @slash_command(name="skip", description="Überspringt das aktuelle Lied")
    async def skip(self, ctx):
        if await self.connected(ctx) and self.voice_client.is_playing():
            self.voice_client.stop()
            await ctx.respond("⏭️ Lied übersprungen.")
        else:
            await ctx.respond("es läuft gerade kein Lied")

    @slash_command(name="lautstärke", description="Setzt die Lautstärke von 1 (leise) bis 10 (laut)")
    async def volume(self, ctx, lautstärke: Option(int, "Lautstärke von 1 bis 10", min_value=1, max_value=10)):
        self.volume = lautstärke / 10
        await ctx.respond(f"🔊 Lautstärke auf {lautstärke}/10 gesetzt.")

    @slash_command(name="warteschlange", description="Zeigt die aktuelle Warteschlange")
    async def queue_cmd(self, ctx):
        if not self.queue:
            await ctx.respond("📭 Warteschlange ist leer.")
        else:
            pages = []
            description = ""

            for index, song in enumerate(self.queue):
                description += f"`{index + 1}.` {song['title']}\n"

                if (index + 1) % 10 == 0:
                    embed = discord.Embed(title=f"🎶 Aktuelle Warteschlange: (**{len(self.queue)}**)", description=description, color=discord.Color.blue())
                    embed.set_thumbnail(url=ctx.guild.icon.url)
                    page = Page(embeds=[embed])
                    pages.append(page)
                    description = ""

            if description:
                embed = discord.Embed(title="🎶 Aktuelle Warteschlange:", description=description, color=discord.Color.blue())
                embed.set_thumbnail(url=ctx.guild.icon.url)
                pages.append(Page(embeds=[embed]))

            paginator = Paginator(pages=pages)
            await paginator.respond(ctx.interaction)

    @slash_command(name="shuffle", description="Mischt die aktuelle Warteschlange")
    async def shuffle(self, ctx):
        if self.queue:
            random.shuffle(self.queue)
            await ctx.respond("🔀 Warteschlange wurde zufällig gemischt.")
        else:
            await ctx.respond("❌ Warteschlange ist leer und kann nicht gemischt werden.")

    @slash_command(name="clear", description="Leert die aktuelle Warteschlange")
    async def clear(self, ctx):
        self.queue.clear()
        await ctx.respond("🗑️ Warteschlange wurde geleert.")


    @slash_command(name="playlist_spotify", description="Spiele eine Playlist")
    async def playlist_spotify(self, ctx, query: Option(str, "Playlist link", name="link")):
        await ctx.defer()

        await self.join(ctx)

        titles = await self.scrape_spotify(query)
        self.queue.extend(titles)

        await ctx.followup.send(f"➕ es wurden **{len(titles)}** Lieder der Warteschlange hinzugefügt.")

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)

    @slash_command(name="playlist", description="Spiele eine Playlist")
    async def playlist(self, ctx, query: Option(str, "Playlist link", name="link")):
        await ctx.defer()


        await self.join(ctx)
        songs = await self.scrape_playlist(query)
        self.queue.extend(songs)

        await ctx.followup.send(f"➕ es wurden **{len(songs)}** Lieder der Warteschlange hinzugefügt.")

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)




    async def playlist_user(self, ctx, playlist_url):
        await ctx.defer()

        await self.join(ctx)
        songs = await self.scrape_playlist(playlist_url)
        self.queue.extend(songs)

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)

        await ctx.followup.send(f"➕ es wurden **{len(songs)}** Lieder der Warteschlange hinzugefügt.")



    @slash_command(name="playlist_chris", description="Spiele Chris seine Playlist")
    async def playlist_chris(self, ctx):
        playlist = "https://youtube.com/playlist?list=PLwMseQeDKcznVL7KGfTu_klfbgI0UA41g&si=V9w1RcInGmTrL_AI"
        await self.playlist_user(ctx, playlist)

    @slash_command(name="playlist_emanuelle", description="Spiele Emanuelle seine Playlist")
    async def playlist_emanuelle(self, ctx):
        playlist = "https://music.youtube.com/playlist?list=PLkIBS6Hz1ixJDWwG3Ad7ZCD36avxmUiSr&si=HN80BpLr5u8Tp4eI"
        await self.playlist_user(ctx, playlist)

    @slash_command(name="playlist_marcel", description="Spiele Marcel seine Playlist")
    async def playlist_marcel(self, ctx):
        playlist = "https://open.spotify.com/playlist/1osHjsciZoYOB9Kg1Lne8S?si=EsjqQKL8SoiZ7h3kVxDuRw&pi=7bGz_SsDS5mA-"
        await self.playlist_spotify(ctx, playlist)

    async def playlist_likes_songs(self, ctx, REFRESHTOKEN):
        ACCESS_TOKEN = get_spotify_access_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REFRESHTOKEN)

        await self.join(ctx)
        titles = await self.scrape_liked_songs(ACCESS_TOKEN)
        self.queue.extend(titles)

        if not self.voice_client.is_playing() and not self.voice_client.is_paused():
            await self.play_song(ctx)

        await ctx.followup.send(f"➕ es wurden **{len(titles)}** Lieder der Warteschlange hinzugefügt.")

    @slash_command(name="playlist_daniel", description="Spiele Daniel seine Spotify Playlist")
    async def playlist_daniel(self, ctx):
        await ctx.defer()
        DANIEL_REFRESH_TOKEN = "AQAmQwRmOkeHS2ggmrcgtmhhsrm8Ocs-nWNMf2yiOkxK6Ovfbwq3zGfYtE2ykQsR3TfBNSQqYv7oamgB8GvnQfiWmnDxMTESqoSPvohLsiL2jtKA7nsVltlQKD87sGxNthA"

        await self.playlist_likes_songs(ctx, DANIEL_REFRESH_TOKEN)


    @slash_command(name="music_help", description="Zeige dir alle Commands für den Musik-Bot an")
    async def help(self, ctx):
        embed = discord.Embed(
            title="📖 Musik-Bot Hilfe",
            description="**Hier findest du alle verfügbaren Musik-Befehle:**",
            color=discord.Color.blurple()
        )

        embed.add_field(name="✅ **/join**", value="_Tritt deinem Voice-Channel bei_", inline=False)
        embed.add_field(name="👋 **/leave**", value="_Verlässt den Voice-Channel_", inline=False)
        embed.add_field(name="▶️ **/play**", value="_Spielt den Song oder fügt ihn zur Warteschlange hinzu_", inline=False)
        embed.add_field(name="↩️ **/next**", value="_Setzt den Song an erste Stelle der Warteschlange_", inline=False)
        embed.add_field(name="⏸ **/pause**", value="_Pausiert oder setzt den Song fort_", inline=False)
        embed.add_field(name="⏩ **/skip**", value="_Überspringt den aktuellen Song_", inline=False)
        embed.add_field(name="🔊 **/lautstärke**", value="_Stellt die Lautstärke von 1–10 ein_", inline=False)
        embed.add_field(name="📄 **/warteschlange**", value="_Zeigt die aktuelle Warteschlange_", inline=False)
        embed.add_field(name="🔀 **/shuffle**", value="_Mischt die aktuelle Warteschlange_", inline=False)
        embed.add_field(name="🧹 **/clear**", value="_Leert die Warteschlange_", inline=False)
        embed.add_field(name="📜 **/playlist**", value="_Spielt eine beliebige Playlist ab_", inline=False)
        embed.add_field(name="📜 **/playlist_chris**", value="_Christians Playlist_", inline=False)
        embed.add_field(name="📜 **/playlist_(euer Name)**", value="_Spielt eure persönliche Playlist ab_", inline=False)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Music(bot))

