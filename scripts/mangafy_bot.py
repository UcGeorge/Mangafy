from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.callbackquery import CallbackQuery
from telegram.parsemode import ParseMode
from mangafy_user import User, Manga
from telegram.message import Message
from telegram.update import Update
import mangafy_storage as store
import scrapper as fy
import datetime
import logging
import time
import sys
import spy
import json
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = json.loads(open('config-sample.json'))

updater = Updater(
    config['token'], use_context=True)
dispatcher = updater.dispatcher

active_users = {}

start_message = config['messages']['start_message']
after_exit_message = config['messages']['after_exit_message']
channel_message = config['messages']['channel_message']
discussion_message = config['messages']['discussion_message']
underdev_message = config['messages']['underdev_message']
invalid_message = config['messages']['invalid_message']
empty_message = config['messages']['empty_message']
error_message = config['messages']['error_message']


def echo(update, context):

    if not update.effective_chat.id in active_users:
        user = User(update.effective_chat.id)
        active_users[user.user_id] = user

    if active_users[update.effective_chat.id].is_searching == False:
        context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                                 text=error_message, reply_markup=bot_menu(update, context))
        return

    active_users[update.effective_chat.id].is_searching = False
    manga(update, context, update.message.text.replace(' ', '_').lower())


def start(update, context):

    user = User(update.effective_chat.id)
    active_users[user.user_id] = user

    message = start_message
    keyboard = [[
        InlineKeyboardButton("Add Manga", callback_data='add_manga'),
        InlineKeyboardButton("Bot Menu", callback_data='bot_menu')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                             text=message + channel_message + discussion_message, reply_markup=reply_markup)


def add_manga(update, context):
    keyboard = [
        [InlineKeyboardButton("Latest Manga", callback_data='latest_manga'),
         InlineKeyboardButton("Newest Manga", callback_data='newest_manga')],
        [InlineKeyboardButton("Hottest Manga", callback_data='hot_manga'),
            InlineKeyboardButton("Search Manga", callback_data='search')],
        [InlineKeyboardButton("Exit", callback_data='exit')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
    #context.bot.send_message(chat_id=update.effective_chat.id, parse_mode= ParseMode.HTML, text = message, reply_markup=reply_markup)


def manga(update, context, genre):

    if not update.effective_chat.id in active_users:
        user = User(update.effective_chat.id)
        active_users[user.user_id] = user

    context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="upload_document")

    manga_list = fy.fetch_manga(genre)

    for x in manga_list[:10]:
        manga = Manga(active_users[update.effective_chat.id], x, context)
        active_users[update.effective_chat.id].add_to_top_ten(manga)

    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                             text="More Manga at <a href = 'https://manganelo.com'>Manganelo</a>", reply_markup=add_manga(update, context))


def under_dev(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                             text=underdev_message + channel_message + discussion_message, reply_markup=bot_menu(update, context))


def search(update, context, query):

    keyboard = [[InlineKeyboardButton("Exit", callback_data='exit')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(parse_mode=ParseMode.HTML, text="Enter a manga to search at <a href = 'https://manganelo.com'>Manganelo</a>",
                            disable_web_page_preview=True, reply_markup=reply_markup)
    if not update.effective_chat.id in active_users:
        user = User(update.effective_chat.id)
        active_users[user.user_id] = user

    active_users[update.effective_chat.id].is_searching = True


def view_mangas(update, context, query):

    if not update.effective_chat.id in active_users:
        user = User(update.effective_chat.id)
        active_users[user.user_id] = user

    alert_list = active_users[update.effective_chat.id].get_alert_list()

    if alert_list == {}:
        context.bot.send_message(chat_id=update.effective_chat.id, text="View Manga Error:\n"+empty_message +
                                 channel_message + discussion_message, parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))
        return

    context.bot.send_message(
        chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML, text="Your manga")

    manga_list = fy.show_updates(alert_list)

    for x in manga_list:

        alert_item_as_message = x["name"] + "\n" + x["link"] + \
            "\n\n👉 <a href = '{}'> Read {} now at manganelo.com</a>".format(
                x["latest_chapter_link"], x["latest_chapter"])

        keyboard = [
            [InlineKeyboardButton("Remove", callback_data='remove_{}'.format(x["name"])),
             InlineKeyboardButton("Read", url=x["link"])]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                                 text=alert_item_as_message, reply_markup=reply_markup)

    context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                             text=channel_message + discussion_message, reply_markup=bot_menu(update, context))


def bot_menu(update, context):
    keyboard = [[InlineKeyboardButton("Add Manga", callback_data='add_manga'), InlineKeyboardButton(
        "View mangas", callback_data='view_mangas')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def button(update, context):

    query: CallbackQuery = update.callback_query
    query.answer()
    data = query.data
    if data == 'add_manga':
        query.edit_message_text(text="Add a manga" + channel_message + discussion_message,
                                parse_mode=ParseMode.HTML, reply_markup=add_manga(update, context))
    elif data == 'bot_menu':
        query.edit_message_text(text="Menu" + channel_message + discussion_message,
                                parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))
    elif data == 'view_mangas':
        view_mangas(update, context, query)
    elif data == 'exit':
        if not update.effective_chat.id in active_users:
            user = User(update.effective_chat.id)
            active_users[user.user_id] = user
        active_users[update.effective_chat.id].is_searching = False
        query.edit_message_text(text="Menu" + channel_message + discussion_message,
                                parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))
    elif data == 'latest_manga':
        manga(update, context, 'latest')
    elif data == 'newest_manga':
        manga(update, context, 'newest')
    elif data == 'hot_manga':
        manga(update, context, 'hot')
    elif data == 'search':
        search(update, context, query)
    elif data == 'show_menu':
        context.bot.send_message(chat_id=update.effective_chat.id, text="Menu" + channel_message +
                                 discussion_message, parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))
    elif "add_" in data:
        if not update.effective_chat.id in active_users:
            user = User(update.effective_chat.id)
            active_users[user.user_id] = user
        manga_name = data[4:]
        top_ten = active_users[update.effective_chat.id].get_top_ten()
        if manga_name in top_ten:
            top_ten[manga_name].add_me(
                active_users[update.effective_chat.id], query)
        else:
            query.edit_message_text(
                text="Oops!\nThis function is invalid or has expired.", parse_mode=ParseMode.HTML)
    elif "remove_" in data:
        if not update.effective_chat.id in active_users:
            user = User(update.effective_chat.id)
            active_users[user.user_id] = user
        manga_name = data[7:]
        store.delete_manga(manga_name, update.effective_chat.id)
        query.edit_message_text(
            text="This manga has been removed from your alerts list.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, parse_mode=ParseMode.HTML,
                                 text=invalid_message, reply_markup=bot_menu(update, context))


def error_callback(update, context):

    context.bot.send_message(chat_id=config['admin'], disable_notification=False,
                             text='An error occoured\n{}'.format(str(context.error)))

    try:
        raise context.error
    except Unauthorized:
        print("An unauthorized error occoured")
    except BadRequest:
        print("A bad request error occoured")
        context.bot.send_message(chat_id=update.effective_chat.id, text="An error occoured!\nPlease try again later!" +
                                 channel_message + discussion_message, parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))
    except TimedOut:
        print("A timeout error occoured")
    except NetworkError:
        print("A network error occoured")
    except ChatMigrated as e:
        print(e)
    except TelegramError:
        print("A telegram error occoured")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Menu" + channel_message +
                                 discussion_message, parse_mode=ParseMode.HTML, reply_markup=bot_menu(update, context))


dispatcher.add_error_handler(error_callback)

button_handler = CallbackQueryHandler(button)
dispatcher.add_handler(button_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
updater.idle()
