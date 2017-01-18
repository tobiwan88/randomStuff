#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from uuid import uuid4

import re
import twitter
import giphypop
from telegram import InlineQueryResultArticle,InlineQueryResultGif,ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from random import randint
from settings import *
import sqlite3
import logging

def isfloat(value):
  try:
    float(value)
    return True
  except:
    return False

g = giphypop.Giphy()
api = twitter.Api(consumer_key=my_consumer_key,consumer_secret=my_consumer_secret,access_token_key=my_access_token_key,access_token_secret=my_access_token_secret)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getPledges(conn,tablename):
    c = conn.cursor()
    c.execute("SELECT * FROM '{}';".format(tablename))
    return c.fetchall()

def createPledgetable(conn,tablename):
    c = conn.cursor()
    c.execute("CREATE TABLE '{}' (userid INT PRIMARY KEY, pledged NUMERIC, name TEXT)".format(tablename))
    conn.commit()       

def checkOrCreatePledgeTable(conn,tablename):
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(tablename))
    if c.fetchone() is None:
        createPledgetable(conn,tablename)
        
def addMoney(conn,tablename,user,money,name):
    c = conn.cursor()
    c.execute("INSERT INTO '{}' VALUES ('{}','{}','{}');".format(tablename,user,money,name))
    conn.commit()

def getMoney(conn,tablename,user):
    c = conn.cursor()
    c.execute("SELECT pledged FROM '{}' WHERE userid={};".format(tablename,user))
    return c.fetchone()
    
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Birthday bot started, you can pledge money with /pledge and see pledges with /pledges')
    
def help(bot, update):
    update.message.reply_text("help text")
        
def checkpledges(bot,update):
    conn = sqlite3.connect("birthday.db")
    chatTable="id{}".format(update.message.chat.id)
    pledges = getPledges(conn,chatTable)
    conn.close()
    total=0
    reply=""
    for pledge in pledges:
        reply+="\n"
        reply+="{} pledged {} €".format(pledge[2],pledge[1])
        total=total + pledge[1]
    reply+="\nTotally pledged {}".format(total)
    update.message.reply_text(reply)
    
def pledge(bot, update):
    conn = sqlite3.connect("birthday.db")
    pledged = 0
    amount = update.message.text.split()[1];
    if isfloat(amount):
        pledged = float(amount)
    elif isfloat(amount[:-1]):
        pledged = float(amount[:-1])
        
    chatTable="id{}".format(update.message.chat.id)
    checkOrCreatePledgeTable(conn,chatTable)
    
    previouspledged=getMoney(conn,chatTable,update.message.from_user.id)
    username=update.message.from_user.username
    if len(username) == 0:
        username ="{} {}".format(update.message.from_user.first_name,update.message.from_user.last_name)
        
    if previouspledged is None:
        addMoney(conn,chatTable,update.message.from_user.id,pledged,username)
        conn.close()
    else:
        teststring = '{} {}  from chat{} pledged already {} Euro'.format(update.message.from_user.first_name,update.message.from_user.last_name,update.message.chat.title,previouspledged[0])
        update.message.reply_text(teststring)
        conn.close()
        return
    #commit
    teststring = '{} {}  from chat{} pledged {} Euro'.format(update.message.from_user.first_name,update.message.from_user.last_name,update.message.chat.title,pledged)
    #chat_id
    update.message.reply_text(teststring)
  
def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()
    gifs=g.search("birthday")
    for gif in gifs:
        results.append(InlineQueryResultGif(id=uuid4(),gif_url=gif.media_url,thumb_url=gif.fixed_height.downsampled.url,title="Birthday"))
        
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
    dp.add_handler(CommandHandler("pledge", pledge))
    dp.add_handler(CommandHandler("pledges", checkpledges))
    
    
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