import mangafy_storage as store
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.parsemode import ParseMode

temp_manga_sample = {
    'manga_1_name': 'InstanceOf.Manga',
    'manga_2_name': 'InstanceOf.Manga',
    'manga_3_name': 'InstanceOf.Manga'
}

alert_list_sample = {
    'manga_1_name': 'manga_1_link',
    'manga_2_name': 'manga_2_link',
    'manga_3_name': 'manga_3_link'
}


class User:

    def __init__(self, user_id):
        store.init_user(user_id)

        self.user_id = user_id
        self.top_ten, self.is_searching = {}, False

    def add_to_top_ten(self, manga):

        self.top_ten[manga.manga_name] = manga

    def get_top_ten(self):

        return self.top_ten

    def get_alert_list(self):

        try:
            alert_list = {}

            data = store.get_alert_list(self.user_id)

            if data == 'None':
                return alert_list

            temp = data.replace("'", '"')
            temp = temp.replace('("', ' ')
            temp = temp.replace('",)', ' ')

            x = json.loads(temp)

            for y in x:
                for z in y:
                    alert_list[z] = y[z]

            return alert_list
        except:
            print('An error occoured')

    def add_manga(self, manga):

        print(manga)

        manga_final = {manga["Name"]: manga["Link"]}

        store.edit_manga(manga_final, self.user_id, manga["Latest_chapter"])


class Manga:

    def __init__(self, user, manga, context):

        self.manga_name = manga["Name"]
        self.manga_link = manga["Link"]
        self.latest_chapter = manga["Latest_chapter"]

        if(self.manga_name in user.get_alert_list()):

            message = "<b>"+self.manga_name+"</b>\n\n" + self.manga_link + \
                "\nHas already been added to your alerts list"

            keyboard = [[InlineKeyboardButton(
                "REMOVE", callback_data='remove_' + self.manga_name)]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            context.bot.send_message(
                chat_id=user.user_id, parse_mode=ParseMode.HTML, text=message, reply_markup=reply_markup)

        else:

            alert_item_as_message = "<b>"+self.manga_name + "</b>\n\n" + \
                self.manga_link + "\n\n" + self.latest_chapter

            keyboard = [[InlineKeyboardButton(
                "ADD", callback_data='add_' + self.manga_name)]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            context.bot.send_message(chat_id=user.user_id, parse_mode=ParseMode.HTML,
                                     text=alert_item_as_message, reply_markup=reply_markup)

    def add_me(self, user, query):

        manga = {
            "Name": self.manga_name,
            "Link": self.manga_link,
            "Latest_chapter": self.latest_chapter
        }

        user.add_manga(manga)

        message = "<b>" + self.manga_name+"</b>\n\n" + \
            self.manga_link + "\nHas been added to your alerts list"
        query.edit_message_text(parse_mode=ParseMode.HTML, text=message)
