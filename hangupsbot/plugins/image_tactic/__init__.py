"""trigger strategy images from the image_tactic directory"""

import io
import os
import re
import random
import aiohttp

import plugins


_lookup = {}


def _initialise(bot):
    _load_all_the_things()
    plugins.register_admin_command(["tactic"])


def _load_all_the_things():
    plugin_dir = os.path.dirname(os.path.realpath(__file__))
    #source_file = os.path.join(plugin_dir, "sauce.txt")
    #with open(source_file) as f:
    #    content = f.read().splitlines()
    for files in plugin_dir:
        if file.endswith(".jpg"):
            trigger = os.path.splitext(file)[0]
            image = file
            _lookup[trigger] = image
    print("tactic image: {} trigger(s) loaded".format(len(_lookup)))


def _get_a_link(trigger):
    if trigger in _lookup:
        return _lookup[trigger]
    return False

def tactic(bot, event, *args):
    try_trigger = _get_a_link(args[0])
    if _externals["running"]:
        bot.send_html_to_conversation(event.conv_id, "<i>busy, give me a moment...</i>")
        return

    _externals["running"] = True

    try:
        #jpg_link = 'http://digitalmatters.net/Radar/kdmx_cr_0.jpg'
        jpg_link = _get_a_link(try_trigger)

        image_data = urllib.request.urlopen(jpg_link)
        filename = os.path.basename(jpg_link)

        #legacy_segments = [hangups.ChatMessageSegment(jpg_link, hangups.SegmentType.LINK, link_target=jpg_link)]

        print("meme(): uploading {} from {}".format(filename, jpg_link))
        # read the resulting file into a byte array
        file_resource = open(filename, 'rb')
        image_data = io.BytesIO(file_resource.read())
        #os.remove(filename)

        image_id = yield from bot._client.upload_image(image_data, filename=filename)
        yield from bot._client.sendchatmessage(event.conv.id_, None, image_id=image_id)

    except Exception as e:
        bot.send_html_to_conversation(event.conv_id, "<i>something went wrong! try again</i>")
        print("{}".format(e))
    finally:
        _externals["running"] = False