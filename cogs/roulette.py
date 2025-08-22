import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import random
import aiosqlite
import asyncio
from datetime import datetime


RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
BLACK_NUMBERS = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]


class RouletteView(discord.ui.View):
    def __init__(self, bet_amount, user_id, cog):
        super().__init__(timeout=30)
        self.bet_amount = bet_amount
        self.user_id = user_id
        self.cog = cog
        self.value = None

    @discord.ui.button(label="Rot", style=discord.ButtonStyle.danger)
    async def red_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Das ist nicht dein Spiel!", ephemeral=True)
            return
        await self.process_bet(interaction, "red")

    @discord.ui.button(label="Schwarz", style=discord.ButtonStyle.secondary)
    async def black_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Das ist nicht dein Spiel!", ephemeral=True)
            return
        await self.process_bet(interaction, "black")

    @discord.ui.button(label="Grün", style=discord.ButtonStyle.success)
    async def green_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Das ist nicht dein Spiel!", ephemeral=True)
            return
        await self.process_bet(interaction, "green")

    async def process_bet(self, interaction: discord.Interaction, color: str):

        for item in self.children:
            item.disabled = True


        result_color, number = self.cog.spin_roulette()


        if color == result_color:
            if color == "green":
                winnings = self.bet_amount * 35
            else:
                winnings = self.bet_amount * 2
            won = True
        else:
            winnings = 0
            won = False


        current_balance = await self.cog.get_balance(self.user_id)
        new_balance = current_balance - self.bet_amount + winnings
        await self.cog.update_balance(self.user_id, new_balance)


        embed = discord.Embed(
            title="🎰 Roulette Ergebnis",
            color=discord.Color.green() if won else discord.Color.red(),
            timestamp=datetime.utcnow()
        )

        embed.add_field(name="Gewinnzahl", value=f"**{number}**", inline=True)
        embed.add_field(name="Farbe", value=f"**{result_color.capitalize()}**", inline=True)
        embed.add_field(name="Deine Wahl", value=f"**{color.capitalize()}**", inline=True)

        if won:
            embed.add_field(name="Ergebnis", value=f"✅ Gewonnen: **{winnings}** Coins", inline=False)
        else:
            embed.add_field(name="Ergebnis", value=f"❌ Verloren: **{self.bet_amount}** Coins", inline=False)

        embed.add_field(name="Neuer Kontostand", value=f"💰 **{new_balance}** Coins", inline=False)

        embed.set_footer(text=f"Gespielt von {interaction.user.name}")

        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class Roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "roulette.db"
        self.bot.loop.create_task(self.setup_database())

    async def setup_database(self):
        """Erstellt die Datenbank-Tabellen wenn sie nicht existieren"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 5000,
                    total_bets INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_losses INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bet_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    bet_amount INTEGER,
                    bet_color TEXT,
                    result_color TEXT,
                    result_number INTEGER,
                    won BOOLEAN,
                    winnings INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def get_balance(self, user_id: int) -> int:
        """Holt den Kontostand eines Nutzers"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                else:
                    # Neuer Nutzer - erstelle Eintrag mit Startguthaben
                    await db.execute(
                        "INSERT INTO users (user_id, balance) VALUES (?, ?)",
                        (user_id, 5000)
                    )
                    await db.commit()
                    return 5000

    async def update_balance(self, user_id: int, new_balance: int):
        """Aktualisiert den Kontostand eines Nutzers"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET balance = ? WHERE user_id = ?",
                (new_balance, user_id)
            )
            await db.commit()

    async def update_stats(self, user_id: int, won: bool):
        """Aktualisiert die Statistiken eines Nutzers"""
        async with aiosqlite.connect(self.db_path) as db:
            if won:
                await db.execute(
                    "UPDATE users SET total_bets = total_bets + 1, total_wins = total_wins + 1 WHERE user_id = ?",
                    (user_id,)
                )
            else:
                await db.execute(
                    "UPDATE users SET total_bets = total_bets + 1, total_losses = total_losses + 1 WHERE user_id = ?",
                    (user_id,)
                )
            await db.commit()

    def spin_roulette(self) -> tuple[str, int]:
        """Dreht das Roulette-Rad und gibt Farbe und Zahl zurück"""
        number = random.randint(0, 36)
        if number == 0:
            return "green", number
        elif number in RED_NUMBERS:
            return "red", number
        else:
            return "black", number

    @slash_command(name="roulette", description="Spiele Roulette!")
    async def roulette(
            self,
            ctx: discord.ApplicationContext,
            amount: Option(int, "Wie viel möchtest du setzen?", min_value=10, max_value=10000)
    ):
        user_id = ctx.author.id
        balance = await self.get_balance(user_id)

        if amount > balance:
            embed = discord.Embed(
                title="❌ Nicht genug Coins!",
                description=f"Du hast nur **{balance}** Coins verfügbar.\nDein Einsatz: **{amount}** Coins",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="🎰 Roulette",
            description=f"**Einsatz:** {amount} Coins\n**Kontostand:** {balance} Coins\n\nWähle eine Farbe:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Auszahlungen", value="Rot: 2x\nSchwarz: 2x\nGrün: 35x", inline=False)

        view = RouletteView(amount, user_id, self)
        await ctx.respond(embed=embed, view=view)

    @slash_command(name="balance", description="Zeigt deinen Kontostand")
    async def balance(self, ctx: discord.ApplicationContext):
        balance = await self.get_balance(ctx.author.id)

        embed = discord.Embed(
            title="💰 Kontostand",
            description=f"**{ctx.author.mention}**\n\nDein aktueller Kontostand: **{balance}** Coins",
            color=discord.Color.gold()
        )
        await ctx.respond(embed=embed)

    @slash_command(name="stats", description="Zeigt deine Roulette-Statistiken")
    async def stats(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id

        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                    "SELECT balance, total_bets, total_wins, total_losses FROM users WHERE user_id = ?",
                    (user_id,)
            ) as cursor:
                row = await cursor.fetchone()

                if not row:
                    await ctx.respond("❌ Du hast noch nicht gespielt!", ephemeral=True)
                    return

                balance, total_bets, total_wins, total_losses = row

                win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0

                embed = discord.Embed(
                    title="📊 Deine Roulette-Statistiken",
                    color=discord.Color.blue()
                )
                embed.add_field(name="💰 Kontostand", value=f"**{balance}** Coins", inline=True)
                embed.add_field(name="🎲 Gesamt Spiele", value=f"**{total_bets}**", inline=True)
                embed.add_field(name="📈 Gewinnrate", value=f"**{win_rate:.1f}%**", inline=True)
                embed.add_field(name="✅ Gewonnen", value=f"**{total_wins}**", inline=True)
                embed.add_field(name="❌ Verloren", value=f"**{total_losses}**", inline=True)

                await ctx.respond(embed=embed)

    @slash_command(name="daily", description="Hole dir dein tägliches Bonus-Geld!")
    async def daily(self, ctx: discord.ApplicationContext):
        user_id = ctx.author.id
        daily_amount = 1000

        balance = await self.get_balance(user_id)
        new_balance = balance + daily_amount
        await self.update_balance(user_id, new_balance)

        embed = discord.Embed(
            title="🎁 Täglicher Bonus!",
            description=f"Du hast **{daily_amount}** Coins erhalten!\n\nNeuer Kontostand: **{new_balance}** Coins",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Roulette(bot))