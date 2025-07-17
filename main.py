import discord
from discord.ext import commands
from sonnet import ask_sonnet  # sonnet.py에서 함수 불러오기

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

@bot.command()
async def 안젤라(ctx, *, message: str):
    await ctx.send("🤖 생각 중...")  # 응답 대기 중 메시지
    reply = ask_sonnet(message)
    await ctx.send(reply)

# 디스코드 봇 토큰
bot.run("your_discord_token_here")
