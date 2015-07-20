import datetime

import plugins

import hangups


def _initialise(bot):
    plugins.register_handler(on_watermark_update, type="watermark")
    plugins.register_handler(on_typing_notification, type="typing")


def on_typing_notification(bot, event, command):
    if event.from_bot:
        """ignore self events"""
        return

    typing_status = event.conv_event.status

    user_chat_id = event.user_id.chat_id
    user_full_name = event.user.full_name
    conv_title = bot.conversations.get_name(event.conv_id)

    if typing_status == hangups.schemas.TypingStatus.TYPING:
        print("{} ({}) typing on {} ({})".format(
            user_full_name, user_chat_id, conv_title, event.conv_id))

    elif typing_status == hangups.schemas.TypingStatus.PAUSED:
        print("{} ({}) paused typing on {} ({})".format(
            user_full_name, user_chat_id, conv_title, event.conv_id))

    elif typing_status == hangups.schemas.TypingStatus.STOPPED:
        print("{} ({}) stopped typing on {} ({})".format(
            user_full_name, user_chat_id, conv_title, event.conv_id))

    else:
        raise ValueError("unknown typing status: {}".format(typing_status))


def on_watermark_update(bot, event, command):
    if event.from_bot:
        """ignore self events"""
        return

    utc_datetime = datetime.datetime.fromtimestamp(
        event.timestamp // 1000000, datetime.timezone.utc
    ).replace(microsecond=(event.timestamp % 1000000))

    print("{} ({}) read up to {} ({}) on {} ({})".format(
        event.user.full_name, 
        event.user_id.chat_id, 
        utc_datetime,
        event.timestamp, 
        bot.conversations.get_name(event.conv_id), 
        event.conv_id))
