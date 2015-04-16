import asyncio
import json
import requests

from hangups.ui.utils import get_conv_name

def _initialise(Handlers, bot=None):
    Handlers.register_user_command(["iitc"])
    return []

def iitc(bot, event, *args):
    config = bot.get_config_option('iitcregion')
    for region in args:
        if region in config:
            url = "http://localhost:31337/"
            payload = json.loads(json.dumps(config[region]))
            payload["name"] = region
            payload["callback"] = "https://localhost:31338/{}".format(event.conv_id)
            
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data = json.dumps(payload), headers = headers, verify=False)
            
            bot.send_html_to_conversation(event.conv_id, "<i>Loading {}, please wait</i>".format(region))
        else:
            bot.send_html_to_conversation(event.conv_id, "<i>Region {} not defined</i>".format(region))