import hangups

from datetime import datetime, timedelta
import time
from time import mktime

def checkpoint(bot, event, date1=time.strftime("%m/%d/%y"), hour1=time.strftime("%H"), *args):
    """returns the time of the next checkpoint"""
    if not bot.get_config_option('checkpoint_enabled'):
        bot.send_message_parsed(event.conv, "checkpoint function disabled")
        return
    t0 = datetime.strptime('2014-07-09 11', '%Y-%m-%d %H')
    hours_per_cycle = 175
    
    try:
        stamp = '{} {}'.format(date1,hour1)
        t = datetime.strptime(stamp, '%m/%d/%y %H')
    except ValueError:
        bot.send_message_parsed(event.conv, 'Invalid Date: {}'.format(stamp))
        return

    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    cycles = seconds // (3600 * hours_per_cycle)
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    checkpoint_times = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))
    
    segments = [hangups.ChatMessageSegment("Checkpoint Times for {} at {}:00").format(date1,hour1),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for num, checkpoint_time in enumerate(checkpoint_times):
        if checkpoint_time > t:
            break
        segments.append(hangups.ChatMessageSegment('{} {}'.format(num,checkpoint_time)))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)