import discord
from discord import app_commands
import asyncio
import time
import requests
from datetime import datetime,timezone

def seconds_from_utc(date_str: str) -> int:
    # Parse the input date
    parsed_date = datetime.strptime(date_str, "%d %b, %Y")

    # Set time to 12:01 AM (00:01)
    target_time = parsed_date.replace(hour=0, minute=1, second=0, microsecond=0)

    # Make it UTC aware
    target_time = target_time.replace(tzinfo=timezone.utc)

    # Current UTC time
    now = datetime.now(timezone.utc)

    # Difference in seconds
    diff_seconds = (target_time - now).total_seconds()

    return int(diff_seconds)

TOKEN = "MTQ3OTgzMDI5MzA5MDI3NTM5OA.GBU8vM.iWKPc3XN6aSVdTBDrvhti0M8rfvtgJ1KD1Hp04"

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
            f"**Releasing: <t:{end_time}:R>**"
        ),
        color=discord.Color.gold()
    )
    
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/hyGUpE441sdRq43OcsqHXnTUi3I0oUXnt10rOB2maSg/https/cdn.discordapp.com/emojis/1073161249006821406.webp?format=webp&width=160&height=160")
    embed.set_footer(text="Timer by ZeroHour",icon_url="https://cdn.discordapp.com/avatars/1479830293090275398/71bb799a0d189fba798d14c0ba7b3671")
    embed.add_field(name="About", value=description, inline=False)
    embed.set_image(url=banner)

    # send response
    await interaction.response.send_message(embed=embed)

    # fetch the sent message
    message = await interaction.original_response()

    # wait for timer
    await asyncio.sleep(seconds)

    finished_embed = discord.Embed(
        title=name,
        url="https://store.steampowered.com/app/"+appid,
        color=discord.Color.gold()
    )
    
    finished_embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/hyGUpE441sdRq43OcsqHXnTUi3I0oUXnt10rOB2maSg/https/cdn.discordapp.com/emojis/1073161249006821406.webp?format=webp&width=160&height=160")
    finished_embed.add_field(name="About", value=description, inline=False)
    finished_embed.set_image(url=banner)

    # edit the message
    await message.edit(embed=finished_embed)

client.run(TOKEN)
