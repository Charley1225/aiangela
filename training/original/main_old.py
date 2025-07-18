import os
import discord
from discord.ext import commands
from sonnet_chat import ask_sonnet

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

@bot.command(name="안젤라")
async def 안젤라(ctx, *, message: str):
    await ctx.send("🤖 생각 중...")
    reply = ask_sonnet(message)
    await ctx.send(reply)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
