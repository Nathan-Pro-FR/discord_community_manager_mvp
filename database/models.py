from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from database.db import Base

class DailyStat(Base):
    __tablename__ = "daily_stats"
    __table_args__ = (UniqueConstraint("guild_id", "day", "channel_id", "user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[str] = mapped_column(String(32), index=True)
    day: Mapped[object] = mapped_column(Date, index=True)
    channel_id: Mapped[str] = mapped_column(String(32), default="0")
    user_id: Mapped[str] = mapped_column(String(32), default="0")
    messages: Mapped[int] = mapped_column(Integer, default=0)
    media_posts: Mapped[int] = mapped_column(Integer, default=0)
    images: Mapped[int] = mapped_column(Integer, default=0)
    videos: Mapped[int] = mapped_column(Integer, default=0)
    gifs: Mapped[int] = mapped_column(Integer, default=0)
    files: Mapped[int] = mapped_column(Integer, default=0)

class BotSetting(Base):
    __tablename__ = "bot_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    stats_message_id: Mapped[str] = mapped_column(String(32), default="")
    stats_channel_id: Mapped[str] = mapped_column(String(32), default="")
    reports_channel_id: Mapped[str] = mapped_column(String(32), default="")

class ReportRecord(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[str] = mapped_column(String(32), index=True)
    period_type: Mapped[str] = mapped_column(String(20))
    start_day: Mapped[object] = mapped_column(Date)
    end_day: Mapped[object] = mapped_column(Date)
    messages: Mapped[int] = mapped_column(Integer, default=0)
    media_posts: Mapped[int] = mapped_column(Integer, default=0)
    active_members: Mapped[int] = mapped_column(Integer, default=0)
    previous_messages: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
