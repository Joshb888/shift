from discord import Embed
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord.utils import get
import os, json

from api import *

class Help(commands.Cog, name="help"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="invite",
        description="Add shift logger to your server!"
    )
    async def _invite(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        embed = Embed(
            title=langPack["Invite Shift Logger!"],
            description=f"[{langPack['Invite Link']}](https://top.gg/bot/861916907367301130)",
            color=Colour.green
        )
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_slash(
        name="help",
        description="Command help menu for Shift Logger"
    )
    async def _help(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)

        embed = Embed(
            title=langPack["---| Help & Info |---"],
            description=f"[{langPack['Help&Support Server']}](https://discord.gg/PFGgfwvfdf) | {langPack['Made with &love& by HTT5041'].replace('&love&', '❤️')} | [{langPack['Invite Link']}](https://top.gg/bot/861916907367301130)",
            color=Colour.blue
        )
        embed.add_field(
            name="/ss",
            value=langPack["Use this command to start your shift, you can only have one shift running at a time."],
            inline=True
        )
        embed.add_field(
            name="/es",
            value=langPack["Use this command to end your shift, this can only be used when a shift is running. It will also tell you how long your shift lasted!"],
            inline=True
        )
        embed.add_field(
            name="/stats [@user]",
            value=langPack["Use this command to see how many total minutes a user has on their time sheet."]
        )
        embed.add_field(
            name="/leaderboard",
            value=langPack["This command will generate a leaderboard from the server's stats."],
            inline=True
        )
        embed.add_field(
            name="/su",
            value=langPack["This command allows you to see how long your shift has been running without ending it."]
        )
        embed.add_field(
            name="/locale",
            value=langPack["This command lets you set your language that the bot will speak to you in!"]
        )
        embed.set_footer(
            text=langPack["If you are looking for admin commands, please type /adminhelp"]
        )
        await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_slash(
        name="adminhelp",
        description="Admin command help menu for Shift Logger"
    )
    async def _adminhelp(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)

        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return
        else:
            embed = Embed(
                title=langPack["---| Admin Command Help |---"],
                description=f"[{langPack['Help&Support Server']}](https://discord.gg/PFGgfwvfdf) | {langPack['Made with &love& by HTT5041'].replace('&love&', '❤️')} | [{langPack['Invite Link']}](https://top.gg/bot/861916907367301130)",
                color=Colour.blue
            )
            embed.add_field(
                name="/reset",
                value=langPack["This command will reset the server configuration, allowing you to use /setup again"],
                inline=True
            )
            embed.add_field(
                name="/addcredit [@user] [minutes]",
                value=langPack["This command lets you add credit to a user's timesheet"],
                inline=True
            )
            embed.add_field(
                name="/removecredit [@user] [minutes]",
                value=langPack["This command, believe it or not, does the opposite to /addcredit!"],
                inline=True
            )
            embed.add_field(
                name="/wipestats",
                value=langPack["This command will wipe ALL stats in a server, this command is very destructive if used incorrectly, this action is irreversable!"],
                inline=True
            )
            embed.add_field(
                name="/forcedes [@user]",
                value=langPack["This command will end the specified user's shift."]
            )
            embed.add_field(
                name="/auditlog",
                value=langPack["When used the bot will DM you the latest audit log for your server."]
            )  
            embed.add_field(
                name="/wipeuser [@user]",
                value=langPack["When used it will reset the mentioned user's time and delete their stats."]
            )   
            await ctx.send(embed=embed, hidden=True)


def setup(client):
    client.add_cog(Help(client))