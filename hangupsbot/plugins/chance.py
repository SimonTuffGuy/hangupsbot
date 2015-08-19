import asyncio

from random import randint

import plugins


def _initialise(bot):
    plugins.register_handler(_handle_me_action)
    plugins.register_user_command(["diceroll", "d12roll", "d20roll", "coinflip"])

def _handle_me_action(bot, event, command):
    if event.text.startswith('/me'):
        if event.text.find("roll dice") > -1 or event.text.find("rolls dice") > -1 or event.text.find("rolls a dice") > -1 or event.text.find("rolled a dice") > -1:
            yield from asyncio.sleep(0.2)
            yield from command.run(bot, event, *["diceroll"])
        elif event.text.find("roll d12") > -1 or event.text.find("rolls d12") > -1 or event.text.find("rolls a d12") > -1 or event.text.find("rolled a d12") > -1:
            yield from command.run(bot, event, *["d12roll"])
        elif event.text.find("roll d20") > -1 or event.text.find("rolls d20") > -1 or event.text.find("rolls a d20") > -1 or event.text.find("rolled a d20") > -1:
            yield from command.run(bot, event, *["d20roll"])
        elif event.text.find("flips a coin") > -1 or event.text.find("flips coin") > -1 or event.text.find("flip coin") > -1 or event.text.find("flipped a coin") > -1:
            yield from asyncio.sleep(0.2)
            yield from command.run(bot, event, *["coinflip"])
        else:
            pass

def diceroll(bot, event, *args):
    """roll a dice"""
    yield from bot.coro_send_message(event.conv, _("<i>{} rolled <b>{}</b></i>").format(event.user.full_name, randint(1,6)))

def d12roll(bot, event, *args):
    bot.send_message_parsed(event.conv, "<i>{} rolled <b>{}</b></i>".format(event.user.full_name, randint(1,12)))

def d20roll(bot, event, *args):
    bot.send_message_parsed(event.conv, "<i>{} rolled <b>{}</b></i>".format(event.user.full_name, randint(1,20)))

def coinflip(bot, event, *args):
    """flip a coin"""
    if randint(1,2) == 1:
        yield from bot.coro_send_message(event.conv, _("<i>{}, coin turned up <b>heads</b></i>").format(event.user.full_name))
    else:
        yield from bot.coro_send_message(event.conv, _("<i>{}, coin turned up <b>tails</b></i>").format(event.user.full_name))
