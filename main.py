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
  embed.add_field(name="Commands", value="/coinflip\n/balance\n/gamba\n/duel")
  embed.add_field(name="Description", value="Flip a coin\nShows balance buckeronis\nGamble an amount for a 50% chance of winning\nChallenge a target for buckeronis")
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
    await interaction.response.send_message(content="You have 10000 buckeronis left")
    return
  if balance == None:
    await interaction.response.send_message(content="Oh no... seems like you are broke")
    return
  await interaction.response.send_message(content=f"You have {balance} buckeronis left")


#Gamba game
@client.tree.command(name="gamba", description="Gamble coins")
async def gamba(interaction: discord.Integration, amount: int):
  username = interaction.user.display_name
  user_id = interaction.user.id
  balance = retrieve_balance(user_id)

  if amount < 0:
    await interaction.response.send_message(content="Invalid amount")
    return
  if balance < amount:
    await interaction.response.send_message(content=f"You do not have enough buckeronis, you only have {balance} buckeronis")
    return
  result = random.choice(["win", "lose"])
  if result == "win":
    winnings = round(amount * 1.5)
    new_balance = balance + winnings
    await interaction.response.send_message(content=f"Congratulations, {username} won {winnings} buckeronis")
  else:
    new_balance = balance - amount
    await interaction.response.send_message(content=f"{username} lost {amount} buckeronis, better luck next time")

  if user_exists(user_id):
    update_buckeronis(user_id, username, new_balance, True)
  else:
    update_buckeronis(user_id, username, new_balance, False)


#Duel game
class DuelButton(discord.ui.View):
  def __init__(self, user, target, amount, user_id, target_id, interaction):
    super().__init__(timeout=30)
    self.user: str = user
    self.target: str = target
    self.amount: int = amount
    self.user_id: str = user_id
    self.target_id: str = target_id
    self.interaction = interaction

  # Until you find a better fix for to check if the interaction has been done
  # async def on_timeout(self):
  #   await self.interaction.followup.send(content="The duel interaction has expired")

  @discord.ui.button(label="Accept")
  async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
    target_balance = retrieve_balance(self.target_id)
    if interaction.user.display_name == self.user:
      await interaction.response.send_message(content="You cannot accept your own challenge")
    elif interaction.user.display_name != self.target:
      await interaction.response.send_message(content="You are not the duel target")
    elif target_balance < self.amount:
      await interaction.response.send_message(content=f"<@{self.target_id}>, you do not have enough buckeronis to accept the duel. You only have {target_balance} buckeronis.")
      return
    else:
      button.disabled = True 
      button.label = "Accepted"
      await interaction.response.edit_message(view=self)
      winner = random.choice([self.user, self.target])
      if winner == self.user:
        winner_id = self.user_id
        loser = self.target
        loser_id = self.target_id
      else:
        winner_id = self.target_id
        loser = self.user
        loser_id = self.user_id
      winner_balance = retrieve_balance(winner_id)
      winner_balance += self.amount
      if user_exists(winner_id):
        update_buckeronis(winner_id, winner, winner_balance, True)
      else:
        update_buckeronis(winner_id, winner, winner_balance, False)
      loser_balance = retrieve_balance(loser_id)
      loser_balance -= self.amount
      if user_exists(loser_id):
        update_buckeronis(loser_id, loser, loser_balance, True)
      else:
        update_buckeronis(loser_id, loser, loser_balance, False)
      await interaction.followup.send(content=f"Duel winner: <@{winner_id}>, you have won {self.amount} buckeronis")


@client.tree.command(name="duel", description="Initiate duel with a user")
async def duel(interaction: discord.Interaction, target: str, amount: int):
  user = interaction.user.display_name
  user_id = interaction.user.id
  members = [{"name": member.display_name, "id":member.id} for member in interaction.guild.members]
  names = [member.display_name for member in interaction.guild.members] #Maybe check if theres a better way to check for this
  balance = retrieve_balance(user_id)
  if amount > balance:
    await interaction.response.send_message(content=f"You do not have enough buckeronis, you only have {balance} buckeronis")
    return
  if target == user:
    await interaction.response.send_message(content="You cannot challenge yourself")
    return
  if target not in names:
      await interaction.response.send_message(content="Unable to challenge a user that is not in the server")
      return
  for member in members:
    if member["name"] == target:
      target_id = member["id"]
      await interaction.response.send_message(content=f"<@{target_id}>, {user} has challenged you to a duel for {amount} buckeronis. You have 30 seconds to accept.", view=DuelButton(user, target, amount, user_id, target_id, interaction))
  

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
  else:
    balance = 10000
  return balance


def update_buckeronis(id: str, username: str, amount: int,  exist: bool):
  global collection
  if exist:
    collection.update_one({"id": id}, {"$set": {"balance": amount}})
    return
  collection.insert_one({"id": id, "username": username, "balance": amount})


client.run(TOKEN)
