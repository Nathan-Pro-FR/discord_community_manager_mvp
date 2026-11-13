from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from bot.config import TIMEZONE
from calendar import monthrange
import discord
from database.db import SessionLocal
from database.models import ReportRecord
from bot.services.stats import totals, channel_leaderboard

def previous_period(period_type, today=None):
    today = today or datetime.now(ZoneInfo(TIMEZONE)).date()
    if period_type == "weekly":
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=6)
    elif period_type == "monthly":
        end = today.replace(day=1) - timedelta(days=1)
        start = end.replace(day=1)
        prev_end = start - timedelta(days=1)
        prev_start = prev_end.replace(day=1)
    else:
        quarter = (today.month - 1) // 3
        current_q_start = date(today.year, quarter * 3 + 1, 1)
        end = current_q_start - timedelta(days=1)
        start = date(end.year, ((end.month - 1) // 3) * 3 + 1, 1)
        prev_end = start - timedelta(days=1)
        prev_start = date(prev_end.year, ((prev_end.month - 1) // 3) * 3 + 1, 1)
    return start, end, prev_start, prev_end

def pct_change(current, previous):
    if previous == 0:
        return "Nouvelle activité" if current else "0 %"
    return f"{((current - previous) / previous) * 100:+.1f} %"

def build_report_embed(guild_id, period_type):
    start, end, pstart, pend = previous_period(period_type)
    current = totals(guild_id, start, end)
    previous = totals(guild_id, pstart, pend)
    labels = {"weekly": "Hebdomadaire", "monthly": "Mensuel", "quarterly": "Trimestriel"}
    embed = discord.Embed(
        title=f"📈 Rapport {labels[period_type]}",
        description=f"Période : {start:%d/%m/%Y} au {end:%d/%m/%Y}",
        color=discord.Color.green()
    )
    embed.add_field(name="Messages", value=f"{current['messages']:,}\n{pct_change(current['messages'], previous['messages'])}", inline=True)
    embed.add_field(name="Publications médias", value=f"{current['media_posts']:,}\n{pct_change(current['media_posts'], previous['media_posts'])}", inline=True)
    embed.add_field(name="Membres actifs", value=f"{current['active_members']:,}\n{pct_change(current['active_members'], previous['active_members'])}", inline=True)
    leaders = channel_leaderboard(guild_id, start, end)
    if leaders:
        embed.add_field(name="Salons les plus actifs", value="\n".join(f"<#{cid}> — {n:,} messages" for cid, n in leaders), inline=False)
    embed.set_footer(text="Comparaison avec la période précédente • Données agrégées")
    with SessionLocal() as db:
        db.add(ReportRecord(
            guild_id=str(guild_id), period_type=period_type,
            start_day=start, end_day=end,
            messages=current["messages"], media_posts=current["media_posts"],
            active_members=current["active_members"],
            previous_messages=previous["messages"]
        ))
        db.commit()
    return embed
