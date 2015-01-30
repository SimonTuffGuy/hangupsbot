import hangups

from datetime import datetime, timedelta
import time
from time import mktime
from dateutil import parser
import pytz

def checkpoint(bot, event, date1=None, hour1=None, *args):
    """returns the time of the next checkpoint"""
    if not bot.get_config_option('checkpoint_enabled'):
        bot.send_message_parsed(event.conv, "Checkpoint Cunction Disabled")
        return
    if not bot.get_config_option('timezone'):
        bot.send_message_parsed(event.conv, "No Timezone Set")
        return
    tz = pytz.timezone(bot.get_config_option('timezone'))
    utc = pytz.timezone('UTC')
    dtformat = "%m-%d-%y %H"
    #set the origin time
    t0 = utc.localize(datetime.strptime('07-09-14 16', dtformat))
    hours_per_cycle = 175
    

    if date1 is None:
        t=utc.localize(datetime.utcnow())
    else:
        stamp = '{} {}'.format(date1,hour1)
        try:
            
            indate = tz.localize(parser.parse(stamp))
            t = indate.astimezone(utc)
        except ValueError: 
            bot.send_message_parsed(event.conv, 'The date "{}" is invalid'.format(stamp))
            return

    date1 = t.astimezone(tz).strftime('%m-%d-%y')
    hour1 = t.astimezone(tz).strftime('%H')
    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    seconds
    cycles = seconds // (3600 * hours_per_cycle)
    cycles
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    start
    checkpoint_times = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))
    
    segments = [hangups.ChatMessageSegment('Checkpoint Times for {} at {}:00'.format(date1,hour1), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for num, checkpoint_time in enumerate(checkpoint_times):
        
        if checkpoint_time > t:
            break
        segments.append(hangups.ChatMessageSegment('{} {}'.format(num,checkpoint_time.astimezone(tz).strftime("%m-%d-%y %H:%M %Z"))))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)