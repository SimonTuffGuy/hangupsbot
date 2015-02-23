import sys, json, asyncio, logging, os

import hangups
from hangups.ui.utils import get_conv_name

from utils import text_to_segments


class CommandDispatcher(object):
    """Register commands and run them"""
    def __init__(self):
        self.commands = {}
        self.unknown_command = None


    @asyncio.coroutine
    def run(self, bot, event, *args, **kwds):
        """Run command"""
        try:
            func = self.commands[args[0]]
        except KeyError:
            if self.unknown_command:
                func = self.unknown_command
            else:
                raise

        # Automatically wrap command function in coroutine
        # (so we don't have to write @asyncio.coroutine decorator before every command function)
        func = asyncio.coroutine(func)

        args = list(args[1:])

        try:
            yield from func(bot, event, *args, **kwds)
        except Exception as e:
            message = "CommandDispatcher.run: {}".format(func.__name__)
            print("EXCEPTION in " + message)
            logging.exception(message)


    def register(self, func):
        """Decorator for registering command"""
        self.commands[func.__name__] = func
        return func

    def register_unknown(self, func):
        """Decorator for registering unknown command"""
        self.unknown_command = func
        return func


# CommandDispatcher singleton
command = CommandDispatcher()

@command.register
def help(bot, event, cmd=None, *args):
    """list supported commands"""
    if not cmd:
        admins_list = bot.get_config_suboption(event.conv_id, 'admins')

        commands_all = command.commands.keys()
        commands_admin = bot._handlers.get_admin_commands(event.conv_id)
        commands_nonadmin = list(set(commands_all) - set(commands_admin))

        text_html = '<b>User commands:</b><br />' + ', '.join(sorted(commands_nonadmin))
        if event.user_id.chat_id in admins_list:
            text_html = text_html + '<br /><b>Admin commands:</b><br />' + ', '.join(sorted(commands_admin))
    else:
        try:
            command_fn = command.commands[cmd]
            text_html = "<b>{}</b>: {}".format(cmd, command_fn.__doc__)
        except KeyError:
            yield from command.unknown_command(bot, event)
            return

    # help can get pretty long, so we send a short message publicly, and the actual help privately
    conv_1on1_initiator = bot.get_1on1_conversation(event.user.id_.chat_id)
    if conv_1on1_initiator:
        bot.send_message_parsed(conv_1on1_initiator, text_html)
        if conv_1on1_initiator.id_ != event.conv_id:
            bot.send_message_parsed(event.conv, "<i>{}, I've sent you some help ;)</i>".format(event.user.full_name))
    else:
        bot.send_message_parsed(event.conv, "<i>{}, before I can help you, you need to private message me and say hi.</i>".format(event.user.full_name))


@command.register
def ping(bot, event, *args):
    """reply to a ping"""
    bot.send_message(event.conv, 'pong')


@command.register_unknown
def unknown_command(bot, event, *args):
    """handle unknown commands"""
    bot.send_message(event.conv,
                     '{}: unknown command'.format(event.user.full_name))