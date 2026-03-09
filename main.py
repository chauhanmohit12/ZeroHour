import discord
from discord import app_commands
import asyncio
import time
import requests
from datetime import datetime,timezone
import os
from dotenv import load_dotenv
from flask import Flask
import threading


def seconds_from_utc(date_str: str) -> int:
    """
    Takes a date like 'Mar 19, 2026'
    Returns seconds between current UTC time
    and 12:01 AM UTC of that date.
    """

    # Parse the date
    parsed_date = datetime.strptime(date_str, "%b %d, %Y")

    # Set time to 12:01 AM
    target_time = parsed_date.replace(hour=0, minute=1, second=0, microsecond=0)

    # Make it UTC aware
    target_time = target_time.replace(tzinfo=timezone.utc)

    # Current UTC time
    now = datetime.now(timezone.utc)

    # Difference in seconds
    return int((target_time - now).total_seconds())

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()   # global sync
        print("Global commands synced")

client = Client()

@client.tree.command(name="test", description="Test command")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("Working")
    
@client.tree.command(name="timer", description="Test timer")
async def create_timer(interaction: discord.Interaction,appid: str):
    
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

    response = requests.get(url)
    data = response.json()

    game = data[str(appid)]["data"]

    name = game["name"]
    description = game["short_description"]
    banner = game["header_image"]

    seconds = seconds_from_utc(str(game["release_date"]["date"]))+1
    end_time = int(time.time()) + seconds

    embed = discord.Embed(
        title=name,
        url="https://store.steampowered.com/app/"+appid,
        description=(
            f"**Release time: <t:{end_time}:R>**"
        ),
        color=discord.Color.blue()
    )
    
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/hyGUpE441sdRq43OcsqHXnTUi3I0oUXnt10rOB2maSg/https/cdn.discordapp.com/emojis/1073161249006821406.webp?format=webp&width=160&height=160")
    embed.set_footer(text="Timer by ZeroHour",icon_url="https://cdn.discordapp.com/avatars/1479830293090275398/71bb799a0d189fba798d14c0ba7b3671")
    embed.add_field(name="About", value=description, inline=False)
    embed.set_image(url=banner)

    # send response
    await interaction.response.send_message(embed=embed)

def run_bot():
    client.run(TOKEN)
    
# ------------------ Flask Web Server ------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port)

# ------------------ Run Both ------------------

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    run_web()


