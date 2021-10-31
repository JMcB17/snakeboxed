# snakeboxed
The public bot for learning Python together on Discord.

<p align="center">
    <img width="256" height="256" alt="Snakeboxed logo, the Python Discord logo hovering out of a clipart cardboard box." src="https://github.com/JMcB17/snakeboxed/blob/main/assets/logo-1024.png">
</p>

## Features
- Run code and get the results all in Discord
    - Results as embedded Discord text file
    - Accepts python files as input
- Links to Python resources
- Written in Python and released as free software, so you can learn from the source code

Work-in-progress features:
- Search the documentation for Python and Python libraries in Discord
- Accept message references as eval input

## Use Snakeboxed

The default command prefix is `?`.    
To start, try `?help`. It has all the up-to-date information about using the bot.    
The most important command is `?eval`.

`?eval` example:
```
?eval
print('hello world')
```

## Get Snakeboxed

### Add the public instance of the bot
https://discord.com/oauth2/authorize?client_id=900808633472933978&scope=bot&permissions=44096

### Self-host
Requires a snekbox server to self-host. Snekbox uses docker.

1. Run the snekbox server: `docker run --ipc=none --privileged -p 8060:8060 ghcr.io/python-discord/snekbox`
2. Clone the bot code: `git clone https://github.com/JMcB17/snakeboxed` `cd snakeboxed`
3. Dependencies    
3.1. (Optional) Create a separate install environment for the bot's dependencies, to keep things tidy: https://docs.python.org/3/tutorial/venv.html    
3.2. Install the bot's dependencies: `python3 -m pip install -r requirements.txt` 
4. Create a configuration file from the template: `cp config.template.toml config.toml`
5. Create a new Discord bot account and get its login token: https://discordpy.readthedocs.io/en/stable/discord.html
6. Fill in the login token in config.toml
7. You're good to go! Run the bot with `python3 bot.py`.

## Credits
As with any programming, most of the work was done for me.

Snekbox:    
https://github.com/python-discord/snekbox    
Code taken from python-discord/bot under the [Expat License/MIT License](https://github.com/JMcB17/snakeboxed/blob/main/LICENSE-THIRD-PARTY):    
https://github.com/python-discord/bot    
https://github.com/python-discord/bot/blob/main/bot/exts/utils/snekbox.py

Someone made a bot something like this already, but I like developing my own stuff, and mine strips out the structure of the python-discord bot more, and has simple self-hosting as well as a public instance you can use.    
https://github.com/HassanAbouelela/evalbot
