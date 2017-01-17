#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

import re
import twitter
import giphypop
from telegram import InlineQueryResultArticle,InlineQueryResultGif,ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from random import randint
from settings import *
import logging


g = giphypop.Giphy()
api = twitter.Api(consumer_key=my_consumer_key,consumer_secret=my_consumer_secret,access_token_key=my_access_token_key,access_token_secret=my_access_token_secret)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('ALL MIGHTY TINY HANDS BOT!')

lyrics =[
"Help, I need somebody",
"Help, not just anybody",
"Help, you know I need someone, help",
"When I was younger, so much younger than today",
"I never needed anybody's help in any way",
"But now these days are gone, I'm not so self assured",
"Now I find I've changed my mind and opened up the doors",
"Help me if you can, I'm feeling down",
"And I do appreciate you being round",
"Help me, get my feet back on the ground",
"Won't you please, please help me",
"And now my life has changed in oh so many ways",
"My independence seems to vanish in the haze",
"But every now and then I feel so insecure",
"I know that I just need you like I've never done before",
"Help me if you can, I'm feeling down",
"And I do appreciate you being round",
"Help me, get my feet back on the ground",
"Won't you please, please help me",
"When I was younger, so much younger than today",
"I never needed anybody's help in any way",
"But now these days are gone, I'm not so self assured",
"Now I find I've changed my mind and opened up the doors",
"Help me if you can, I'm feeling down",
"And I do appreciate you being round",
"Help me, get my feet back on the ground",
"Won't you please, please help me, help me, help me, oh"]
count = 0
def help(bot, update):
    global count 
    update.message.reply_text(lyrics[count])
    count=count+1
    if count > len(lyrics):
        count = 0
        

def trump(bot, update):
    statuses = api.GetUserTimeline(screen_name="realDonaldTrump",count=100)
    int = randint(0,99)
    update.message.reply_text(statuses[int].text)
    gif=g.random_gif("trump")
    update.message.reply_document(gif.media_url,quote=False)
    

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    results.append(InlineQueryResultGif(id=uuid4(),gif_url="https://media.giphy.com/media/oxsfuzJuJzCjm/giphy.gif",thumb_url="https://media4.giphy.com/media/oxsfuzJuJzCjm/200_s.gif#24",title="trump"))

    update.inline_query.answer(results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("trump", trump))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()