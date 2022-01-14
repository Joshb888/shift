from discord import *
from discord.abc import User
from discord.activity import create_activity
from discord.channel import TextChannel
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import ComponentContext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.utils import get
import os, json, datetime, time

from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

from api import *

class Leaderboard(commands.Cog, name="leaderboard"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="leaderboard",
        description="Generates a leaderboard ranking all server users"
    )
    async def _leaderboard(self, ctx:SlashContext):
        langPack = loadLocaleByUserID(ctx.author.id)
        if not await isServerSetup(ctx, langPack):
            return
        
        config = json.load(open(f"./servers/{ctx.guild.id}-cfg.json"))

        # Make Last LB file if it doesn't exist
        if not os.path.isdir(f"./leaderboard/{ctx.guild.id}"):
            os.makedirs(f"./leaderboard/{ctx.guild.id}")
            last_lb_file = open(f"./leaderboard/{ctx.guild.id}/last_lb.txt", "w")
            last_lb_file.write("0")
            last_lb_file.close()

        lastLBTime = int(open(f"./leaderboard/{ctx.guild.id}/last_lb.txt").read())

        if lastLBTime + 900 < time.time():
            await ctx.defer()
            f = open(f"./leaderboard/{ctx.guild.id}/last_lb.txt", "w") # Write current time
            f.write(str(int(time.time())))
            f.close()
            
            embed = Embed(
                title="Leaderboard", 
                description="Generating Leaderboard...", 
                color=Colour.green
            )
            embed.set_footer(text="This could take a few seconds!")
            confMsg = await ctx.send(embed=embed) # Send confirmation msg

            potential_server_users = await getUsersByServer(ctx.guild.id)
            
            usernames = [] # Fetch usernames and respective credits
            credits = []
            for id in potential_server_users:
                try:
                    temp = await ctx.author.guild.fetch_member(id)
                    usernames.append(str(temp.name + "#" + temp.discriminator))
                    credits.append(await getCurrentStats(ctx.guild.id, id))
                except:
                    await deleteUserStats(ctx.guild.id, id)
            
            unsorted_stats = list(zip(credits, usernames)) # Zip together the usernames and credits making a dict

            sorted_stats = sorted(unsorted_stats, key=lambda x: (x[0]), reverse=True) # Now sort the stats (takes time)

            try:
                os.remove(f"./leaderboard/{ctx.guild.id}/leaderboard.txt") # Try to remove the leaderboard if one exists, if not just catch error
            except :
                pass
            

            # Now write the leaderboard

            f = open(f"./leaderboard/{ctx.guild.id}/leaderboard.txt", "a")
            for a in range(len(sorted_stats)):
                f.write(f"{a + 1}. {sorted_stats[a][1]} | {sorted_stats[a][0]} minute(s)!\n")
            f.close()

            embed = Embed(
                title="Leaderboard",
                description=f"Here's the top users!\nBelow will be a complete leaderboard that you can download or view :)",
                color=Colour.green
            )

            if len(sorted_stats) == 0:
                await ctx.send("There are no users to put in the leaderboard!")
            if len(sorted_stats) == 1:
                embed.add_field(name="1st Place",
                                value=f"{sorted_stats[0][1]} has {sorted_stats[0][0]} minute(s)!", inline=True)
            if len(sorted_stats) == 2:
                embed.add_field(name="1st Place",
                                value=f"{sorted_stats[0][1]} has {sorted_stats[0][0]} minute(s)!", inline=True)
                embed.add_field(name="2nd Place",
                                value=f"{sorted_stats[1][1]} has {sorted_stats[1][0]} minute(s)!", inline=True)
            if len(sorted_stats) > 2:
                embed.add_field(name="1st Place",
                                value=f"{sorted_stats[0][1]} has {sorted_stats[0][0]} minute(s)!", inline=True)
                embed.add_field(name="2nd Place",
                                value=f"{sorted_stats[1][1]} has {sorted_stats[1][0]} minute(s)!", inline=True)
                embed.add_field(name="3rd Place",
                                value=f"{sorted_stats[2][1]} has {sorted_stats[2][0]} minute(s)!", inline=True)
            await confMsg.delete()
            await ctx.send(embed=embed)

            # Send the full leaderboard
            with open(f"./leaderboard/{ctx.guild.id}/leaderboard.txt", 'rb') as fp:
                await ctx.send(file=File(fp, 'leaderboard.txt'))

        else:
            embed = Embed(
                title="Leaderboard",
                description=f"Unfortunately, you cannot generate a fresh leaderboard for your server yet, please wait!\n\n Here is the latest leaderboard:",
                color=Colour.red
            )
            await ctx.send(embed=embed, hidden=True)
            with open(f"./leaderboard/{ctx.guild.id}/leaderboard.txt", 'rb') as fp:
                await ctx.send(file=File(fp, 'leaderboard.txt'), hidden=True)

    

def setup(client):
    client.add_cog(Leaderboard(client))