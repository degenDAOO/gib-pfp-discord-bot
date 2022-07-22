# Discord Bot for Creating Degeniverse Promo PFPs

We originally forked the [MonkeyDAO Discord Bot](https://github.com/0xbagp/new-fit-for-your-pfp---discord-bot) to help promote various marketing efforts by adding custom traits to your DAA / DTP / DEGG pfp. Over time it was re-written to suit our needs and make it easier to roll out new campaigns with ease, and changed enough to deserve its own repo. 

## Results
```
[In Discord] !gib ape 1297 beer
```
![clean_pfp](/docs/img/ape.png) ![suit](/docs/img/beer_hat.png) ![pfp_with_fit](/docs/img/beer-ape.png)

## Cool things going on here...
Users simply need to type their collection (`ape/dtp/egg`) and the number of the NFT, along with the name of the campaign/promo. In the background we download the image, before performing an image tranformation, and sending it back to discord. 

For DAA, we have all the image urls for versions without any headtraits (super useful), but for DTP/DEGG we use [The Hyperspace API](https://docs.hyperspace.xyz/hype/developer-guide/overview) to querey the chain for the NFT metadata, pull the image url, download that and then perform the transformation. No need for a big json file for every Degeniverse NFT!



# Getting Started

## 1. Setup

First, setup your [.env](https://medium.com/chingu/an-introduction-to-environment-variables-and-how-to-use-them-f602f66d15fa) file to store your secrets. See [Create the Discord Bot](#3-create-the-discord-bot) for generating that token. 
```sh
cp .env.example .env

## .env file
DISCORD_TOKEN=
HYPER_TOKEN=
```

We use [Poetry](https://python-poetry.org/) for our dependency & package mgmt. To get everything installed and run the application:

```sh
poetry install

poetry run python main.py
```
This runs the bot locally on your machine... fine for testing, but you'll want to [Deploy to Heroku](#4-deploy-to-heroku) so it runs on an always available server.

## 2. Adding a new campaign

* In each collection folder, create a folder in `/outfits` with the name of the campaign.
  > N.B. this will be used in the command so choose wisely.

* Next add the transparent pngs into that folder, with each filename representing a "variant" of the trait. If there are no variants, then name the file "default.png" for easier usage.

* Update the `gib-help` bot command in `main.py` with the new campaign info to help people know how to use the thing.

## 3. Create the Discord Bot
Easiest just to point you here: [Setup the bot](https://discordpy.readthedocs.io/en/stable/discord.html) and then invite it into your server -- giving it access to the channels you'd like people to use it. 

## 4. Deploy to Heroku
We've included a `Procfile, requirements.txt, and runtime.txt` files to make it easy for you to deploy your bot for free on Heroku. Here is a [handy guide](https://devcenter.heroku.com/articles/getting-started-with-python) to get you started.

But once you're setup, generally it looks like this to deploy your code to Heroku and have the process started:
```sh
git push heroku master
```

## 5. How to use it in Discord

Generally this is the pattern utilized to initiate the bot in discord. Everything is explained in the `main.py` file as well. The `variant` parameter is optional and assumed to be `default`. See Bussin for an example of using lots of different variants.

```md
!gib [collection] [id] [campaign] [variant]
!gib [ape/dtp/egg] [123] [solcap/solsnap/bussin/beer] [black/blue/red/white... etc]

Ex:
!gib ape 123 solcap
!gib ape 123 bussin blue
!gib dtp 456 solsnap 
!gib egg 789 beer 
```

---

## Thats it!

Hope this helps you develop something cool for your community! Give me a shout at [@jsb_sol](https://twitter.com/jsb_sol) if you need help or have built something cool yourself!
