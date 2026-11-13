import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import date, timedelta
from sqlalchemy import select
from database.db import SessionLocal
from database.models import BotSetting
from bot.config import STATS_CHANNEL_ID, REPORTS_CHANNEL_ID
from bot.services.stats import record_message, totals
from bot.services.embeds import build_live_embed
from bot.services.reports import build_report_embed

class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.refresh_embed.start()

    def cog_unload(self):
        self.refresh_embed.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return
        # Le bot conserve uniquement des compteurs, jamais le texte du message.
        record_message(message.guild.id, message.channel.id, message.author.id, message.attachments)

    @tasks.loop(minutes=1)
    async def refresh_embed(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            with SessionLocal() as db:
                setting = db.scalar(select(BotSetting).where(BotSetting.guild_id == str(guild.id)))
                if not setting:
                    continue
                channel_id = int(setting.stats_channel_id or STATS_CHANNEL_ID or 0)
                if not channel_id:
                    continue
                channel = guild.get_channel(channel_id)
                if not channel:
                    continue
                embed = build_live_embed(guild.id)
                try:
                    if setting.stats_message_id:
                        msg = await channel.fetch_message(int(setting.stats_message_id))
                        await msg.edit(embed=embed)
                    else:
                        msg = await channel.send(embed=embed)
                        setting.stats_message_id = str(msg.id)
                        setting.stats_channel_id = str(channel.id)
                        db.commit()
                except discord.NotFound:
                    msg = await channel.send(embed=embed)
                    setting.stats_message_id = str(msg.id)
                    setting.stats_channel_id = str(channel.id)
                    db.commit()

    @app_commands.command(name="setup", description="Créer une structure communautaire SFW")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        structure = {
            "📌 ACCUEIL": ["règlement", "annonces", "présentations"],
            "💬 COMMUNAUTÉ": ["général", "discussions", "questions"],
            "🖼️ MÉDIAS": ["photos", "vidéos", "créations"],
            "🤖 BOTS": ["commandes-bot"],
            "📊 STATISTIQUES": ["activité", "rapports"],
            "🛡️ MODÉRATION": ["signalements", "journal-modération"]
        }
        created = 0
        for category_name, channels in structure.items():
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            if category is None:
                category = await interaction.guild.create_category(category_name)
                created += 1
            for channel_name in channels:
                if discord.utils.get(category.text_channels, name=channel_name) is None:
                    await interaction.guild.create_text_channel(channel_name, category=category)
                    created += 1
        # Enregistre les salons dédiés à partir des noms de catégorie/salon.
        stats_cat = discord.utils.get(interaction.guild.categories, name="📊 STATISTIQUES")
        stats_channel = discord.utils.get(stats_cat.text_channels, name="activité") if stats_cat else None
        report_channel = discord.utils.get(stats_cat.text_channels, name="rapports") if stats_cat else None
        with SessionLocal() as db:
            setting = db.scalar(select(BotSetting).where(BotSetting.guild_id == str(interaction.guild.id)))
            if setting is None:
                setting = BotSetting(guild_id=str(interaction.guild.id))
                db.add(setting)
            if stats_channel:
                setting.stats_channel_id = str(stats_channel.id)
            if report_channel:
                setting.reports_channel_id = str(report_channel.id)
            db.commit()
        await interaction.followup.send(f"Configuration terminée. {created} éléments créés ou ajoutés.", ephemeral=True)

    @app_commands.command(name="stats", description="Afficher les statistiques des 7 derniers jours")
    async def stats(self, interaction: discord.Interaction):
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=6)
        data = totals(interaction.guild_id, start, end)
        embed = discord.Embed(title="📊 Statistiques — 7 derniers jours", color=discord.Color.blurple())
        embed.add_field(name="Messages", value=f"{data['messages']:,}", inline=True)
        embed.add_field(name="Publications médias", value=f"{data['media_posts']:,}", inline=True)
        embed.add_field(name="Membres actifs", value=f"{data['active_members']:,}", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="report", description="Générer un rapport")
    @app_commands.choices(period=[
        app_commands.Choice(name="Hebdomadaire", value="weekly"),
        app_commands.Choice(name="Mensuel", value="monthly"),
        app_commands.Choice(name="Trimestriel", value="quarterly")
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def report(self, interaction: discord.Interaction, period: app_commands.Choice[str]):
        embed = build_report_embed(interaction.guild_id, period.value)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Community(bot))
