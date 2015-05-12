import os
import asyncio
import aiohttp
import hangups
import urllib.request
import plugins

_externals = { "running": False }


def _initialise(bot):
    plugins.register_user_command(["radar"])
    #Handlers.register_user_command(["radar"])
    return []

def radar(bot, event, *args):
    if _externals["running"]:
        bot.send_html_to_conversation(event.conv_id, "<i>busy, give me a moment...</i>")
        return

    _externals["running"] = True

    try:
        jpg_link = 'http://digitalmatters.net/Radar/kdmx_cr_0.jpg'

        image_data = urllib.request.urlopen(jpg_link)
        filename = os.path.basename(jpg_link)

        #legacy_segments = [hangups.ChatMessageSegment(jpg_link, hangups.SegmentType.LINK, link_target=jpg_link)]

        print("meme(): uploading {} from {}".format(filename, jpg_link))
        photo_id = yield from bot._client.upload_image(image_data, filename=filename)

        bot.send_message_segments(event.conv.id_, None, image_id=photo_id)

    except Exception as e:
        bot.send_html_to_conversation(event.conv_id, "<i>something went wrong! try again</i>")
        print("{}".format(e))
    finally:
        _externals["running"] = False
