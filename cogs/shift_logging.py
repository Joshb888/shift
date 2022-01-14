from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.utils import get
import os, json, time

from api import *

class ShiftLogging(commands.Cog, name="shift_logging"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="ss",
        description="Start your shift!"
    )
    async def _ss(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await isServerSetup(ctx, langPack):
            return
        else:
            with open(f"./servers/{ctx.guild.id}-cfg.json") as file:
                config = json.load(file)
                # Check to see if shift can be started
                if not await isUserShiftRunning(ctx.guild.id, ctx.author.id):  # Shift can be started
                    try:
                        role = get(ctx.guild.roles, id= config["shift_role"])
                        await ctx.author.add_roles(role)
                    except:
                        await ctx.send(langPack["There was an error! Error code: 0x02"], hidden=True)
                        return
                    
                    embed = Embed(
                        description=langPack["Your shift has started!"],
                        color=Colour.green
                    )
                    await addShift(ctx.guild.id, ctx.author.id)
                    await ctx.send(embed=embed, hidden=True)

                    #Now send a message to the logs channel
                    logs_ch = self.client.get_channel(config["logs_channel"])
                    embed = Embed(
                        description=f"{ctx.author.mention}'s shift has started",
                        #description=f"{ctx.author.mention}'s shift has started",
                        color=Colour.blue
                    )
                    await logs_ch.send(embed=embed)

                else:  # Shift cannot be started
                    await ctx.send(langPack["You cannot start a shift because you already have one running!"], hidden=True)

    @cog_ext.cog_slash(
        name="es",
        description="End your shift!"
    )
    async def _es(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        
        if not await isServerSetup(ctx, langPack):
            return

        with open(f"./servers/{ctx.guild.id}-cfg.json") as file:
            config = json.load(file)
            if await isUserShiftRunning(ctx.guild.id, ctx.author.id):  # Check to see if shift exists
                time_elapsed = await removeShift(ctx.guild.id, ctx.author.id)
                
                try:
                    role = get(ctx.guild.roles, id= config["shift_role"])
                    await ctx.author.remove_roles(role)
                except:
                    await ctx.send(langPack["There was an error! Error code: 0x02"], hidden=True)
                    return
                
                # update stats
                if not await doesUserHaveTimesheet(ctx.guild.id, ctx.author.id):
                    # stats entry does not exist
                    await createTimesheet(ctx.guild.id, ctx.author.id)
                
                # Add time
                await alterCredit(ctx.guild.id, ctx.author.id, time_elapsed)

                current_stats = await getCurrentStats(ctx.guild.id, ctx.author.id)

                # send messages
                embed = Embed(
                    description=langPack["Your shift has ended, it lasted &time& minutes!"].replace("&time&", str(time_elapsed)),
                    color=Colour.green
                )
                if int(time_elapsed / 60) == 999:
                    embed.set_footer(text="999 #lljw")

                log_embed = Embed(
                    description=f"{ctx.author.mention}'s shift has ended, it lasted {str(time_elapsed)} minutes!\nThey have {str(current_stats)} minutes of shift credit.",
                    color=Colour.blue
                )
                if int(time_elapsed / 60) == 999 or int(current_stats) == 999:
                    log_embed.set_footer(text="999 #lljw")

                logging_channel = self.client.get_channel(config["logs_channel"])
                await ctx.send(embed=embed, hidden=True)
                await logging_channel.send(embed=log_embed)
            else:  # doesnt exist
                await ctx.send(langPack["You cannot end your shift because you don't have one running!"], hidden=True)


    @cog_ext.cog_slash(
        name="su",
        description="Get a shift update on yourself or a given user",
        options=[
            create_option(
                name="user",
                description="User to get update on",
                option_type=6,
                required=False
            )
        ]
    )
    async def _su(self, ctx:SlashContext, user:User = None):
        if user:
            target = user
        else:
            target = ctx.author

        langPack = loadLocaleByUserID(ctx.author.id)

        if not await isServerSetup(ctx, langPack):
            return
        
        with open(f"./servers/{ctx.guild.id}-cfg.json") as file:
            config = json.load(file)
            if await isUserShiftRunning(ctx.guild.id, target.id):  # Check to see if shift exists
                # exists
                time_elapsed = await getTimeElapsed(ctx.guild.id, target.id)
                embed = Embed(
                    description=langPack["&user&'s shift has been running for &time& minutes!"].replace("&user&", target.mention).replace("&time&", str(time_elapsed)),
                    #description=f"{target.mention}'s shift has been running for {int(time_elapsed / 60)} minutes!",
                    color=Colour.green
                )
                if int(time_elapsed / 60) == 999:
                    embed.set_footer(text="999 #lljw")

                await ctx.send(embed=embed, hidden=True)
            else:  # doesnt exist
                embed = Embed(
                    description=langPack["&user& doesn't have a shift running, so you can't get an update!"].replace("&user&", target.mention),
                    color=Colour.red
                )
                await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_slash(
        name="stats",
        description="Get a your's or a user's stats",
        options=[
            create_option(
                name="user",
                description="User's stats to fetch",
                option_type=6,
                required=False
            )
        ]
    )
    async def _stats(self, ctx:SlashContext, user:User = None):
        if user:
            target = user
        else:
            target = ctx.author

        langPack = loadLocaleByUserID(ctx.author.id)

        if not await isServerSetup(ctx, langPack):
            return

        with open(f"./servers/{ctx.guild.id}-cfg.json") as file:
            config = json.load(file)
            userID = target.id
            if await doesUserHaveTimesheet(ctx.guild.id, target.id):
                stats = await getCurrentStats(ctx.guild.id, target.id)
                embed = Embed(
                    description=langPack["The user &user& has &time& minutes logged! (&time_hrs& hours)"].replace("&user&", target.mention).replace("&time&", str(stats)).replace("&time_hrs&", str(round((stats / 60), 1))),
                    color=Colour.green
                )
                if int(stats) == 999:
                    embed.set_footer(text="999 #lljw")
                await ctx.send(embed=embed, hidden=True)
            else:
                embed = Embed(
                    description=langPack["The user &user& has never finished a shift!"].replace("&user&", target.mention),
                    color=Colour.red
                )
                await ctx.send(embed=embed, hidden=True)

def setup(client):
    try:
        client.add_cog(ShiftLogging(client))
    except Exception as e:
        print(e.with_traceback())