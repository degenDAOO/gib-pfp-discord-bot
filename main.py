from genericpath import isfile
import os
import io
import discord
from discord.ext import commands
import json
from pprint import pprint
import requests
import typing
from dotenv import load_dotenv
import PIL
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
# - Cap
# - Beer
#
# Archive Campaigns
# - Seven

# Collections available
collections = ['ape', 'dtp', 'egg']

# Functions

def get_daa_image(pfp_id, type='no-head-traits'):
  url = ('https://degenape.nyc3.digitaloceanspaces.com/apes/'+ type +'/' + str(pfp_id) + '.png')
  save_image_file_path = ('collections/ape/clean_pfps/' + str(pfp_id) + '.png') 

  if os.path.isfile(save_image_file_path):
    pprint('no double call needed')
    return save_image_file_path
  else:
    pprint('grabed the new img')
    download_image(url, save_image_file_path)
    return save_image_file_path

def get_background_color(collection, pfp_id):
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
                'value': search_value[collection]['search_value'] + str(pfp_id)
                },
        }
    })
  headers = {
      'Authorization': os.environ['HYPER_TOKEN'],
      'Content-Type': 'application/json'
  }
  r = requests.post('https://beta.api.solanalysis.com/rest/get-market-place-snapshots', headers=headers, data=payload)
  
  background = r.json()['market_place_snapshots'][0]['attributes']['Background']

  return background

def get_collection_image(collection, pfp_id):
  search_value = {
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
                'value': search_value[collection]['search_value'] + str(pfp_id)
                },
        }
    })
  headers = {
      'Authorization': os.environ['HYPER_TOKEN'],
      'Content-Type': 'application/json'
  }
  r = requests.post('https://beta.api.solanalysis.com/rest/get-market-place-snapshots', headers=headers, data=payload)
  
  url = r.json()['market_place_snapshots'][0]['meta_data_img']

  save_image_file_path = ('collections/' + collection + '/clean_pfps/' + str(pfp_id) + '.png')

  download_image(url, save_image_file_path)

def make_wallpaper(collection, pfp_id, img_path):
  save_file_path = ('collections/' + collection + '/dressed_pfps/' + str(pfp_id) + '_wallpaper.png')
  pfp = Image.open(img_path)
  bg_color = get_background_color(collection, pfp_id)
  bg = Image.open('collections/ape/wallpaper/'+bg_color+'.png')
  new_pfp = pfp.resize((390,390))
  bg.paste(new_pfp, (0, 454), mask=new_pfp)
  bg.save(save_file_path)

  return save_file_path

def download_image(url, image_file_path):
  r = requests.get(url, timeout=4.0)
  if r.status_code != requests.codes.ok:
      assert False, 'Status code error: {}.'.format(r.status_code)

  with Image.open(io.BytesIO(r.content)) as im:
      im.save(image_file_path)

def combine_images(collection, outfit, fit, pfp_id):
  save_file_path = ('collections/' + collection + '/dressed_pfps/' + str(pfp_id) + '_' + outfit + '_' + fit + '.png')

  pfp = Image.open('collections/' + collection + '/clean_pfps/' + str(pfp_id) + '.png')
  outfit = Image.open('collections/' + collection + '/outfits/' + outfit + '/' + fit + '.png')

  # Better blending method
  dressed = Image.new("RGBA", pfp.size)
  dressed = Image.alpha_composite(dressed, pfp)
  dressed = Image.alpha_composite(dressed, outfit)
  dressed.save(save_file_path)

  return save_file_path

@bot.command(name="gib", brief='Gib me cool pfp', description='This command will let you be much cooler than you are... fr fr')
async def gib(ctx, collection: str, pfp_id: int, campaign: str, fit: typing.Optional[str] = 'default' ):
  outfit = campaign
  collection = collection.lower()

  if campaign == 'wallpaper':
    try:
      if collection == 'ape':
        img_path = get_daa_image(pfp_id, 'no-background')
        save_file_path = make_wallpaper(collection, pfp_id, img_path)

        await ctx.send(file=discord.File(save_file_path))
      else:
        await ctx.send('Please enter a valid collection. `ape`')
    except:
        await ctx.send('Please enter a valid collection. `ape`')
  else:
    try:
      if collection in collections:
        if collection == 'ape':
          get_daa_image(pfp_id)
        else:
          get_collection_image(collection, pfp_id)
      else: 
        await ctx.send('Please enter a valid collection. ape / dtp / egg')

      save_file_path = combine_images(collection, outfit, fit, pfp_id)

      await ctx.send(file=discord.File(save_file_path))
    except:
      await ctx.send('Please enter valid options for your request.\n\nTry `!gib-help` for more info')


@bot.command(name='gib-help', brief='List avaiable fits', description='This command will list the different outfits available to you')
async def gib_help(ctx):
    message =  """**Formatting the command examples**

```md
!gib [collection] [id] [campaign] [variant]
!gib [ape/dtp/egg] [123] [solcap/solsnap/bussin/beer] [black/blue/red/white... etc]

!gib ape 123 solcap
!gib ape 123 bussin blue
!gib dtp 456 solsnap 
!gib egg 789 beer 
```

==========================

**What I Can Gib**

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
    """
    await ctx.send(message)



load_dotenv()

bot.run(os.environ['DISCORD_TOKEN'])
