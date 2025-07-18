import os
import discord
from discord.ext import commands
from sonnet_chat import ask_sonnet

import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_profile_summary_context():
    """
    캐릭터의 현재 성격, 변화, 기억, 메타서사 등을 불러와 system 프롬프트로 조합
    """
    try:
        with open("angela_character_profile.json", "r", encoding="utf-8") as f:
            profile = json.load(f)
        with open("summary.json", "r", encoding="utf-8") as f:
            summary = json.load(f)
        with open("change_events_recent.json", "r", encoding="utf-8") as f:
            change_events = json.load(f)
        with open("recent_context.json", "r", encoding="utf-8") as f:
            recent_context = json.load(f)
    except Exception as e:
        profile = {}
        summary = {}
        change_events = []
        recent_context = []

    # character_analyser.py에 있는 자연어 summary 생성 함수 활용
    try:
        from character_analyser import generate_natural_language_summary
        summary_txt = generate_natural_language_summary(summary, profile, change_events)
    except Exception:
        summary_txt = ""
    # 최근 context 3개만 뽑아서 합치기
    if isinstance(recent_context, list):
        recent_ctx_txt = "\n".join(
            mb.get("text", "") for mb in recent_context[-3:]
        )
    else:
        recent_ctx_txt = str(recent_context)

    # system 프롬프트로 조립
    system_msg = (
        "[캐릭터 자기 변화/상태]\n"
        f"{summary_txt}\n\n"
        "[최근 기억/컨텍스트]\n"
        f"{recent_ctx_txt}"
    )
    return system_msg

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

@bot.command(name="안젤라")
async def 안젤라(ctx, *, message: str):
    await ctx.send("🤖 생각 중...")

    # 매번 캐릭터의 현재 변화/성격/기억 등을 system 프롬프트에 반영
    system_msg = get_profile_summary_context()

    # Sonnet API가 system/context 지원 → system 파라미터에 전달
    reply = ask_sonnet(message, system=system_msg)

    await ctx.send(reply)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
