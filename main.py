# SPDX-FileCopyrightText: 2024 Deren Vural derenvural@outlook.com
# SPDX-License-Identifier: MIT

##
#  Title: OSRSBlueskyBot
# Author: Deren Vural
#  Notes:
#   https://docs.bsky.app/docs/starter-templates/bots
#   https://docs.bsky.app/blog/rate-limits-pds-v3#pds-distribution-v3
#
#   https://atproto.blue/en/latest/
#   https://github.com/bluesky-hack/bot/blob/main/main.py
#   https://sperea.es/blog/bot-bluesky-rss
#
#   https://github.com/bluesky-social/atproto/tree/main/packages/api
#   https://docs.python.org/3/library/typing.html
##

# imports
from atproto import (
    Client,
    models
)
import os
import dotenv
import feedparser
import requests

# main function
def main() -> bool:
    # Status message
    print("🤖 Starting bot..")

    # Fetch config from environment variables
    configData = fetchConfig()

    # Validate environment variables fetched
    if(configData):
        # Status message
        print("🤖 Bot fetched environment variables..")
    else:
        # Status message
        print("🤖 Bot was unable to fetch environment variables..")

        # Return failure
        return False

    # Create client
    client = Client("https://bsky.social")

    # Log in to Bluesky
    loginSuccess = loginBluesky(
       client,
       configData['BLUESKY_USERNAME'],
       configData['BLUESKY_PASSWORD']
    )

    # Validate log in
    if(loginSuccess):
        # Status message
        print("🤖 Bot is logged in to Bluesky..")
    else:
        # Status message
        print("🤖 Bot failed to log in to Bluesky..")

        # Return failure
        return False
    
    # Get last post
    lastPost = getLastPost(
        client
    )

    if(lastPost == ""):
        # Status message
        print("🤖 Bot cannot get previous post..")
    else:
        # Status message
        print("🤖 Bot fetched previous post..")

    # Fetch RSS content to post
    RSSContent = fetchRSS(
        configData['OSRS_RSS_URL'],
        lastPost
    )

    # If new RSS item found
    if(RSSContent):
        # Status message
        print("🤖 Bot has found a new RSS item..")
    else:
        # Status message
        print("🤖 Bot has not found a new RSS item..")

        # Return failure
        return False

    # Post to Bluesky
    postSuccess = sendPost(
       client,
       RSSContent
    )
    
    # Validate post
    if(postSuccess):
        # Status message
        print("🤖 Bot has posted to Bluesky..")
    else:
        # Status message
        print("🤖 Bot has failed to post to Bluesky..")

        # Return failure
        return False

    # Return success
    return True


# Fetch login info from environment variables
def fetchConfig() -> dict[str, str]:
    # Status message
    print(f"🤖 Bot loading environment variables..")

    if "BLUESKY_USERNAME" not in os.environ:
        print(f"🤖 Bot cannot find key \'BLUESKY_USERNAME\' in environment variables..")
        return {}
    if "BLUESKY_PASSWORD" not in os.environ:
        print(f"🤖 Bot cannot find key \'BLUESKY_PASSWORD\' in environment variables..")
        return {}
    if "OSRS_RSS_URL" not in os.environ:
        print(f"🤖 Bot cannot find key \'OSRS_RSS_URL\' in environment variables..")
        return {}

    # Return in dictionary
    return {
        'BLUESKY_USERNAME' : os.environ['BLUESKY_USERNAME'],
        'BLUESKY_PASSWORD' : os.environ['BLUESKY_PASSWORD'],
            'OSRS_RSS_URL' : os.environ['OSRS_RSS_URL']
    }

def getLastPost(
      client: Client
) -> str:
    # Attempt to get last post
    try:
        # Return text of last post
        posts = client.app.bsky.feed.post.list(client.me.did, limit=1)
        for uri, post in posts.records.items():
            return post.text
    except Exception as e:
        # Return failure
        print(e)
        return ""


# Log in client to Bluesky
# TODO: return & check success
def loginBluesky(
      client: Client,
    username: str,
    password: str
) -> bool:
    # Log in
    try:
        client.login(username, password)
    except Exception as e:
        # Return failure
        print(e)
        return False
    
    # Return success
    return True

# Get RSS feed
def fetchRSS(
      RSSUrl: str,
    lastPost: str
) -> dict[str, str]:
    # Parse the RSS feed
    feed = feedparser.parse(
        RSSUrl
    )

    # Check if is new item
    try:
        if feed.entries[0].summary != lastPost:
            # Return feed item content as dictionary
            return {
                   'TITLE' : feed.entries[0].title,
                 'SUMMARY' : feed.entries[0].summary,
                     'URL' : feed.entries[0].link,
                    'DATE' : feed.entries[0].published,
                'IMAGEURL' : feed.entries[0].links[0].href
            }
        else:
            # Return empty dictionary
            return {}
    except:
        print("🤖 Bot cannot find content in RSS feed..")
        return {}

# Download image
def downloadImage(
    url: str
):
    # Attempt to download image
    try:
        return requests.get(url).content
    except Exception as e:
        # Return 'None'
        print(e)
        return

# Post to Bluesky
# TODO: return & check success
def sendPost(
        client: Client,
    RSSContent: dict[str, str]
) -> bool:
    # Validate RSS content
    if "TITLE" not in RSSContent:
        print(f"🤖 Bot cannot find key \'TITLE\' in dictionary..")
        return {}
    if "SUMMARY" not in RSSContent:
        print(f"🤖 Bot cannot find key \'SUMMARY\' in dictionary..")
        return {}
    if "URL" not in RSSContent:
        print(f"🤖 Bot cannot find key \'URL\' in dictionary..")
        return {}
    if "IMAGEURL" not in RSSContent:
        print(f"🤖 Bot cannot find key \'IMAGEURL\' in dictionary..")
        return {}
    
    # Create & send post
    try:
        # Attempt to download image
        image = downloadImage(RSSContent['IMAGEURL'])

        # Create thumbnail
        thumb = client.upload_blob(image)

        # Create embedded link
        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                title=RSSContent['TITLE'],
                description=RSSContent['SUMMARY'],
                uri=RSSContent['URL'],
                thumb=thumb.blob,
            )
        )

        # Send post with text
        client.send_post(RSSContent['SUMMARY'], embed=embed)
    except Exception as e:
        # Return failure
        print(e)
        return False
    
    # Return success
    return True


# Run main() function
if __name__ == '__main__':
    if(main() == True):
        print("🤖 Bot succeeded!")
    else:
        print("🤖 Bot failed!")
