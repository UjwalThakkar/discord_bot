import discord
from discord.ext import commands
from discord import app_commands
import random
import requests
import pymongo
import datetime
import db_functions

# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["Toxicity_detector"]
# server_collection = db['servers']
# MAX_RECENT_TOXIC = 3

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True 

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)

response = [
    "Hey, it seems like your message could be perceived as toxic. Let's maintain a respectful and positive atmosphere here. Please be mindful of your language and interactions",
    "Hello! Your message appears to contain language that may be considered toxic. Remember, we value kindness and respect in our community. Let's keep the conversation constructive and supportive",
    "Hi there! Just a friendly reminder to keep the conversation positive and respectful. Your message might come across as toxic, so let's strive to communicate in a way that uplifts others and fosters a welcoming environment"
]

@bot.tree.command(name="report", description="Report a user messgae for toxicity that is not automatically detected by the bot")
@app_commands.describe(flags = "Flags for report (e.g. : Toxic, Severely_toxic, Insult, Threat, Identity_hate, Obscene)")
async def report(interaction: discord.Interaction, message_id: str, flags: str):
    try:
        toxic_classes = [flag.strip() for flag in flags.split(",")]
        print("flags are :",toxic_classes)
        reported_message = await interaction.channel.fetch_message(int(message_id))
        reported_content = reported_message.content
        message_author = reported_message.author
        author_id = message_author.id
        
        userDoc = db_functions.handle_user(author_id, message_author, reported_content, toxic_classes)
        print(userDoc)
        
        report_doc = db_functions.handle_report(message_id, reported_content, toxic_classes)
        
        response = f"Message has been reported"
        await interaction.response.send_message(response, ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("Message not found. please provide a valid message ID.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Failed to retrieve the message. Try again later.")
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to edit this message.")


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Listening for messages...')



def isToxic(content):
    data = {"text": content}
    response = requests.post("http://127.0.0.1:5000/predict", json=data)
    if response.status_code == 200:
        result = response.json()['0']
        print(result)
        toxic_classes = [key for key, value in result.items() if value > 0.55]
        print('toxic_Classes: ',toxic_classes)
        return toxic_classes
    else:
        return "error"



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    reply = random.choice(response)
    
    toxic_classes = isToxic(message.content)
    if toxic_classes:
        await message.channel.send(f"{message.author.mention}, you message has been deleted")
        await message.delete()
        user_doc =  db_functions.handle_user(message.author.id, message.author, message.content, toxic_classes)
        print(user_doc)

    elif toxic_classes == "error":
        await message.channel.send("Error processing the message.")

    else:
        return



# Replace with your actual bot token
bot.run('your_bot_token')
