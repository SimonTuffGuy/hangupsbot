import asyncio
import json
import requests
import json
import plugins

from urllib.parse import urlparse, parse_qs
from hangups.ui.utils import get_conv_name

url = "http://localhost:31337/"
headers = {'content-type': 'application/json'}

def _initialise(bot):
    plugins.register_user_command(["iitc", "iitcregion", "iitcdraw"])
    #Handlers.register_user_command(["iitc", "iitcregion", "iitcdraw"])
    return []

def iitc(bot, event, *args):
    """
    Returns an iitc screenshot for the requested region
    """
    config = bot.get_config_option('iitcregion')
    for region in args:
        if region in config:
            payload = json.loads(json.dumps(config[region]))
            payload["name"] = region
            payload["callback"] = "https://localhost:31338/{}".format(event.conv_id)
            
            headers = {'content-type': 'application/json'}
            try:
              r = requests.post(url, data = json.dumps(payload), headers = headers, verify=False)
              bot.send_html_to_conversation(event.conv_id, "<i>Loading {}, please wait</i>".format(region))
            except requests.exceptions.ConnectionError:
              bot.send_html_to_conversation(event.conv_id, "<i>Casper not ready :(</i>")
        else:
            bot.send_html_to_conversation(event.conv_id, "<i>Region {} not defined</i>".format(region))

def iitcregion(bot, event, name=None, url=None):
  """
  Adds a region to the bot's memory.
  Usage: /bot iitcregion name iitc_url
  """
  if not name or not url:
    config = bot.get_config_option('iitcregion')
    regions = ", ".join(config)
    bot.send_html_to_conversation(event.conv_id, "<i>{}: Configured regions: {}</i>".format(event.user.full_name, regions))
    return
  parsed = urlparse(url)
  query = parse_qs(parsed.query)
  latlng = list(map(float, query['ll'][0].split(',')))
  zoom = int(query['z'][0])
  obj = {"latlng":latlng, "zoom":zoom}
  bot.config.set_by_path(["iitcregion", name], obj)
  bot.config.save()
  bot.send_html_to_conversation(event.conv_id, "<i>{}: {} saved</i>".format(event.user.full_name, name))

def iitcdraw(bot, event, action=None, name=None, plan=None):
  """
  Stores json for field plans, and adds or removes them from the intel map
  """
  if not action:
    config = bot.get_config_option('iitcdraw')
    plans = ', '.join(config)
    bot.send_html_to_conversation(event.conv_id, "<i>{}: Configured plans: {}</i>".format(event.user.full_name, plans))
    return
  elif action == 'store' and name and plan:
    bot.config.set_by_path(["iitcdraw", name], json.loads(plan))
    bot.config.save()
    bot.send_html_to_conversation(event.conv_id, "<i>{}: {} saved</i>".format(event.user.full_name, name))
  elif action == 'clear':
    try:
      r = requests.post(url, data = json.dumps({"action":"clear"}), headers = headers, verify=False)
      bot.send_html_to_conversation(event.conv_id, "<i>Clear sent to Casper</i>")
    except requests.exceptions.ConnectionError:
      bot.send_html_to_conversation(event.conv_id, "<i>Casper not ready :(</i>")
  else:
    try:    
      plan = bot.config.get_by_path(["iitcdraw", action])
    except KeyError:
      bot.send_html_to_conversation(event.conv_id, "<i>No such plan: {}</id>".format(action))
      return
    payload = {"action": "load", "json": json.dumps(plan)}
    try:
      r = requests.post(url, data = json.dumps(payload), headers = headers, verify=False)
      bot.send_html_to_conversation(event.conv_id, "<i>{} sent to Casper</i>".format(action))
    except requests.exceptions.ConnectionError:
      bot.send_html_to_conversation(event.conv_id, "<i>Casper not ready :(</i>")