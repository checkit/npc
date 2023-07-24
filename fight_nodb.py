from nextcord.ext import commands
import random
import requests
import os
import json
from dotenv import load_dotenv
import datetime
import logging
import nextcord

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

intents = nextcord.Intents.default()
intents.typing = False
intents.presences = False
intents.emojis = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Uncomment the line below to enable cooldowns
# last_command_time = {}

def award_badge(winner_id, points):
    # Define the API endpoint
    url = "https://api.3gate.io/badges/transfer_gift"

    # Define the headers for the request
    headers = {
        "Content-Type": "application/json"
    }

    # Define the payload for the request
    payload = {
        "API_KEY": os.getenv('API_KEY'),
        "target": {"type": "discord", "value": winner_id},
        "API_TOKEN": os.getenv('API_TOKEN'),
        "badge_id": os.getenv('BADGE_ID'),
        "badge_nb": points,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    #  Print out the entire Response object
    print(response.__dict__)

    # Check if the request was successful
    if response.status_code == 200:
        response_body = response.json()
        if response_body["statusCode"] == 200:
            print(f"Successfully awarded badge to user !")
        else:
            print("Failed to award badge.")
            print(f"Status Code: {response_body['statusCode']}")
            print(f"Response: {response_body['body']['message']}")
    else:
        print("Failed to award badge.")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

@bot.slash_command(guild_ids=[int(os.getenv('TESTING_GUILD_ID'))])
async def fight(interaction: nextcord.Interaction, opponent: nextcord.User):
    """Start a fight with someone!"""
    # Check if the user is trying to fight themselves
    
    now = datetime.datetime.now()

    # Uncomment the lines below to enable cooldowns
    # if interaction.user.id in last_command_time and (now - last_command_time[interaction.user.id]).total_seconds() < 7200:
    #     await interaction.response.send_message("You're in a cooldown period. Please wait before using this command again.", ephemeral=True)
    #     return
    # last_command_time[interaction.user.id] = now

    # Determine the winner
    winner = random.choice([interaction.user, opponent])

    # Check if the initiator of the interaction is the winner
    if winner == interaction.user:
        outcomes = [
            "{user} incinerates {opponent} instantly with a hellish inferno. Nothing but ashes remains. {user} revels in the victory.",
            "{opponent} crafts a spear of ice, but {user} vaporizes it, retaliating with a whip of molten lava. The agonizing screams of {opponent} signal {user}'s triumph.",
            # Add more outcomes here...
            # Keep in mind to make the outcomes very graphic as you requested
            # You should have 25 outcomes in total
        ]
    else:
        outcomes = [
            "{opponent} incinerates {user} instantly with a hellish inferno. Nothing but ashes remains. {opponent} revels in the victory.",
            "{user} crafts a spear of ice, but {opponent} vaporizes it, retaliating with a whip of molten lava. The agonizing screams of {user} signal {opponent}'s triumph.",
            # Add more outcomes here...
            # Keep in mind to make the outcomes very graphic as you requested
            # You should have 25 outcomes in total
        ]

    outcome = random.choice(outcomes)
    outcome = outcome.format(user=interaction.user.name, opponent=opponent.name)

    # Add points to the winner
    points = random.randint(1, 35)

    # Call the function to award the badge
    award_badge(winner.id, points)

    embed = nextcord.Embed(title="Battle Outcome", description=outcome, color=nextcord.Color.from_rgb(204, 255, 0))
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    embed.set_image(url="https://media.discordapp.net/attachments/1131268787417649282/1131325436048179260/gartherly_an_anime_illustration_of_two_warriors_preparing_to_fi_aafcc47d-e79b-44ba-b864-fea89e649ed9.png?width=1620&height=908")
    embed.add_field(name="Winner", value=winner.mention, inline=True)
    embed.add_field(name="Loser", value=(opponent if winner == interaction.user else interaction.user).mention, inline=True)
    embed.set_footer(text=f"{winner.name} has won the battle against {(opponent if winner == interaction.user else interaction.user).name} and also won **{points}** fight points. | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await interaction.followup.send(embed=embed)

    logging.info(f"A fight occurred between {interaction.user.name} and {opponent.name}. Outcome: {outcome}")

bot.run(os.getenv('BOT_TOKEN'))  # replace TOKEN with your bot token
