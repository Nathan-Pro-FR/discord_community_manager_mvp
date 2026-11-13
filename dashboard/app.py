from fastapi import FastAPI
from datetime import date, timedelta
from bot.services.stats import totals, channel_leaderboard

app = FastAPI(title="Discord Community Manager API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/guilds/{guild_id}/stats")
def guild_stats(guild_id: int, days: int = 7):
    if days < 1 or days > 365:
        return {"error": "days doit être compris entre 1 et 365"}
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return {"guild_id": guild_id, "start": str(start), "end": str(end),
            **totals(guild_id, start, end)}

@app.get("/guilds/{guild_id}/channels")
def guild_channels(guild_id: int, days: int = 7):
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return {"channels": [{"channel_id": cid, "messages": n}
                         for cid, n in channel_leaderboard(guild_id, start, end)]}
