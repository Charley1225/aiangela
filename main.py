import discord
import os

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 안젤라 작동 중! 로그인됨: {bot.user}")

@bot.slash_command(name="hello", description="봇이 인사해요")
async def hello(ctx):
    await ctx.respond("안녕! 나는 안젤라야 💬")

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
