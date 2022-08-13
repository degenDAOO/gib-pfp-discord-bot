from tweepy import StreamingClient, StreamRule, OAuthHandler, API
import os
from dotenv import load_dotenv
from PIL import Image
import requests
import io

# TW API AUTH
load_dotenv()
auth = OAuthHandler(os.getenv('api-key'), os.getenv('api-secret'))
auth.set_access_token(os.getenv('access-token'), os.getenv('access-secret'))
twitter_api = API(auth, wait_on_rate_limit=True, retry_count=2, retry_delay=2)
bearer_token = os.getenv('bearer-token')


def create_send_tweet(collection, pfp_id, campaign, extra, reply_to):
    """
    Create tweet with image-text and send it
    Arguments:
        collection: str
            name of the collection
        pfp_id: str or int
            numer of the NFT
        campaign: str
            name of the campaign
        extra: str
            extra argument needed depends on the campaign
        reply_to: int
            id of tweet to reply
    """
    if campaign in ['wallpaper', 'banner']:
        image = make_image(collection, pfp_id, campaign, extra)
    elif campaign in ['eye', 'solcap', 'solsnap', 'beer']:
        image = combine_images(collection, pfp_id, campaign)
    elif campaign == 'bussin':
        image = combine_images(collection, pfp_id, campaign, extra)
    else:
        reply_tweet(reply_to, 'is_campaign')
        return
    message = f'Here is your {collection} #{pfp_id} {campaign}'
    twitter_api.update_status_with_media(status=message, filename=image,
                                         in_reply_to_status_id=reply_to,
                                         auto_populate_reply_metadata=True)


def reply_tweet(reply_to, condition):
    """
    Predefine tweets for specific cases. Create and send tweet
    Arguments:
        reply_to: int
            id of tweet to reply
        condition: str
            condition for predefine tweet
    """
    if condition == 'is_reply':
        message = f"Can't be a reply. It must be a new tweet."
    if condition == 'is_troll':
        message = f'You can go and fuck with your mom bozo.'
    if condition == 'is_campaign':
        message = f'That campaign do not exist. Read the pinned message.'

    twitter_api.update_status(status=message,
                              in_reply_to_status_id=reply_to,
                              auto_populate_reply_metadata=True)


def make_image(collection, pfp_id, campaign, bg_color):
    """
    Create image for campaign banner or wallpaper
    Arguments:
        collection: str
            name of the collection
        pfp_id: str or int
            numer of the NFT
        campaign: str
            name of the campaign
        bg_color: str
            color for background
    """
    filename = get_daa_image(pfp_id, 'no-background')
    if campaign == 'wallpaper':
        resize = 780
        paste_x = 0
        paste_y = 908
    elif campaign == 'banner':
        resize = 800
        paste_x = 2000
        paste_y = 200
    save_file_path = f'collections/{collection}/dressed_pfps/{pfp_id}_{campaign}.png'
    bg_color = bg_color
    bg = Image.open(f'collections/ape/outfits/{campaign}/{bg_color.lower()}.png')
    pfp = Image.open(filename)
    pfp = pfp.resize((resize, resize))
    new_pfp = Image.new("RGBA", bg.size)
    new_pfp.paste(pfp, (paste_x, paste_y), mask=pfp)

    img = Image.new("RGBA", bg.size)
    img = Image.alpha_composite(img, bg)
    img = Image.alpha_composite(img, new_pfp)
    img.save(save_file_path)

    return save_file_path


def get_daa_image(pfp_id, type='no-head-traits'):
    """
    Get DAA images for campaign 
    Arguments:
        pfp_id: str or int
            numer of the NFT
        type: str
            type of image needed

    """
    url = f'https://degenape.nyc3.digitaloceanspaces.com/apes/{type}/{pfp_id}.png'
    save_image_file_path = f'collections/ape/clean_pfps/{type}/{pfp_id}.png'

    if os.path.isfile(save_image_file_path):
        return save_image_file_path
    else:
        download_image(url, save_image_file_path)
        return save_image_file_path


def download_image(url, image_file_path):
    """
    Download image from given url
    Arguments:
        url: str
            url for download image
        image_file_path: str
            path where image will be save
    """
    r = requests.get(url, timeout=4.0)
    if r.status_code != requests.codes.ok:
        assert False, f'Status code error: {r.status_code}.'

    with Image.open(io.BytesIO(r.content)) as im:
        im.save(image_file_path)


def combine_images(collection, pfp_id, campaign, fit='default'):
    """
    Create image for campaign
    Arguments:
        collection: str
            name of the collection
        pfp_id: str or int
            numer of the NFT
        campaign: str
            name of the campaign
        fit: str
            name of fit for campaign
    """
    filename = get_daa_image(pfp_id, 'no-head-traits')
    save_file_path = f'collections/{collection}/dressed_pfps/{pfp_id}_{campaign}_{fit}.png'
    outfit_file_path = f'collections/{collection}/outfits/{campaign}/{fit}.png'
    pfp = Image.open(filename)
    outfit = Image.open(outfit_file_path)

    # Better blending method
    dressed = Image.new("RGBA", pfp.size)
    dressed = Image.alpha_composite(dressed, pfp)
    dressed = Image.alpha_composite(dressed, outfit)
    dressed.save(save_file_path)

    return save_file_path


class TweetStreamerV2(StreamingClient):

    def on_tweet(self, tweet):
        """
        All tweets that streamer catch comes here.
        Split the tweet text to decide what bot will do.
        """
        try:
            print(f"{tweet.id} {tweet.created_at} ({tweet.author_id}): {tweet.text}")
            print("-" * 50)
            tweet_text = tweet.text

            # lower case all tweet
            tweet_text_lower = tweet_text.lower()
            
            # split tweet into list of str
            tweet_word_list = tweet_text_lower.split()

            # check if two first words are !gib ape command
            if f'{tweet_word_list[0]} {tweet_word_list[1]}' == '!gib ape':
                # check if pfp_id is between 0 & 10000
                if float(tweet_word_list[2]) > 10000 or 0 > float(tweet_word_list[2]):
                    reply_tweet(tweet.id, 'is_troll')
                else:
                    create_send_tweet(tweet_word_list[1], tweet_word_list[2],
                                      tweet_word_list[3], tweet_word_list[4], tweet.id)

            # check if tweet comes from a reply
            elif f'{tweet_word_list[0]} {tweet_word_list[1]} {tweet_word_list[2]}' == '@gib_pfp_bot !gib ape':
                reply_tweet(tweet.id, 'is_reply')
        except Exception as e:
            print(e)


# start streamer
streamer = TweetStreamerV2(bearer_token)

# add new rules
rule = StreamRule(value="gib ape")
streamer.add_rules(rule)
rules = streamer.get_rules()

# add filters
streamer.filter(expansions="author_id", tweet_fields="created_at")
