import hangups
from subprocess import check_output

def fortune(bot, event, *args):
    """Prints a funny joke or riddle, piped from the fortune command"""
    fortune = check_output(["fortune", "-s"])
    bot.send_message_parsed(event.conv, '{}'.format(fortune.decode("utf-8")))

def fortuneo(bot, event, *args):
    """Prints an offensive joke or riddle, piped from the fortune command"""
    fortune = check_output(["fortune", "-so"])
    bot.send_message_parsed(event.conv, '{}'.format(fortune.decode("utf-$")))
