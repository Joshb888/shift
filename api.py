from discord import *
from discord_slash.context import SlashContext
from discord.utils import get
import asyncpg as pg
import asyncio
import os, json
import time

class Colour():
    green = 0x42F56C
    red = 0xFF0000
    blue = 0x0000FF

async def isServerSetup(ctx:SlashContext, langPack):
    if not os.path.isfile(f"./servers/{ctx.guild.id}-cfg.json"):
        embed = Embed(title=langPack["Setup Required"], description=langPack["Please run /setup"], color=Colour.red)
        await ctx.send(embed=embed)
        return False
    else:
        return True

async def userIsAdmin(ctx:SlashContext, langPack):
    if ctx.author.guild_permissions.administrator:
        return True

    #Get serverwide admin role
    role = None
    serverCfg = json.load(open(f"./servers/{ctx.guild.id}-cfg.json"))
    try:
        role = role = get(ctx.guild.roles, id=serverCfg["admin_role"])
    except Exception as e:
        print(e)
        await ctx.send(langPack["There was an error! Error code: 0x01"], hidden=True)
        return False
    #Check if role is in author's roles
    if role in ctx.author.roles:
        return True

    return False

def loadLocaleByUserID(uid:int):
    # Check if user defined locale exists
    if os.path.isfile(f"./locale/{uid}-locale.json"):
        userLocale = json.load(open(f"./locale/{uid}-locale.json"))["locale"]
        return json.load(open(f"./locale/lang_packs/{userLocale}.json", "rb"))
    else:
        # Return default english locale
        return json.load(open("./locale/lang_packs/en.json", "rb"))

async def isUserShiftRunning(guild_id, user_id): # Returns True or False whether a shift is running
    conn = await pg.connect(user="", password="", database="", host="")
    values = await conn.fetch(
        f"SELECT * FROM shifts WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()
    if len(values) == 0:
        return False
    return True
    
async def doesUserHaveTimesheet(guild_id, user_id):
    conn = await pg.connect(user="", password="", database="", host="")
    values = await conn.fetch(
        f"SELECT * FROM stats WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()
    if len(values) == 0:
        return False
    return True

async def addShift(guild_id, user_id): # Adds a shift to the shifts table
    conn = await pg.connect(user="", password="", database="", host="")
    await conn.fetch(
        f"INSERT INTO shifts VALUES ('{str(guild_id)}', '{str(user_id)}', '{str(int(time.time()))}')"
    )
    await conn.close()

async def removeShift(guild_id, user_id): # Removes the given user's shift from the shifts table and returns the time difference in mins
    conn = await pg.connect(user="", password="", database="", host="")
    # Get time
    record = await conn.fetch(
        f"SELECT * FROM shifts WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.fetch(
        f"DELETE FROM shifts WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()
    startTime = int(float(record[0]["start_time"]))
    return (int(time.time()) - startTime) // 60

async def getTimeElapsed(guild_id, user_id):
    conn = await pg.connect(user="", password="", database="", host="")
    # Get time
    record = await conn.fetch(
        f"SELECT * FROM shifts WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()
    startTime = int(float(record[0]["start_time"]))
    return (int(time.time()) - startTime) // 60

async def alterCredit(guild_id, user_id, minutes:int): # Universal method to alter credit on a timesheet, use positive mins to add time, and negative for removing
    conn = await pg.connect(user="", password="", database="", host="")
    # Get time
    record = await conn.fetch(
        f"SELECT * FROM stats WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    currentTime = int(record[0]["minutes_logged"])
    newTime = currentTime + minutes
    # Update time
    await conn.fetch(
        f"UPDATE stats SET minutes_logged='{str(newTime)}' WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()

async def createTimesheet(guild_id, user_id):
    conn = await pg.connect(user="", password="", database="", host="")
    await conn.fetch(
        f"INSERT INTO stats VALUES ('{str(guild_id)}', '{str(user_id)}', '0')"
    )
    await conn.close()

async def getCurrentStats(guild_id, user_id):
    conn = await pg.connect(user="", password="", database="", host="")
    record = await conn.fetch(
        f"SELECT * FROM stats WHERE serverid='{str(guild_id)}' AND userid='{str(user_id)}'"
    )
    await conn.close()
    return int(record[0]["minutes_logged"])

async def deleteStatsByServer(guild_id):
    conn = await pg.connect(user="", password="", database="", host="")
    await conn.fetch(
        f"DELETE FROM stats WHERE serverid='{guild_id}'"
    )
    await conn.close()

async def deleteUserStats(guild_id, user_id):
    conn = await pg.connect(user="", password="", database="", host="")
    await conn.fetch(
        f"DELETE FROM stats WHERE serverid='{guild_id}' AND userid='{user_id}'"
    )
    await conn.close()

async def getUsersByServer(guild_id):
    conn = await pg.connect(user="", password="", database="", host="")
    records = await conn.fetch(
        f"SELECT * FROM stats WHERE serverid='{guild_id}'"
    )
    await conn.close()
    usersList = []
    for record in records:
        usersList.append(int(record["userid"]))
    return usersList

async def getNumActiveShifts():
    conn = await pg.connect(user="", password="", database="", host="")
    records = await conn.fetch(
        "SELECT * FROM shifts"
    )
    await conn.close()
    return len(records)