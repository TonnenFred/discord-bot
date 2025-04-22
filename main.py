import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "Bot ist online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Slash-Commands synchronisiert: {len(synced)}")
    except Exception as e:
        print(f"❌ Fehler beim Sync: {e}")

REQUIRED_ROLE = "Loaner"

@bot.tree.command(name="loan", description="Berechnet Collateral und Rückzahlung basierend auf dem Kreditbetrag.")
@app_commands.describe(betrag="z.B. 200k, 1.5m, 100000")
async def loan(interaction: discord.Interaction, betrag: str):
    user = interaction.user
    has_role = any(role.name == REQUIRED_ROLE for role in user.roles)

    if not has_role:
        await interaction.response.send_message("❌ Du hast keine Berechtigung, diesen Befehl zu verwenden.", ephemeral=True)
        return

    multiplier = 1
    if betrag.lower().endswith("k"):
        multiplier = 1000
        betrag = betrag[:-1]
    elif betrag.lower().endswith("m"):
        multiplier = 1000000
        betrag = betrag[:-1]

    try:
        loan_amount = int(float(betrag) * multiplier)
        collateral = int(loan_amount * 1.5)
        repayment = int(loan_amount * 1.25)

        await interaction.response.send_message(
            f"💰 **Loan Summary**\n"
            f"🔹 Loan: {loan_amount:,}\n"
            f"🔹 Required collateral: {collateral:,}\n"
            f"🔹 Repayment: {repayment:,}",
            ephemeral=True
        )
    except ValueError:
        await interaction.response.send_message("❌ Ungültiger Betrag. Beispiel: `/loan betrag: 200k`", ephemeral=True)

keep_alive()

bot.run(os.getenv("DISCORD_TOKEN"))
