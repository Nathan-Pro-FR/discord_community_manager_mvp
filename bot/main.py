import asyncio
import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.config import DISCORD_TOKEN, GUILD_ID, TIMEZONE
from database.db import init_db
from bot.services.reports import build_report_embed
from database.db import SessionLocal
from database.models import BotSetting
from sqlalchemy import select

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True

class CommunityBot(commands.Bot):
    async def setup_hook(self):
        init_db()
        await self.load_extension("bot.cogs.community")
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        scheduler.add_job(self.send_report, CronTrigger(day_of_week="mon", hour=9, minute=0), args=["weekly"])
        scheduler.add_job(self.send_report, CronTrigger(day=1, hour=9, minute=5), args=["monthly"])
        for month in (1, 4, 7, 10):
            scheduler.add_job(self.send_report, CronTrigger(month=month, day=1, hour=9, minute=10), args=["quarterly"])
        scheduler.start()
        self.scheduler = scheduler

    async def send_report(self, period):
        for guild in self.guilds:
            with SessionLocal() as db:
                setting = db.scalar(select(BotSetting).where(BotSetting.guild_id == str(guild.id)))
                channel_id = int(setting.reports_channel_id) if setting and setting.reports_channel_id else 0
            channel = guild.get_channel(channel_id) if channel_id else None
            if channel:
                try:
                    await channel.send(embed=build_report_embed(guild.id, period))
                except Exception as exc:
                    print(f"Report error for guild {guild.id}: {exc}")

bot = CommunityBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN manquant. Copie .env.example vers .env et renseigne le token.")
bot.run(DISCORD_TOKEN)
