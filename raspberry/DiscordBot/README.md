## QUB ASL Discord bots

### How to create a new bot and get a token

[This video](https://discord.is-serious.business/6fd481.mp4) explains how to create a bot and obtain a token. 

You need to:

1. Visit https://discord.com/developers/applications/
2. Select "New application" (top right corner)
3. Give your bot a name. Our naming convention in bzzz is that all bots have a name that starts with `BOT_`. For example `BOT_Pi_1`.
4. In the left sidebar, go to "bot" and make sure that all options under "Privileged Gateway Intents" are active.  Don't touch anything else.

To get the token of your bot select "Reset Token". Then the token will be reset and revealed. Copy the token and paste it into a file named `token.private` in this folder (you need to create the file). Each agent (each Raspberry Pi) will have a unique token.


The next step is to invite your bot to the server.

### Invite the bot

To invite your bollow these steps

1. Ask @alphaville, @jamie-54 or any other member for an invitation to the Discord server and accept it and ask @alphaville for admin privideges 
2. Visit https://discord.com/developers/applications
3. Select your bot
4. Go to "OAuth2" and then "URL Generator"
5. From the list of scopes, select "bot"
6. From the list below select "Manage Roles", "Manage Channels", "Read messages/view channels", "Send messages", "Manage messages", "Embed links", "Attach files", "Read message history", "Use slash commands", "Connect" and "Speak"
7. Copy the link from below
8. Follow the link to invite your bot to the server


### How to run the client

To run the client, first you need to create a virtual environment with Python 3 (we have tested this with Python 3.11.2):

```
python -m venv venv_bot
```

For older versions of Python a virtual environment can be created by (we have tested this with Python 3.9):

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


### How to run the client on Start_up

After the virtual environment and dependencies have been installed as described above, a script can be used to atuomatically run the client on start_up.

To do this, the `run_DiscordBot_on_start_up.sh` can be added to the user's crontab by:

```
crontab -e
```
Then add the following:

```
@reboot sleep 10 && ~/bzzz/raspberry/DiscordBot/run_DiscordBot_on_start_up.sh
```


### Chatting with the bot

Firstly, you need to join our private Discord server. Ask one of the team members for an invitation.

In the list of participants you can see which agents (bots) are live. Type `.ip`[^1] to get their IPs. To format the output using markdown, use `.ip p` (here 'p' stands for 'pretty')

[^1]: It is not case-sensitive, so `.IP` works as well
