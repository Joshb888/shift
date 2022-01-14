from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord.utils import get
import os, json

from discord_slash.utils.manage_commands import create_option, create_choice

from api import *

class Locale(commands.Cog, name="locale"):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="locale",
        description="Set the language the bot speaks to you in!",
        options=[
            create_option(
                name="lang",
                description="Choose your language",
                required=True,
                option_type=3,
                choices=[
                    create_choice(
                        name="English",
                        value="en"
                    ),
                    create_choice(
                        name="Español",
                        value="es"
                    )
                ]
            )
        ]
    )
    async def _locale(self, ctx:SlashContext, lang:str):
        localeJson = {"locale": lang}
        writeFile = open(f"./locale/{ctx.author.id}-locale.json", "w")
        json.dump(localeJson, writeFile)
        writeFile.close()
        langPack = loadLocaleByUserID(ctx.author.id)
        await ctx.send(langPack["Your language has been set!"], hidden=True)

def setup(client):
    client.add_cog(Locale(client))