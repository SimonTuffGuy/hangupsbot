import asyncio
import sqlite3

_internal = {}

def _initialise(Handlers, bot=None):
    database = bot.get_config_option("keeperdb")
    if database:
        conn = sqlite3.connect(database)
        _internal['keeper_connection'] = conn
        _internal['keeper_cursor'] = conn.cursor()
        Handlers.register_admin_command(["keeper"])
    else:
        print("plugin.keeper: config.keeperdb requires path to database")
    return []


@asyncio.coroutine
def keeper(bot, event, *args):
    """manage database entries<br />
       /bot keeper action type [code]<br />
       where action is one of show, gettypes, get, use, add, or addtype<br />
       /bot keeper show - show all unused entries<br />
       /bot keeper gettypes - get list of entry types (for adding)<br />
       /bot keeper get [type] - get entries of a certain type<br />
       /bot keeper use [entry] - mark an entry as used<br />
       /bot keeper add [type] [entry] - add an entry of type<br />
       /bot keeper addtype [type] - add a new type
       """

    response = ""
    cursor = _internal['keeper_cursor']

    if len(args) == 0:
        response = "usage: /bot keeper action type [code]"
    else:
        if len(args) == 1 and args[0] == "show":
            response = "<b>Passcode | Description | Added</b><br />"
            for row in cursor.execute('SELECT passcode, description, added from v_active_passcodes'):
                response = response + "%s | %s | %s<br />" % (row[0], row[1], row[2])

        if len(args) == 1 and args[0] == "gettypes":
            response = "<b>Type | Description</b><br />"
            for row in cursor.execute('SELECT codetype, description from passcode_types'):
                response = response + "%s | %s<br />" % (row[0], row[1])

        if len(args) == 2 and args[0] == "get":
            codetype = args[1]
            response = "<b>Passcode | Description | Added</b><br />"
            for row in cursor.execute('SELECT passcode, description, added, from v_active_passcodes where description=?', codetype):
                response = response + "%s | %s | %s<br />" % (row[0], row[1], row[2])

        if len(args) == 2 and args[0] == "use":
            passcode = args[1]
            void = cursor.execute('UPDATE passcodes SET retrieved=datetime("now") WHERE passcode=?', (passcode,))
            if cursor.rowcount != 1:
                response = "<b>Error</b>: Invalid passcode specified"
            else:
                response = "Passcode marked as used"

        if len(args) == 3 and args[0] == "add":
            codetype = args[1]
            passcode = args[2]

            void = cursor.execute('SELECT codetype FROM passcode_types WHERE codetype=?', (codetype,))
            if cursor.rowcount != 1:
                response = "<b>Error</b>: Invalid code type specified"
            else:
                void = cursor.execute('INSERT INTO passcodes (passcode, codetype) VALUES (?, ?)', (passcode, codetype))
                if cursor.rowcount != 1:
                    response = "<b>Error</b>: Failed to insert passcode in to database"
                else:
                    response = "Passcode added to database"

        if len(args) == 3 and args[0] == "addtype":
            codetype = args[1]
            description = args[2]
            void = cursor.execute('INSERT INTO passcode_types (codetype, description) VALUES (?, ?)', (codetype, description))
            if cursor.rowcount != 1:
                response = "Failed to add new passcode type"
            else:
                response = "Passcode type added to database"

    if (len(response) > 0):
        bot.send_message_parsed(event.conv, response)
    else:
        bot.send_message_parsed(event.conv, "<b>Error</b>: Invalid command arguments")
