"""
## Grammar

We're taking cues from
[infobot](http://www.infobot.org/guide-0.43.x.html) on grammar.

Set factoids: Abierto will respond to "X is Y" and "X are Y".

Access factoids: "What is X?", "Where is X?", or "X?"  If there are
too many answers, it will send privmsg.  If there's just a giant pile
of them, it will tell you that.

Alter factoids: Address the bot and use "Abierto: X =~ s/A/B/" and
that will change all instances of A to B in the factoid.

Append: "X is also Y" will add an answer to X's list of factoids.

Delete factoid: "Abierto: forget X"

Replace factoid: "Abierto: no, X is Y"  will replace the factoid with Y.
"""

import re
import sopel.module
import sqlite3

def setup(bot):
    db = sqlite3.connect(bot.config.urkel.db_file)
    crsr = db.cursor()
    crsr.execute("CREATE table if not exists factoids "+
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "+
                 "trigger VARCHAR NOT NULL, "+
                 "factoid VARCHAR NOT NULL, "+
                 "user VARCHAR NOT NULL, "+
                 "CONSTRAINT factoid_unique UNIQUE (factoid, trigger))")
    db.commit()
    db.close()
    
@sopel.module.nickname_commands(r'(.*?) is (.*?)')
@sopel.module.nickname_commands(r'(.*?) are (.*?)')
def set_factoid(bot, trigger):
    nick = trigger.nick
    if re.match(r"{}\b".format(bot.nick), trigger):
        trigger = re.sub(r"^{}\S*\s*".format(bot.nick), '', trigger)
        
    one = re.match(r'(.*?) is (.*)', trigger)
    multi = re.match(r'(.*?) are (.*)', trigger)
    if one and multi:
        if len(one.groups()[0]) < len(multi.groups()[0]):
            found = one.groups()
        else:
            found = multi.groups()
    elif one:
        found = one.groups()
    elif multi:
        found = multi.groups()
    else:
        bot.say("set_factoid triggers, but no regexes match?!")
        return
    bot.say("trigger = {0}; factoid = {1} {2}".format(found[0], found[1], found))

    db = sqlite3.connect(bot.config.urkel.db_file)
    crsr = db.cursor()
    crsr.execute('INSERT or IGNORE INTO factoids (trigger, factoid, user) VALUES (?,?,?)', [found[0], found[1], nick])
    db.commit()
    db.close()

@sopel.module.require_privmsg()
@sopel.module.rule(r'(.*?) is (.*?)')
@sopel.module.rule(r'(.*?) are (.*?)')
def set_factoid_priv(bot, trigger):
    if not re.match(r"{}\b".format(bot.nick), trigger):
        return set_factoid(bot, trigger)
