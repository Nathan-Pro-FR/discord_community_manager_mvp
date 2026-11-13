from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from bot.config import TIMEZONE
from sqlalchemy import select, func
from database.db import SessionLocal
from database.models import DailyStat

def record_message(guild_id, channel_id, user_id, attachments):
    today = datetime.now(ZoneInfo(TIMEZONE)).date()
    counts = {"images": 0, "videos": 0, "gifs": 0, "files": 0}
    for a in attachments:
        name = (a.filename or "").lower()
        content_type = (a.content_type or "").lower()
        if content_type.startswith("image/"):
            counts["images"] += 1
            if name.endswith(".gif") or "gif" in content_type:
                counts["gifs"] += 1
        elif content_type.startswith("video/") or name.endswith((".mp4", ".mov", ".webm")):
            counts["videos"] += 1
        else:
            counts["files"] += 1

    with SessionLocal() as db:
        row = db.scalar(select(DailyStat).where(
            DailyStat.guild_id == str(guild_id),
            DailyStat.day == today,
            DailyStat.channel_id == str(channel_id),
            DailyStat.user_id == str(user_id)
        ))
        if row is None:
            row = DailyStat(guild_id=str(guild_id), day=today,
                            channel_id=str(channel_id), user_id=str(user_id))
            db.add(row)
        row.messages += 1
        row.images += counts["images"]
        row.videos += counts["videos"]
        row.gifs += counts["gifs"]
        row.files += counts["files"]
        if attachments:
            row.media_posts += 1
        db.commit()

def totals(guild_id, start, end):
    with SessionLocal() as db:
        result = db.execute(select(
            func.coalesce(func.sum(DailyStat.messages), 0),
            func.coalesce(func.sum(DailyStat.media_posts), 0),
            func.count(func.distinct(DailyStat.user_id))
        ).where(
            DailyStat.guild_id == str(guild_id),
            DailyStat.day >= start,
            DailyStat.day <= end,
            DailyStat.user_id != "0"
        )).one()
        return {"messages": int(result[0]), "media_posts": int(result[1]), "active_members": int(result[2])}

def daily_totals(guild_id, day=None):
    day = day or datetime.now(ZoneInfo(TIMEZONE)).date()
    return totals(guild_id, day, day)

def channel_leaderboard(guild_id, start, end, limit=10):
    with SessionLocal() as db:
        rows = db.execute(select(
            DailyStat.channel_id, func.sum(DailyStat.messages).label("n")
        ).where(
            DailyStat.guild_id == str(guild_id),
            DailyStat.day >= start, DailyStat.day <= end
        ).group_by(DailyStat.channel_id).order_by(func.sum(DailyStat.messages).desc()).limit(limit)).all()
        return [(str(r[0]), int(r[1])) for r in rows]
