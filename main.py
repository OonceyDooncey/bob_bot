import os
from dotenv import load_dotenv
from colorama import Fore
from pymongo import MongoClient
import discord
from discord.ext import commands
import random

#Load env file
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")


#Connect to database
cluster = MongoClient(f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0.yrl41lw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["bob_bot"]
collection = db["scores"]

#Initialise BOT
client = commands.Bot(command_prefix='$', intents=discord.Intents.all(), help_command=None)

@client.event
async def on_ready():
  print(Fore.GREEN + client.user.name + " is running")
  synced = await client.tree.sync()
  print(Fore.GREEN + str(len(synced)) + " slashed commands synced")


#Help menu
@client.tree.command(name="help", description="List of commands available for BOB_BOT")
async def help(interaction: discord.Interaction):
  embed = discord.Embed(
    color=discord.Colour.dark_teal(),
    title="Commands",
    description="List of commands available from BOB"
  )
  embed.add_field(name="Commands", value="/coinflip\n/balance\n/gamba")
  embed.add_field(name="Description", value="Flip a coin\nShows balance buckeronis\nGamble an amount for a 50% chance of winning")
  await interaction.response.send_message(embed=embed)


#Flip coin
@client.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
  result = random.choice(["Heads", "Tails"])
  await interaction.response.send_message(content=f"The coin landed on '{result}'")


#Show account balance
@client.tree.command(name="balance", description="Shows balance buckeronis")
async def balance(interaction: discord.Interaction):
  user_id = interaction.user.id
  user_in_db = user_exists(user_id)
  balance = retrieve_balance(user_id)
  if not user_in_db:
    await interaction.response.send_message(content="You have 1000 buckeronis left")
    return
  if balance == None:
    await interaction.response.send_message(content="Oh no... seems like you are broke")
    return
  await interaction.response.send_message(content=f"You have {balance} buckeronis left")


#Gamba game
@client.tree.command(name="gamba", description="Gamble coins")
async def gamba(interaction: discord.Integration, amount: int):
  result = random.choice(["win", "lose"])
  user = interaction.user.display_name
  if result == "win":
    winnings = round(amount * 1.5)
    await interaction.response.send_message(content=f"Congratulations, {user} won {winnings} buckeronis")
  else:
    await interaction.response.send_message(content=f"{user} lost {amount} buckeronis, better luck next time")
def user_exists(id):
  global collection
  results = collection.find_one({"id": id})
  if results == None:
    return False
  return True


def retrieve_balance(id):
  global collection
  result = collection.find_one({"id": id}, {"balance": 1, "_id": 0})
  if result:
    balance = result["balance"]
    return balance




client.run(TOKEN)
