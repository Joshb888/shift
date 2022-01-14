import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
import os, json, random

from api import getNumActiveShifts

client = commands.AutoShardedBot(command_prefix="s!")
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}")
    status_task.start()

@tasks.loop(minutes=0.5)
async def status_task():
    num = random.randint(1, 2)
    print(num)
    if num == 1:
        await client.change_presence(activity=discord.Game(f"{len(client.guilds)} guilds across {client.shard_count} shards!"))
    elif num == 2:
        await client.change_presence(activity=discord.Game(f"Watching {await getNumActiveShifts()} active shifts"))

@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return
    if message.content.startswith("s!"):
        await message.channel.send("We have moved to slash commands, please use them instead!\n\nIf slash commands are not showing up in your server, please re-invite ShiftLogger with this link: https://discord.com/api/oauth2/authorize?client_id=861916907367301130&permissions=268437504&scope=applications.commands%20bot\n\n*No stats will be lost*")

if __name__ == "__main__":
    cfg = json.load(open("cfg.json"))
    client.remove_command("help")
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                client.load_extension(f"cogs.{extension}")
                print(f"Loaded module '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load module {extension}\n{exception}")
    if os.name == "nt":
        input("Running TEST version of ShiftLogger, press enter to continute!")
        client.run(cfg["testToken"])
    else:
        input("Running MAIN version of ShiftLogger, press enter to continute!")
        client.run(cfg["mainToken"])