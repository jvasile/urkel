import sopel.module

@sopel.module.commands('urkel')
def urkel(bot, trigger):
    bot.say('Did I do that?!')
