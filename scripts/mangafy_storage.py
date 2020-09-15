import mysql.connector
import spy
import json

config = json.loads(open('config-sample.json'))

mydb = mysql.connector.connect(
    host=config['db']['host'],
    user=config['db']['user'],
    password=config['db']['password'],
    database=config['db']['database']
)

sql_create_user = "INSERT INTO users (user_id) VALUES(%s)"
sql_delete_user = "DELETE FROM users WHERE user_id =%s"
sql_get_user = "SELECT {} FROM users WHERE user_id =%s"

mycursor = mydb.cursor()


def init_user(user_id):
    if not user_exists(user_id):
        create_user(user_id)


def create_user(user_id):
    args = (user_id,)
    mycursor.execute(sql_create_user, args)
    mydb.commit()


def user_exists(user_id):
    args = (user_id,)
    mycursor.execute(sql_get_user.format('user_id'), args)
    myresult = mycursor.fetchone()
    return myresult != None


def get_alert_list(user_id):
    args = (user_id,)
    mycursor.execute("SELECT manga FROM manga WHERE user =%s", args)
    myresult = mycursor.fetchall()
    return str(myresult)


def edit_manga(value, user_id, latest_chapter):

    name = None
    manga_link = None

    for x in value:
        name = x
        manga_link = value[x]

    if spy.get_last_chapter(name) == latest_chapter:
        args = (str(value), user_id, latest_chapter)
        mycursor.execute(
            "INSERT INTO manga (manga, user, last_chapter) VALUES(%s, %s, %s)", args)
        mydb.commit()
        return

    interested_users = []
    temp = spy.get_interested_users(name)

    for user in temp:
        print("\nContacting: {}\n".format(user))
        interested_users.append(user[0])

    new_data = spy.get_manga_data(manga_link)

    notification_list = {}

    notification_list[name] = {"link": new_data['link'],
                               "last_chapter": new_data['last_chapter'], "interested_users": interested_users}

    spy.notify_users(notification_list)

    spy.update_chapter(new_data['last_chapter'], name)

    args = (str(value), user_id, new_data['last_chapter'])
    mycursor.execute(
        "INSERT INTO manga (manga, user, last_chapter) VALUES(%s, %s, %s)", args)

    mydb.commit()


def delete_manga(name, user_id):
    manga = "%{}%".format(name)
    args = (manga, user_id)

    mycursor.execute(
        "DELETE FROM manga WHERE manga LIKE %s AND user = %s", args)
    mydb.commit()
