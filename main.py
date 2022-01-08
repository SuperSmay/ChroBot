import discord
from pathlib import Path
import os
import json

from discord.commands import permissions

# Config 
PREFIX = '.'  # Prefix for any macros or other commands
RELOAD_ON_COMMAND = False  # Reloads the macros on every command attempt if true
MACRO_FILE_NAME = 'macros.json'  # File name to load macros from
ALLOWED_ROLE_IDS = []  # List of roles to allow using macros/commands. If empty anyone is allowed to use them
ALLOW_ALL_MODERATORS = True  # Allows anyone with manage messages (or admin) to use macros/commands. Channel specific permissions are taken into account
ALLOW_ALL_ADMINS = True  # Allows any admin to use macros/commands
ENABLE_SLASH_MACROS = True  # Registers all macros as slash commands
GUILD_IDS_FOR_SLASH = [764385563289452545]  # List of guild ids to register slash commands in

bot = discord.Bot()  #Create bot
macros_dictionary = {}  #Initialize empty dictionary
macro_file_path = Path(MACRO_FILE_NAME)  #Create path object to macro file

# Load token
token_file = Path('token')
if os.path.isfile(token_file):
    with open(token_file, 'r') as f:
        TOKEN = f.read()
else:
    print('Token file not found! Please create a file called \'token\' in the same folder as this file containing the token!')
    exit(1)

@bot.event
async def on_ready():
  print(f"Logged in {bot.user.name}{bot.user.discriminator}")
  
  async for guild in bot.fetch_guilds(limit=150):  #List connected guilds
    print(guild.name)


@bot.event
async def on_message(message: discord.Message):

    if message.author.bot:  # Ignore other bots
        return

    if message.content.startswith(PREFIX):  # Runs commands and provides permissions check

        if user_allowed(message.author, message.channel):

            if message.content.startswith(PREFIX):
                await run_macro_check(message)

            if message.content.startswith(f'{PREFIX}reload'):
                reload()
                await message.delete()
    

def user_allowed(author: discord.Member, channel: discord.TextChannel):

    valid_command_user = False

    if ALLOWED_ROLE_IDS == []:
        valid_command_user = True

    for role_id in [role.id for role in author.roles]:
        if role_id in ALLOWED_ROLE_IDS:
            valid_command_user = True

    if ALLOW_ALL_MODERATORS and (channel.permissions_for(author)).manage_messages:
        valid_command_user = True

    if ALLOW_ALL_ADMINS and (channel.permissions_for(author)).administrator:
        valid_command_user = True
    
    return valid_command_user      


async def run_macro_check(message: discord.Message):  # Checks if a message is a call to a macro, and sends the response if it is

    macro_name = message.content.removeprefix(PREFIX).lower()

    if RELOAD_ON_COMMAND:
        reload()

    if macro_name in macros_dictionary.keys():
        await message.delete()
        
        response = get_macro_response(macro_name)

        if type(response) == discord.Embed:
            await message.channel.send(embed=response)
        else:
            await message.channel.send(response)
            

def get_macro_response(macro_name):
    macro: dict = macros_dictionary[macro_name]

    title = str(macro['title']) if 'title' in macro.keys() else ''
    description = str(macro['description']) if 'description' in macro.keys() else 'None'

        
    if 'embed' in macro.keys() and macro['embed']:
        
        embed = discord.Embed(title=title, description=description)

        if 'color' in macro.keys():
            embed.color = macro['color']

        if 'image' in macro.keys():
            embed.set_image(url=macro['image'])
        
        if 'icon' in macro.keys():
            embed.set_thumbnail(url=macro['icon'])

        if 'image' in macro.keys():
            embed.set_image(url=macro['image'])
        
        return embed
    else:
        return '**' + title + '**' + '\n' + description

async def list_macros(message: discord.Message):  # Sends a message containing the names and descriptions (if provided) 
    pass


def reload_slash_commands():

    if not ENABLE_SLASH_MACROS: return

    for macro_name in macros_dictionary.keys():
        @bot.slash_command(
            name=macro_name,
            guild_ids=GUILD_IDS_FOR_SLASH,
            default_permission=True
        )
        async def command(ctx: discord.ApplicationContext):
            
            if user_allowed(ctx.author, ctx.channel):

                response = get_macro_response(ctx.command.qualified_name())

                if type(response) == discord.Embed:
                    await ctx.respond(embed=response)
                else:
                    await ctx.respond(response)
            
            else: await ctx.respond(content='You don\'t have permission to use this',ephemeral=True)


def reload(reload_slash=True):
    global macros_dictionary
    print('Reloading macros...')
    if os.path.isfile(macro_file_path):
        with open(macro_file_path, 'r') as f:
            try:
                macros_dictionary_temp = json.load(f)
            except:
                macros_dictionary_temp = {}
                print(f'Invalid json in {MACRO_FILE_NAME}!')
            
        if type(macros_dictionary_temp) == dict:
            macros_dictionary = macros_dictionary_temp.copy()
            print(f'{len(macros_dictionary.keys())} macros loaded from {MACRO_FILE_NAME}')
            if reload_slash: reload_slash_commands()

        else:
            print(f'json format incorrect! Should be dict, found {type(macros_dictionary_temp)}')

    else:
        print(f'{MACRO_FILE_NAME} file not found! No macros will be loaded.')

reload()

bot.run(token=TOKEN)