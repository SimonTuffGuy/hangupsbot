import hangups

from datetime import datetime, timedelta
import time
from time import mktime
from dateutil import parser
import pytz

def cp(bot, event,*args):
    """Returns the time left until the next checkpoint"""
    if not bot.get_config_option('timezone'):
        bot.send_message_parsed(event.conv, "No Timezone Set")
        return
    tz = pytz.timezone(bot.get_config_option('timezone'))
    utc = pytz.timezone('UTC')
    dtformat = "%m-%d-%y %H"
    t1 = utc.localize(datetime.utcnow())
    t0 = utc.localize(datetime(2014, 7, 9, 10, 0))
    #print (t1)
    tdelta = t1-t0
    cycle = timedelta(hours=175)
    cycles = tdelta // cycle
    #print(cycles)
    cycle_start = t0+(cycles*cycle)
    #print(cycle_start)
    cycle_start
    cdelta = t1 - cycle_start
    checkpoint = timedelta(hours=5)
    checkpoints = (cdelta // checkpoint) +1
    checkpoint_start = cycle_start+(checkpoint*checkpoints)
    cpdelta = checkpoint_start - t1
    total_seconds = int(cpdelta.total_seconds())
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    
    segments = [hangups.ChatMessageSegment('Time Until Next Checkpoint', is_bold=True),
    hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
    hangups.ChatMessageSegment('{} hrs {} mins {} secs'.format(hours,minutes,seconds))
    ]
    #output the results
    bot.send_message_segments(event.conv, segments)
    
def cps(bot, event, date1=None, hour1=None, *args):
    """cps <date> <time> returns the checkpoints before the date and time specified, starting with the previous cycle.  If no date or time is entered, the current time is used."""
    if not bot.get_config_option('timezone'):
        bot.send_message_parsed(event.conv, "No Timezone Set")
        return
    #set the local time zone from config.json    
    tz = pytz.timezone(bot.get_config_option('timezone'))
    utc = pytz.timezone('UTC')
    #set the origin time
    t0 = utc.localize(datetime(2014, 7, 9, 10, 0))
    #set hours in a cycle
    hours_per_cycle = 175
    
    #fill in current datetime if none is specified in the arguments
    if date1 is None:
        t=utc.localize(datetime.utcnow())
    #else, set the datetime as specified the the arguments
    else:
        if hour1 is None:
            hour1 = time.strftime('%H:%M',time.localtime())
        stamp = '{} {}'.format(date1,hour1)
        try:
            
            indate = tz.localize(parser.parse(stamp))
            t = indate.astimezone(utc)
        #check for errors or invalid dates
        except ValueError: 
            bot.send_message_parsed(event.conv, 'The date "{}" is invalid'.format(stamp))
            return
    #set the human readable dates and correct them for display and timezone            
    date1 = t.astimezone(tz).strftime('%m-%d-%y')
    hour1 = t.astimezone(tz).strftime('%H:%M %Z')

    #start the math on figuring the cycles
    seconds = mktime(t.timetuple()) - mktime(t0.timetuple())
    seconds
    cycles = seconds // (3600 * hours_per_cycle)
    cycles
    start = t0 + timedelta(hours=cycles * hours_per_cycle)
    start
    checkpoint_times = map(lambda x: start + timedelta(hours=x), range(0, hours_per_cycle, 5))
    
    #start the output of results
    segments = [hangups.ChatMessageSegment('Checkpoint Times for {} at {}'.format(date1,hour1), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    for num, checkpoint_time in enumerate(checkpoint_times):
        
        if checkpoint_time > t:
            break
        segments.append(hangups.ChatMessageSegment('{} {}'.format(num,checkpoint_time.astimezone(tz).strftime("%m-%d-%y %H:%M %Z"))))
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    #output the results
    bot.send_message_segments(event.conv, segments)
