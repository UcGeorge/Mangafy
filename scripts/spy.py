from bs4 import BeautifulSoup as soup
import requests as req
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.callbackquery import CallbackQuery
import mysql.connector
import datetime
import logging
import time
import sys
import json
import telegram
from telegram.parsemode import ParseMode

config = json.loads(open('config-sample.json'))

mydb = mysql.connector.connect(
    host=config['db']['host'],
    user=config['db']['user'],
    password=config['db']['password'],
    database=config['db']['database']
)

mycursor = mydb.cursor(buffered=True)

bot = telegram.Bot(token=config['token'])


def get_all_manga():

    mycursor = mydb.cursor()

    all_manga = {}

    mycursor.execute("SELECT DISTINCT manga, last_chapter FROM manga")
    myresult = mycursor.fetchall()

    for row in myresult:

        manga = {}
        last_chapter = None
        manga_name = None
        manga_link = None

        for column in row:
            try:
                manga = json.loads(column.replace("'", '"'))
            except json.decoder.JSONDecodeError:
                last_chapter = column

        for x in manga:
            manga_name = x
            manga_link = manga[manga_name]

        all_manga[manga_name] = {}
        all_manga[manga_name]['link'] = manga_link
        all_manga[manga_name]['last_chapter'] = last_chapter

    bot.send_message(chat_id=config['admin'], disable_notification=False,
                     text='There are {} mangas to check.'.format(mycursor.rowcount))

    return all_manga


def update_chapter(new_chapter, manga_name):

    mycursor = mydb.cursor(buffered=True)

    manga = "%{}%".format(manga_name)
    args = (new_chapter, str(datetime.datetime.now()), manga)

    mycursor.execute(
        "UPDATE manga SET last_chapter = %s, date_modified = %s WHERE manga LIKE %s", args)
    mydb.commit()

    bot.send_message(chat_id=config['admin'], disable_notification=False,
                     text='{} has just been updated.'.format(manga_name))


def get_interested_users(manga_name):

    mycursor = mydb.cursor(buffered=True)

    print("Getting interested users for {}".format(manga_name))

    manga = "%{}%".format(manga_name)
    args = (manga,)

    mycursor.execute("SELECT user FROM manga WHERE manga LIKE %s", args)
    myresult = mycursor.fetchall()
    data = myresult

    print(data)

    bot.send_message(chat_id=config['admin'], disable_notification=False,
                     text='There are {} users interested in {}.'.format(mycursor.rowcount, manga_name))

    return data


def send_notification(user_id, message, link):

    keyboard = [[InlineKeyboardButton(
        "Menu", callback_data='show_menu'), InlineKeyboardButton("READ", url=link)]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=user_id, parse_mode=ParseMode.HTML,
                     disable_notification=False, text=message, reply_markup=reply_markup)


def get_last_chapter(manga_name):

    mycursor = mydb.cursor(buffered=True)

    manga = "%{}%".format(manga_name)
    args = (manga,)

    mycursor.execute(
        "SELECT DISTINCT last_chapter FROM manga WHERE manga LIKE %s", args)
    myresult = mycursor.fetchone()
    data = myresult[0] if myresult != None else None

    return data


def get_manga_to_spy():

    spy_list = {}

    all_manga = get_all_manga()

    print("All manga: {} \n\n".format(str(all_manga).replace(', ', '\n')))

    for manga in all_manga:

        manga_name = None
        manga_link = None

        manga_name = manga
        manga_link = all_manga[manga]['link']
        last_chapter = all_manga[manga]['last_chapter']

        spy_list[manga_name] = {
            "link": manga_link, "last_chapter": last_chapter}

    return spy_list


def get_manga_data(manga_link):

    uClient = req.get(manga_link)
    client_html = uClient.text
    client_soup = soup(client_html, 'lxml')

    homepage_item = client_soup.find("li", {"class": "a-h"})

    new_chapter = homepage_item.a.text
    new_chapter_link = homepage_item.a['href']

    return {'last_chapter': new_chapter, 'link': new_chapter_link}


def spy_report(spy_list):

    spy_report_list = {}

    print("Spy list: {}".format(str(spy_list).replace('}, ', '}\n\n')))

    for item in spy_list:

        print("\nMaking report for {}\n at {}\n".format(
            item, spy_list[item]['link']))

        manga_name = None
        manga_link = None
        last_chapter = None
        new_chapter = None
        new_chapter_link = None

        manga_name = item
        manga_link = spy_list[item]["link"]
        last_chapter = spy_list[item]["last_chapter"]

        uClient = req.get(manga_link)
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')

        homepage_item = client_soup.find("li", {"class": "a-h"})

        new_chapter = homepage_item.a.text
        new_chapter_link = homepage_item.a['href']

        if last_chapter == new_chapter:
            print("{} has not been updated".format(manga_name))
            continue

        print("{} has been updated".format(manga_name))

        spy_report_list[manga_name] = {
            "link": new_chapter_link, "last_chapter": new_chapter}

    print("\nSpy report: {}\n".format(spy_report_list))

    if spy_report_list == {}:
        bot.send_message(
            chat_id=config['admin'], disable_notification=False, text='No manga was updated.')

    return spy_report_list


def notification_report(spy_report):

    notification_list = {}

    for item in spy_report:

        print("\nFocus: {}\n".format(item))

        interested_users = []
        manga_name = item
        manga_link = spy_report[item]["link"]
        last_chapter = spy_report[item]["last_chapter"]

        temp = get_interested_users(item)

        print("Interested users: ", temp)

        for user in temp:
            print("\nContacting: {}\n".format(user))
            interested_users.append(user[0])

        notification_list[manga_name] = {
            "link": manga_link, "last_chapter": last_chapter, "interested_users": interested_users}

    print("\nNotification list: {}\n".format(notification_list))

    return notification_list


def notify_users(notification_list):

    for item in notification_list:

        print("\nFocus: {}\n".format(item))

        manga_name = item
        manga_link = notification_list[item]["link"]
        last_chapter = notification_list[item]["last_chapter"]

        message = "🔔🔔🔔\n\n<b>{}</b> has been updated to \n{}!!\n\n👉<a href = '{}'>READ</a>👈".format(
            manga_name, last_chapter, manga_link)

        interested_users = notification_list[item]["interested_users"]

        update_chapter(last_chapter, manga_name)

        for user in interested_users:

            print("\nNotifying: {}\n".format(user))

            send_notification(user, message, manga_link)


if __name__ == "__main__":

    start = time.time()
    bot.send_message(chat_id=config['admin'], parse_mode=ParseMode.HTML, disable_notification=False,
                     text='Mangafy is checking for updates at {}'.format(datetime.datetime.now()))
    notify_users(notification_report(spy_report(get_manga_to_spy())))
    bot.send_message(chat_id=config['admin'], parse_mode=ParseMode.HTML, disable_notification=False,
                     text='Mangafy took {} seconds to check for updates.'.format(int(time.time() - start)))
