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
client = commands.Bot(command_prefix='$', intents=discord.Intents.all())

@client.event
async def on_ready():
  global members
  print(f"{client.user.name} is running")
  synced = await client.tree.sync()
  print(f"{str(len(synced))} slashed commands synced")


#Help menu
@client.tree.command(name="help", description="List of commands available for BOB_BOT")
async def help(interaction: discord.Interaction):
  await interaction.response.send_message(content=f"/coinflip to flip a coin\n/gamba (amount) to gamble for a 50% chance of winning")


#Flip coin
@client.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
  result = random.choice(["Heads", "Tails"])
  await interaction.response.send_message(content=f"The coin landed on '{result}'")


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


client.run(TOKEN)
