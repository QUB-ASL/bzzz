## QUB ASL Discord bots

### How to create a new bot and get a token

[This video](https://discord.is-serious.business/6fd481.mp4) explains how to create a bot and obtain a token. 

You need to:

1. Visit https://discord.com/developers/applications/
2. Select "Create application" (top right corner)
3. Give your bot a name. Our naming convention in bzzz is that all bots have a name that starts with `BOT_`. For example `BOT_Pi_1`.
4. In the left sidebar, go to "bot" and make sure that all options under "Privileged Gateway Intents" are active

To get the token of your bot select "Reset Token". Then the token will be reset and revealed. Copy the token and paste it into the file `token.private` in this folder. Each agent (each Raspberry Pi) will have a unique token.


The next step is to invite your bot to the server

### Invite the bot

Follow these steps

1. Visit https://discord.com/developers/applications
2. Select your bot
3. Go to "OAuth2" and then "URL Generator"
4. From the list of scopes, select "bot"
5. From the list below select "Manage Roles", "Manage Channels", "Read messages/view channels", "Send messages", "Manage messages", "Embed links", "Attach files", "Read message history", "Use slash commands", "Connect" and "Speak"
6. Copy the link from below
7. Go to that link to invite the bot to your server


### How to run the client

To run the client, first you need to create a virtual environment with Python 3 (we have tested this with Python 3.9):

```
virtualenv -p python3 venv_bot
```

Then, activate the virtual environment

```
source  venv_bot/bin/activate
```

and install the following packages

```
pip install discord.py
pip install netifaces
```

Then, just run the script

```
python main.py
```

### Chatting with the bot

Firstly, you need to join our private Discord server. Ask one of the team members for an invitation.

In the list of participants you can see which agents (bots) are live. Type `.ip`* to get their IPs. To format the output using markdown, use `.ip p` (here 'p' stands for 'pretty')

> * It is not case-sensitive, so `.IP` works as well