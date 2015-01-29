import asyncio

from random import randint

def _initialise(command):
    command.register_handler(_handle_me_action)


@asyncio.coroutine
def _handle_me_action(bot, event, command):
    if event.text.startswith('/me'):
        if event.text.find("roll dice") > -1 or event.text.find("rolls dice") > -1 or event.text.find("rolls a dice") > -1 or event.text.find("rolled a dice") > -1:
            yield from command.run(bot, event, *["diceroll"])
        elif event.text.find("roll d12") > -1 or event.text.find("rolls d12") > -1 or event.text.find("rolls a d12") > -1 or event.text.find("rolled a d12") > -1:
            yield from command.run(bot, event, *["d12roll"])
        elif event.text.find("roll d20") > -1 or event.text.find("rolls d20") > -1 or event.text.find("rolls a d20") > -1 or event.text.find("rolled a d20") > -1:
            yield from command.run(bot, event, *["d20roll"])
        elif event.text.find("flips a coin") > -1 or event.text.find("flips coin") > -1 or event.text.find("flip coin") > -1 or event.text.find("flipped a coin") > -1:
            yield from command.run(bot, event, *["coinflip"])
        else:
            pass


def diceroll(bot, event, *args):
    bot.send_message_parsed(event.conv, "<i>{} rolled <b>{}</b></i>".format(event.user.full_name, randint(1,6)))

def d12roll(bot, event, *args):
    bot.send_message_parsed(event.conv, "<i>{} rolled <b>{}</b></i>".format(event.user.full_name, randint(1,12)))

def d20roll(bot, event, *args):
    bot.send_message_parsed(event.conv, "<i>{} rolled <b>{}</b></i>".format(event.user.full_name, randint(1,20)))

def coinflip(bot, event, *args):
    if randint(1,2) == 1:
        bot.send_message_parsed(event.conv, "<i>{}, coin turned up <b>heads</b></i>".format(event.user.full_name))
    else:
        bot.send_message_parsed(event.conv, "<i>{}, coin turned up <b>tails</b></i>".format(event.user.full_name))
