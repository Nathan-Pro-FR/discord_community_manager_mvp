import discord
from datetime import date
from bot.services.stats import daily_totals

def build_live_embed(guild_id):
    stats = daily_totals(guild_id)
    embed = discord.Embed(
        title="📊 Activité du serveur",
        description=f"Statistiques du {date.today().strftime('%d/%m/%Y')}",
        color=discord.Color.blurple()
    )
    embed.add_field(name="Messages", value=f"{stats['messages']:,}", inline=True)
    embed.add_field(name="Publications avec médias", value=f"{stats['media_posts']:,}", inline=True)
    embed.add_field(name="Membres actifs", value=f"{stats['active_members']:,}", inline=True)
    embed.set_footer(text="Actualisation automatique • Compteurs agrégés")
    return embed
