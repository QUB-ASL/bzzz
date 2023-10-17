import discord
import json
from netifaces import interfaces, ifaddresses, AF_INET
import socket


# Create dictionary with bot's info
bot_name = socket.gethostname()
bot_info = {'name': bot_name}

# Get IPs
network_info = {}
for iface_name in interfaces():
    addresses = [i['addr'] for i in ifaddresses(
        iface_name).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
    if not (len(addresses) == 1 and addresses[0] == "No IP addr") and addresses[0] != '127.0.0.1':
        network_info[iface_name] = addresses
bot_info["net"] = network_info

# Open private token file and read Discord token
with open('token.private') as fh:
    bot_token = fh.readline().strip()


# Define class for my client
class DiscordBotClient(discord.Client):

    # What to do uplon login
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    # What to do every time a message is received
    async def on_message(self, message):
        # Ignore own messages and messages from other bots
        if message.author == client.user or message.author.name.startswith("BOT"):
            return
        # otherwise, print the message to the console
        print(f'[{message.author}]> {message.content}')
        # and respond to commands
        if message.content.strip().lower() == "ip":
            await message.channel.send(json.dumps(bot_info, indent=4))


intents = discord.Intents.default()
intents.message_content = True

client = DiscordBotClient(intents=intents)

client.run(bot_token)  # run the client
