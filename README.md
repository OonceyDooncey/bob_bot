# Discord Game Bot

#### A discord game bot inspired by a game from twitch chat.

Built with:
![Built with](https://skillicons.dev/icons?i=discord,py,mongodb)

## Features

#### Coinflip:

-   Flip a coin to land on either heads or tails

#### Gamba:

-   Input an amount for a 50% chance to win 1.5x the original amount
-   User can input either an integer, a percentage of their balance or all of their balance (Example: 100, 5% or all)

#### Duel:

-   Challenge a user to a duel for x amount of money
-   Winner takes the x amount of money

## Running the bot

You will first need to create a discord application at [Discord Developer Portal — My Applications] (https://discord.com/developers/applications). Then, replace the token with your own token obtained from Discord.

Do take note that the database is built with MongoDB, so if you are planning to use a different database. You will need to adjust the functions "user_exists", "retrieve_balance" and "update_buckeronis".

```
git clone https://github.com/OonceyDooncey/bob_bot.git
python main.py
```

To use custom display name in duel, you will need to amend the name and value accordingly

```
@app_commands.choices(target=[app_commands.Choice(name="USER1", value=USER1), app_commands.Choice(name="USER2", value=USER2)])
```

If you would like to use user's original username, replace the "Duel" function as:

```
@client.tree.command(name="duel", description="Initiate duel with a user")
async def duel(interaction: discord.Interaction, target: str, amount: str):
	username = interaction.user.name
	user_displayname = interaction.user.display_name
	user_id = interaction.user.id
	members = [{"name": member.name, "id":member.id} for member in interaction.guild.members]
	names = [member.name for member in interaction.guild.members] #Maybe check if theres a better way to check for this
	balance = retrieve_balance(user_id, collection)
	amt = calculate_amt(amount, balance)
	if amt > balance:
		await interaction.response.send_message(content=f"You do not have enough buckeronis, you only have {balance} buckeronis")
		return
	if target == username:
		await interaction.response.send_message(content="You cannot challenge yourself")
		return
	if target not in names:
		await interaction.response.send_message(content="Unable to challenge a user that is not in the server")
		return
	for member in members:
		if member["name"] == target:
			target_id = member["id"]
			await interaction.response.send_message(content=f"<@{target_id}>, {user_displayname} has challenged you to a duel for {amt} buckeronis. You have 30 seconds to accept.", view=DuelButton(username, target, amt, user_id, target_id, interaction))
```
