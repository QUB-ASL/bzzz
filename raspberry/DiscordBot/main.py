import discord
import json
import socket
import re
from netifaces import interfaces, ifaddresses, AF_INET

# Create Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


def create_bot_info(format=False):
    """
    Create a string with network information

    :param format: whether to MD-format the string
    """
    # Create dictionary with bot's info
    bot_name = socket.gethostname()
    bot_info = {'name': bot_name}

    # Get IPs
    network_info = {}
    for iface_name in interfaces():
        addresses = [i['addr'] for i in ifaddresses(
            iface_name).setdefault(AF_INET, [{'addr': 'No IP addr'}])]
        if not (len(addresses) == 1 and addresses[0] == "No IP addr") \
                and addresses[0] != '127.0.0.1':
            network_info[iface_name] = addresses
    bot_info["net"] = network_info
    bot_info_str_pretty = json.dumps(bot_info, indent=4)
    if format:
        bot_info_str_pretty = "```json\n" + bot_info_str_pretty + "\n```"
    return bot_info_str_pretty


@client.event
async def on_ready():
    """
    What to do once the bot connects
    """
    print(f'Logged on as {client.user}!')


@client.event
async def on_message(message):
    """
      What to do every time a message is received

      :param message: message from Discord server
    """
    # Ignore own messages and messages from other bots
    if message.author == client.user or message.author.name.startswith("BOT"):
        return

    # otherwise, print the message to the console
    print(f'[{message.author}]> {message.content}')

    is_mention = '<@' in message.content
    if is_mention and client.user.mention not in message.content:
        return  # this is not a message for me

    # and respond to commands
    clean_message_content = re.sub('<@[0-9]+>', '', message.content)
    message_tokens = clean_message_content.split()
    message_cmd = message_tokens[0].strip().lower()

    if not message_cmd.startswith('.'):
        return  # not a command

    # Command: .ip
    if message_cmd == ".ip":
        format = len(message_tokens) >= 2 and 'p' in message_tokens[1]
        await message.channel.send(create_bot_info(format))


def run_bot():
    """
    Run the bot  
    """
    # Open private token file and read Discord token
    with open('token.private') as fh:
        bot_token = fh.readline().strip()
    client.run(bot_token)  # run the client


run_bot()  # run the bot
