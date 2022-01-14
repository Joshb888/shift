from discord.abc import User
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.utils import get
import json, datetime

from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

from api import *

buttons = [
            manage_components.create_button(
                style=ButtonStyle.red,
                label="Wipe ALL Server Stats!"
            ),
          ]
action_row = manage_components.create_actionrow(*buttons)


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="addcredit",
        description="Add time to a given user's timesheet",
        options=[
            create_option(
                name="user",
                description="The target user to add time to",
                option_type=6,
                required=True
            ),
            create_option(
                name="time",
                description="Time in minutes",
                option_type=4,
                required=True
            )
        ]
    )
    async def _addcredit(self, ctx:SlashContext, user:User, time:int):
        langPack = loadLocaleByUserID(ctx.author.id)
    
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return

        if time <= 0:
            await ctx.send(langPack["Time must be a positive value!"], hidden=True)
            return

        try:
            if await doesUserHaveTimesheet(ctx.guild.id, user.id):
                await alterCredit(ctx.guild.id, user.id, time)
            else:
                raise Exception("No timesheet")

            #Send success status
            embed = Embed(
                title=langPack["Success!"],
                description=langPack["Successfully added &time& minutes to user &user&!"].replace("&time&", str(time)).replace("&user&", user.mention),
                #description=f"Successfully added {time} minutes to user {user.mention}!",
                color=Colour.green
            )
            await ctx.send(embed=embed, hidden=True)

            audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
            audit_log.write(
                f"{str(datetime.datetime.now())} | User: {ctx.author} (ID: {ctx.author.id}) added {str(time)} minute(s) credit to {user} (ID: {user.id})\n")
            audit_log.close()

        except Exception as e:
            await ctx.send(langPack["Error. The user you are trying to add credit to likely doesn't have a timesheet!"], hidden=True)

    @cog_ext.cog_slash(
        name="removecredit",
        description="Remove time from a given user's timesheet",
        options=[
            create_option(
                name="user",
                description="The target user to remove time from.",
                option_type=6,
                required=True
            ),
            create_option(
                name="time",
                description="Time in minutes",
                option_type=4,
                required=True
            )
        ]
    )
    async def _removecredit(self, ctx:SlashContext, user:User, time:int):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return

        if time <= 0:
            await ctx.send(langPack["Time must be a positive value!"], hidden=True)
            return

        try:
            if await doesUserHaveTimesheet(ctx.guild.id, user.id):
                await alterCredit(ctx.guild.id, user.id, -time)
            else:
                raise Exception("No timesheet")

            #Send success status
            embed = Embed(
                title=langPack["Success!"],
                description=langPack["Successfully removed &time& minutes from user &user&!"].replace("&time&", str(time)).replace("&user&", user.mention),
                #description=f"Successfully removed {time} minutes from user {user.mention}!",
                color=Colour.green
            )
            await ctx.send(embed=embed, hidden=True)

            audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
            audit_log.write(
                f"{str(datetime.datetime.now())} | User: {ctx.author} (ID: {ctx.author.id}) removed {str(time)} minute(s) credit from {user} (ID: {user.id})\n")
            audit_log.close()

        except:
            await ctx.send(langPack["Error. The user you are trying to remove credit from likely doesn't have a timesheet!"], hidden=True)

    @cog_ext.cog_slash(
        name="wipestats",
        description="Wipe ALL user stats from your server",
    )
    async def _wipestats(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return

        await ctx.send(langPack["Are you sure you want to wipe ALL server stats?"], components=[action_row], hidden=True)

        button_ctx: ComponentContext = await manage_components.wait_for_component(self.client, components=action_row)
        
        await deleteStatsByServer(ctx.guild.id)
        
        await button_ctx.edit_origin(content=langPack["Success!"])
        audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
        audit_log.write(
            f"{str(datetime.datetime.now())} | User: {ctx.author} (ID: {ctx.author.id}) wiped all stats from the server!\n")
        audit_log.close()

    @cog_ext.cog_slash(
        name="forcedes",
        description="Forcably end a given user's shift",
        options=[
            create_option(
                name="user",
                description="User who's shift to end",
                option_type=6,
                required=True
            )
        ]
    )
    async def _forcedes(self, ctx:SlashContext, user:User):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return
  
        with open(f"./servers/{ctx.guild.id}-cfg.json") as file:
            config = json.load(file)
        if await doesUserHaveTimesheet(ctx.guild.id, user.id):
            elapsed_time = await removeShift(ctx.guild.id, user.id)
            # update stats
            if not await doesUserHaveTimesheet(ctx.guild.id, user.id):
                await createTimesheet(ctx.guild.id, user.id)
            
            await alterCredit(ctx.guild.id, user.id, elapsed_time)
            current_stats = await getCurrentStats(ctx.guild.id, user.id)
            # send messages
            embed = Embed(
                description=f"{user.mention}, your shift has been ended by {ctx.author.mention}, it lasted {elapsed_time} minutes!",
                color=Colour.blue
            )
            log_embed = Embed(
                description=f"{user.mention}'s shift has ended, it lasted {elapsed_time} minutes!\nThey have {current_stats} minutes of shift credit.",
                color=Colour.blue
            )
            logging_channel = self.client.get_channel(config["logs_channel"])
            try:
                role = get(ctx.guild.roles, id= config["shift_role"])
                await ctx.author.remove_roles(role)
            except:
                await ctx.send(langPack["There was an error! Error code: 0x02"], hidden=True)
                return
            await logging_channel.send(embed=embed)
            await logging_channel.send(embed=log_embed)
            await ctx.send(langPack["Success!"], hidden=True)
        else:
            embed = Embed(
                title=langPack["Error!"], 
                description=langPack["The user specified does not have an active shift!"],
                color=Colour.red
            )
            await ctx.send(embed=embed, hidden=True)


    @cog_ext.cog_slash(
        name="wipeuser",
        description="Wipe a user's stats",
        options=[
            create_option(
                name="user",
                description="User to wipe",
                option_type=6,
                required=True
            )
        ]
    )
    async def _wipeuser(self, ctx:SlashContext, user:User):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return

        if await doesUserHaveTimesheet(ctx.guild.id, user.id):  # Check to see if stats exists
            await deleteUserStats(ctx.guild.id, user.id)
            embed = Embed(
                title=langPack["Success!"],
                description=langPack["Successfully wiped &user&'s stats."].replace("&user&", user.mention),
                #description=f"Successfully wiped {user.mention}'s stats.",
                color=Colour.green
            )
            await ctx.send(embed=embed, hidden=True)
            audit_log = open(f"./servers/{ctx.guild.id}-audit.txt", "a")
            audit_log.write(
                f"{str(datetime.datetime.now())} | User: {ctx.author} (ID: {ctx.author.id}) wiped the stats of {user} (ID: {user.id})!\n")
            audit_log.close()
        else:
            await ctx.send(langPack["Error. The specified user doesn't have a timesheet!"], hidden=True)

    @cog_ext.cog_slash(
        name="auditlog",
        description="Fetch the server auditlog"
    )
    async def _auditlog(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await userIsAdmin(ctx, langPack):
            await ctx.send(langPack["You are not authorised to run this command!"], hidden=True)
            return

        if not await isServerSetup(ctx, langPack):
            return

        with open(f"./servers/{ctx.guild.id}-audit.txt", 'rb') as fp:
            await ctx.send(file=File(fp, f'{ctx.guild.id}-audit.txt'), hidden=True)

def setup(client):
    client.add_cog(Moderation(client))