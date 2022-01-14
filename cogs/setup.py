from discord.channel import TextChannel
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.utils import get
import os, json, datetime

from api import *

class Setup(commands.Cog, name="setup"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="setup",
        description="Sets up Shift Logger for use",
        options=[
            create_option(
                name= "logs_channel",
                description= "Channel that SL will send shift logs to",
                option_type= 7,
                required= True
            )
        ]
    )
    async def _setup(self, ctx:SlashContext, logs_channel:TextChannel = None):
        langPack = loadLocaleByUserID(ctx.author.id)
        if ctx.author.guild_permissions.administrator:
            if not os.path.isfile(f"./servers/{ctx.guild.id}-cfg.json"):
                shiftRole = await ctx.guild.create_role(name="On Shift Role")
                adminRole = await ctx.guild.create_role(name="Shift Admin Role")
                config = {"logs_channel": int(logs_channel.id), "shift_role": int(shiftRole.id), "admin_role": int(adminRole.id)}
                jsonConfig = json.dumps(config, indent=4)
                config_file = open(f"./servers/{ctx.guild.id}-cfg.json", "w")
                config_file.write(jsonConfig)
                config_file.close()
                if not os.path.isfile(f"./servers/{ctx.guild.id}-audit.txt"):
                    audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "w")
                    audit_log.write(
                        f"{str(datetime.datetime.now())} | -- Begin Audit Log of server {ctx.guild.name} (ID:{ctx.guild.id}) --\n")
                    audit_log.close()
                else:
                    audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
                    audit_log.write(
                    f"{str(datetime.datetime.now())} | -- Server Re-setup! {ctx.guild.name} (ID:{ctx.guild.id}) --\n")
                    audit_log.close()
                embed = Embed(
                    title=langPack["Setup Succcessful!"],
                    description=langPack["Hey, you have successfully set up your server! You can use /help and /adminhelp to view all of the commands we offer. Also please join our [**Help&Support Server**](https://discord.gg/PFGgfwvfdf) so you can get any help you might need! Thanks :)\n\nAlso, I have created 2 new roles: &role1& and &role2&, &role1& will be automatically given to a user when they start a shift. &role2& is what you should give to users that you trust with the admin commands!"].replace("&role1&", str(shiftRole.mention)).replace("&role2&", str(adminRole.mention)),
                    color=Colour.green
                )
                await ctx.send(embed=embed, hidden=True)
            else:
                await ctx.send(langPack["This server is already setup! If you are trying to change the setup please reset the server first with /reset."], hidden=True)
        else:
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)

    @cog_ext.cog_slash(
        name="reset",
        description="Resets Shift Logger",
    )
    async def _reset(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
        else:
            if os.path.isfile(f"./servers/{ctx.guild.id}-cfg.json"):
                os.remove(f"./servers/{ctx.guild.id}-cfg.json")
                audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
                audit_log.write(
                    f"{str(datetime.datetime.now())} | -- Server reset triggered by user {ctx.author} (ID: {ctx.author.id}) --\n")
                audit_log.close()
                embed = Embed(
                    title = langPack["Reset Successful"],
                    description= langPack["You have reset your server's config, no user stats were wiped."],
                    color=Colour.green
                )
                await ctx.send(embed=embed, hidden=True)
            else:
                await ctx.send(langPack["Error, your server is not setup"], hidden=True)

def setup(client):
    client.add_cog(Setup(client))