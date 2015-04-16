import hangups

def lookup(bot, event, *args):
    """find keywords in a specified spreadsheet"""

    if not bot.get_config_option('spreadsheet_enabled'):
        bot.send_message_parsed(event.conv, "Spreadsheet function disabled")
        return

    if not bot.get_config_option('spreadsheet_url'):
        bot.send_message_parsed(event.conv, "Spreadsheet URL not set")
        return

    if not bot.get_config_option('spreadsheet_table_class'):
        bot.send_message_parsed(event.conv, "Spreadsheet table identifier not set")
        return

    spreadsheet_url = bot.get_config_option('spreadsheet_url')
    table_class = bot.get_config_option('spreadsheet_table_class') # Name of table class to search

    keyword = ' '.join(args)

    segments = [hangups.ChatMessageSegment('Results for keyword "{}":'.format(keyword),
                                           is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK)]
    print("{0} ({1}) has requested to lookup '{2}'".format(event.user.full_name, event.user.id_.chat_id, keyword))
    import urllib.request
    html = urllib.request.urlopen(spreadsheet_url).read()

    keyword_lower = keyword.strip().lower()

    data = []

    counter = 0
    counter_max = 5 # Maximum rows displayed per query

    # Adapted from http://stackoverflow.com/questions/23377533/python-beautifulsoup-parsing-table
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(str(html, 'utf-8'))
    table = soup.find('table', attrs={'class':table_class})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')

    for row in rows:
        col = row.find_all('td')
        cols = [ele.text.strip() for ele in col]
        data.append([ele for ele in cols if ele]) # Get rid of empty values

    for row in data:
        matchfound = 0
        for cell in row:
            testcell = str(cell).lower().strip()
            if (keyword_lower in testcell) and counter < counter_max and matchfound == 0:
                segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
                segments.append(hangups.ChatMessageSegment('Row {}: '.format(counter+1),
                                                       is_bold=True))
                for datapoint in row:
                    if datapoint.startswith('http'):
                        segments.append(hangups.ChatMessageSegment("", hangups.SegmentType.LINK, link_target=datapoint))
                    else:
                        segments.append(hangups.ChatMessageSegment(datapoint))
                    segments.append(hangups.ChatMessageSegment(' | ', is_bold=True))
                segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
                counter += 1
                matchfound = 1
            elif (keyword_lower in testcell) and counter >= counter_max:
                counter += 1

    if counter > counter_max:
        segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
        segments.append(hangups.ChatMessageSegment('{0} rows found. Only returning first {1}.'.format(counter, counter_max), is_bold=True))
    if counter == 0:
        segments.append(hangups.ChatMessageSegment('No match found', is_bold=True))

    segments.append(hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK))
    bot.send_message_segments(event.conv, segments)
