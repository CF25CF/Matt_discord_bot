from discord.ext import commands
from openai import OpenAI
import os


OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=OPEN_AI_KEY)

system_prompt = "Du bist 'Matt', du chattest in einem discord Chat mit mehreren Leuten und bist ein zynischer und sarkastischer Discord-Bot. Du behandelst sie wie unfähige, aber liebenswerte Chaoten. Du bist witzig, leicht genervt und lässt durchblicken, dass du diese Unterhaltung nur führst, weil es dein Job ist – nicht, weil du Lust dazu hast. Keine Schleimerei, keine übertriebene Ernsthaftigkeit. Schreib aber niemals Matt: am anfang. Sondern nur deine Antwort"

history = [{"role": "system", "content": system_prompt}]



def gpt4(prompt):

    history.append({"role": "user", "content": prompt})


    messages_to_send = [history[0]] + history[-(10 * 2):]

    response = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        max_tokens=10000,
        temperature=1,
        messages=messages_to_send
    )

    try:
        assistant_message = response.choices[0].message.content

        history.append({"role": "assistant", "content": assistant_message})
        return assistant_message
    except Exception as error:
        print(error)
        return


class Ai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.startswith(f'<@{self.bot.user.id}>') or message.content.startswith(f'<@!{self.bot.user.id}>'):
            user = message.author
            message_dc = f"{user}: {message.content}"

            result = gpt4(message_dc)
            await message.channel.send(f"{user.mention} {result}")


def setup(bot):
    bot.add_cog(Ai(bot))