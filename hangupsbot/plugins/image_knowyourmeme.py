from bs4 import BeautifulSoup

import os
import random
import asyncio
import aiohttp
import hangups
import urllib.request
import io

_externals = { "running": False }


def _initialise(Handlers, bot=None):
    Handlers.register_user_command(["meme"])
    return []


@asyncio.coroutine
def _retrieve(url):
    print("meme._retrieve(): getting {}".format(url))
    response = yield from aiohttp.request('GET', url)
    assert response.status == 200
    return (yield from response.read())

def _find_links(content, css_selector):
    soup = BeautifulSoup(content)
    links = soup.select(css_selector)
    print("Found {} images".format(len(links)))
    return links

@asyncio.coroutine
def meme(bot, event, *args):
    try:
        query = " ".join(args)
        print("meme(): args = " + query)

        # content = asyncio.get_event_loop().run_until_complete(_retrieve("http://knowyourmeme.com/search?context=images&q=" + urllib.request.quote(query)))
        content = yield from _retrieve("http://knowyourmeme.com/search?context=images&q=" + urllib.request.quote(query))
        links = _find_links(content, "#photo_gallery .item img")

        if len(links) > 0:
            chosen_link_tag = random.choice(links)
            instance_link = chosen_link_tag.get("data-src")

            print("fetching link {}".format(instance_link))
            r = yield from aiohttp.request('GET', instance_link)
            raw = yield from r.read()
            image_data = io.BytesIO(raw)
            
            filename = os.path.basename(instance_link)

            legacy_segments = [hangups.ChatMessageSegment(instance_link, hangups.SegmentType.LINK, link_target=instance_link)]

            print("meme(): uploading {} from {}".format(filename, instance_link))
            photo_id = yield from bot._client.upload_image(image_data, filename=filename)

            bot.send_message_segments(event.conv.id_, legacy_segments, image_id=photo_id)

        else:
            bot.send_html_to_conversation(event.conv_id, "<i>couldn't find a nice picture :( try again</i>")
    except Exception as e:
        bot.send_html_to_conversation(event.conv_id, "<i>couldn't find a suitable meme! try again</i>")
        print("{}".format(e))
