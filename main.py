import os
import io
import discord
from discord.ext import commands
import json
import requests
import typing
from dotenv import load_dotenv
from PIL import Image

# discord bot prefix
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


# # Bot command functions overview
# 0. inputs: collection, pfp_id, outfit, variant
# 1. Get base image
# 2. Download base image to clean_pfp dir
# 3. Combine images & save to dressed_pfp dir
# 4. Send dressed_pfp image to discord

# Current Campaigns
# - Bussin
# - Solcap/Solsnap
# - Beer
# - Wallpaper
# - Banner
#
# Archive Campaigns
# - Seven

# Collections available
collections = ['ape', 'dtp', 'egg']


# Functions

def get_daa_image(pfp_id, type='no-head-traits'):
    url = f'https://degenape.nyc3.digitaloceanspaces.com/apes/{type}/{pfp_id}.png'
    save_image_file_path = f'collections/ape/clean_pfps/{type}/{pfp_id}.png'

    if os.path.isfile(save_image_file_path):
        return save_image_file_path
    else:
        download_image(url, save_image_file_path)
        return save_image_file_path

def get_hyperspace_data(collection, pfp_id):
    search_value = {
        'ape': {
            'project_id': 'degenape',
            'search_value': 'Degen Ape #',
        },
        'dtp': {
            'project_id': 'degentrashpandas',
            'search_value': 'Degen Trash Panda #',
        },
        'egg': {
            'project_id': 'degenerateapekindergarten',
            'search_value': 'Degen Egg #',
        },
    }

    payload = json.dumps({
        'condition': {
            'project_ids': [
                {
                    'project_id': search_value[collection]['project_id']
                }
            ],
            'name': {
                'operation': 'EXACT',
                'value': f'{search_value[collection]["search_value"]}{pfp_id}'
            },
        }
    })
    headers = {
        'Authorization': os.environ['HYPER_TOKEN'],
        'Content-Type': 'application/json'
    }

    return requests.post('https://beta.api.solanalysis.com/rest/get-market-place-snapshots', headers=headers, data=payload)

def get_background_color(collection, pfp_id):
    r = get_hyperspace_data(collection, pfp_id)
    background = r.json()['market_place_snapshots'][0]['attributes']['Background']

    return background

def get_collection_image(collection, pfp_id):
    r = get_hyperspace_data(collection, pfp_id)
    url = r.json()['market_place_snapshots'][0]['meta_data_img']
    save_image_file_path = f'collections/{collection}/clean_pfps/{pfp_id}.png'

    download_image(url, save_image_file_path)

    return save_image_file_path

def download_image(url, image_file_path):
    r = requests.get(url, timeout=4.0)
    if r.status_code != requests.codes.ok:
        assert False, f'Status code error: {r.status_code}.'

    with Image.open(io.BytesIO(r.content)) as im:
        im.save(image_file_path)


def combine_images(clean_image_file_path, outfit_file_path, save_file_path):
    pfp = Image.open(clean_image_file_path)
    outfit = Image.open(outfit_file_path)

    # Better blending method
    dressed = Image.new("RGBA", pfp.size)
    dressed = Image.alpha_composite(dressed, pfp)
    dressed = Image.alpha_composite(dressed, outfit)
    dressed.save(save_file_path)

    return save_file_path


def make_image(collection, pfp_id, clean_image_file_path, campaign):
    if campaign == 'wallpaper':
        resize = 780
        paste_x = 0
        paste_y = 908
    elif campaign == 'banner':
        resize = 800
        paste_x = 2000
        paste_y = 200
    save_file_path = f'collections/{collection}/dressed_pfps/{pfp_id}_{campaign}.png'
    bg_color = get_background_color(collection, pfp_id)
    bg = Image.open(f'collections/ape/outfits/{campaign}/{bg_color.lower()}.png')
    pfp = Image.open(clean_image_file_path)
    pfp = pfp.resize((resize, resize))
    new_pfp = Image.new("RGBA", bg.size)
    new_pfp.paste(pfp, (paste_x, paste_y), mask=pfp)

    wallpaper = Image.new("RGBA", bg.size)
    wallpaper = Image.alpha_composite(wallpaper, bg)
    wallpaper = Image.alpha_composite(wallpaper, new_pfp)
    wallpaper.save(save_file_path)

    return save_file_path


@bot.command(name="gib", brief='Gib me cool pfp',
             description='This command will let you be much cooler than you are... fr fr')
async def gib(ctx, collection: str, pfp_id: int, campaign: str, fit: typing.Optional[str] = 'default'):
    outfit = campaign
    collection = collection.lower()

    if campaign == 'wallpaper' or campaign == 'banner':
        try:
            if collection == 'ape':
                clean_image_file_path = get_daa_image(pfp_id, 'no-background')
                dressed_file_path = make_image(collection, pfp_id, clean_image_file_path, campaign)

                await ctx.send(file=discord.File(dressed_file_path))
            else:
                await ctx.send('Please enter a valid collection. `ape`')
        except:
            await ctx.send('Mhmmm something went wrong\n\nTry `!gib-help` for more info')
    else:
        try:
            if collection in collections:
                if collection == 'ape':
                    clean_image_file_path = get_daa_image(pfp_id)
                else:
                    clean_image_file_path = get_collection_image(collection, pfp_id)

                save_file_path = f'collections/{collection}/dressed_pfps/{pfp_id}_{outfit}_{fit}.png'
                outfit_file_path = f'collections/{collection}/outfits/{outfit}/{fit}.png'

                dressed_file_path = combine_images(clean_image_file_path, outfit_file_path, save_file_path)

                await ctx.send(file=discord.File(dressed_file_path))
            else:
                await ctx.send('Please enter a valid collection. ape / dtp / egg')
        except:
            await ctx.send('Please enter valid options for your request.\n\nTry `!gib-help` for more info')


@bot.command(name='gib-help', brief='List avaiable fits',
             description='This command will list the different outfits available to you')
async def gib_help(ctx):
    message = """**Formatting the command examples**

```md
!gib [collection] [id] [campaign] [variant]
!gib [ape/dtp/egg] [123] [solcap/solsnap/bussin/beer] [black/blue/red/white... etc]

!gib ape 123 eye
!gib ape 123 wallpaper
!gib ape 123 banner
!gib ape 123 solcap
!gib ape 123 bussin blue
!gib dtp 456 solsnap 
!gib egg 789 beer 
```

==========================

**What I Can Gib**

**Eye**
*collections:* `ape`

**Beer**
*collections:* `ape`, `dtp`,`egg`
*variants:* `clean`, `background`

**bussin**
*collections:* `ape`, `dtp`
*variants:* `black`, `blue`, `brown`, `gold`, `green`, `purple`, `red`, `white`

**solcap**
*collections:* `ape`, `dtp`

**solsnap**
*collections:* `ape`, `dtp`

**wallpaper**
*collections:* `ape`

**banner**
*collections:* `ape`
    """
    await ctx.send(message)


load_dotenv()

bot.run(os.environ['DISCORD_TOKEN'])

