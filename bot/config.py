import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./community.db"
)
STATS_CHANNEL_ID = int(os.getenv("STATS_CHANNEL_ID", "0") or 0)
REPORTS_CHANNEL_ID = int(os.getenv("REPORTS_CHANNEL_ID", "0") or 0)
GUILD_ID = int(os.getenv("GUILD_ID", "0") or 0)
TIMEZONE = os.getenv("TIMEZONE", "Europe/Paris")
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8000"))
