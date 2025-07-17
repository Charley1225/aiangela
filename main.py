import discord
from discord.ext import commands
from sonnet_chat import ask_sonnet

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def 안젤라(ctx, *, message):
    await ctx.defer()
    reply = ask_sonnet(message)
    await ctx.send(reply)

bot.run(os.getenv("DISCORD_TOKEN"))
