#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import urllib.parse as urlparse
from urllib.parse import parse_qs
import re
import subprocess
import os
import errno
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

## Parameters
bot_token = ""

## Configuration
output_format = ".mp4"
ffmpeg_bin = "ffmpeg"
folder = "./videos/"
loglevel = logging.INFO
#loglevel = logging.DEBUG

logging.basicConfig(filename='youtubetrimmer_bot.log',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=loglevel)
logger = logging.getLogger(__name__)

try:
    os.mkdir(folder)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

def YoutubeTrimmer(text,context):
    url=re.search("(?P<url>https?://[^\s]+)", text).group("url")
    parsed = urlparse.urlparse(url)
    website=parsed.netloc
    information=parsed.query

    if website == "youtu.be":
        idvideo=parsed.path[1:]
        start=parse_qs(parsed.query)['start'][0]
        finish=parse_qs(information)['end'][0]
    elif "youtubetrimmer" or "youtube" in website:
        idvideo=parse_qs(information)['v'][0]
        start=parse_qs(parsed.query)['start'][0]
        finish=parse_qs(information)['end'][0]
    else:
        text.message.reply_text("Unknown: "+website)

    video_path=folder+idvideo+output_format
    download_command=ffmpeg_bin+" -y -ss "+start+" -i $(youtube-dl -f best -g 'https://www.youtube.com/watch?v="+idvideo+"') -t "+finish+" "+video_path
    print ("WEBSITE: "+website+", idvideo: "+idvideo+", start: "+start+", finish: "+finish)
    logger.info('WEBSITE: "%s", idvideo: "%s", start: "%s", finish: "%s"', website, idvideo, start, finish)
    logger.debug(subprocess.run(download_command, shell=True,capture_output=True))
    return video_path

def start(update, context):
    update.message.reply_text("Hello!\nWelcome to YoutubeTrimmer.com Telegram bot\n")
    update.message.reply_photo(photo=open("start.png","rb"),caption="To use this bot, first go to YoutubeTrimmer.com, insert your youtube URL and set the start and the end of the video that you want to get. Copy the url")
    update.message.reply_text("Then send with /cut command the url you have just copied and add comments and tags (if you want). Here is an example")
    update.message.reply_photo(photo=open("start2.png","rb"),caption="/cut https://www.youtubetrimmer.com/view/?v=qU1qy9831nw&start=56&end=118 best #solo part")
    

def help(update, context):
    update.message.reply_text('Type /start to know how to use this bot\nType /cut and add a YoutubeTrimmer URL\nUsage example:\n/cut https://www.youtubetrimmer.com/view/?v=qU1qy9831nw&start=56&end=118 best #solo part')

def echo(update, context):
    update.message.reply_text('Usage example:\n/cut https://www.youtubetrimmer.com/view/?v=qU1qy9831nw&start=56&end=118 best #solo part')

def cut(update, context):
    downloaded_video=YoutubeTrimmer(update.message.text,context)
    update.message.reply_video(video=open(downloaded_video,"rb"),caption=str(update.message.text[4:]),supports_streaming=True)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("cut", cut))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
