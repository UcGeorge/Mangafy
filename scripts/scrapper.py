from bs4 import BeautifulSoup as soup
import requests as req
import json

config = json.loads(open('config-sample.json'))
channel_message = config['messages']['channel_message']
discussion_message = config['messages']['discussion_message']

home_url = config['urls']['home_url']
latest_url = config['urls']['latest_url']
hot_url = config['urls']['hot_url']
newest_url = config['urls']['newest_url']
search_url = config['urls']['search_url']


def parse_name(name):
    print("Parsing {}".format(name))
    name_to_return = name
    allowed_characters = "QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuioplkjhgfdsazxcvbnm-_"
    for x in name_to_return:
        if x in allowed_characters:
            continue
        if x == '&':
            name_to_return = name_to_return.replace(x, 'and')
        name_to_return = name_to_return.replace(x, ' ')
    print("Result: {}".format(name_to_return))
    return name_to_return


def fetch_manga(genre):
    manga_list = []

    if genre == "latest":

        uClient = req.get(latest_url)
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')
        homepage_items = client_soup.findAll(
            "div", {"class": "content-genres-item"})
        print('Found {} manga'.format(len(homepage_items)))
        index = 0

        for homepage_item in homepage_items:
            try:
                manga_name = parse_name(homepage_item.div.h3.a.text)
                latest_chapter_box = homepage_item.find(
                    "a", {"class": "genres-item-chap text-nowrap a-h"})
                if latest_chapter_box == None:
                    latest_chapter = "Unable to fetch latest chapter"
                else:
                    latest_chapter = latest_chapter_box.text
                manga_link = homepage_item.div.h3.a["href"]

                manga_list.append(
                    {"Name": manga_name, "Link": manga_link, "Latest_chapter": latest_chapter})

                index = index + 1
                if index == 10:
                    break
            except UnboundLocalError:
                print("local variable 'index' referenced before assignment")
            except:
                print('An error occoured')

    elif genre == "hot":

        uClient = req.get(hot_url)
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')
        homepage_items = client_soup.findAll(
            "div", {"class": "content-genres-item"})
        print('Found {} manga'.format(len(homepage_items)))
        index = 0

        for homepage_item in homepage_items:
            try:
                manga_name = parse_name(homepage_item.div.h3.a.text)
                latest_chapter_box = homepage_item.find(
                    "a", {"class": "genres-item-chap text-nowrap a-h"})
                if latest_chapter_box == None:
                    latest_chapter = "Unable to fetch latest chapter"
                else:
                    latest_chapter = latest_chapter_box.text
                manga_link = homepage_item.div.h3.a["href"]

                manga_list.append(
                    {"Name": manga_name, "Link": manga_link, "Latest_chapter": latest_chapter})

                index = index + 1
                if index == 10:
                    break
            except UnboundLocalError:
                print("local variable 'index' referenced before assignment")
            except:
                print('An error occoured')

    elif genre == "newest":

        uClient = req.get(newest_url)
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')
        homepage_items = client_soup.findAll(
            "div", {"class": "content-genres-item"})
        print('Found {} manga'.format(len(homepage_items)))
        index = 0

        for homepage_item in homepage_items:
            try:
                manga_name = parse_name(homepage_item.div.h3.a.text)
                latest_chapter_box = homepage_item.find(
                    "a", {"class": "genres-item-chap text-nowrap a-h"})
                if latest_chapter_box == None:
                    latest_chapter = "Unable to fetch latest chapter"
                else:
                    latest_chapter = latest_chapter_box.text
                manga_link = homepage_item.div.h3.a["href"]

                manga_list.append(
                    {"Name": manga_name, "Link": manga_link, "Latest_chapter": latest_chapter})

                index = index + 1
                if index == 10:
                    break
            except UnboundLocalError:
                print("local variable 'index' referenced before assignment")
            except:
                print('An error occoured')

    else:

        uClient = req.get(search_url.format(genre))
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')
        homepage_items = client_soup.findAll(
            "div", {"class": "search-story-item"})

        for homepage_item in homepage_items:
            try:
                manga_name = parse_name(homepage_item.div.h3.a.text)
                latest_chapter_box = homepage_item.find(
                    "a", {"class": "item-chapter a-h text-nowrap"})
                if latest_chapter_box == None:
                    latest_chapter = "Unable to fetch latest chapter"
                else:
                    latest_chapter = latest_chapter_box.text

                manga_link = homepage_item.div.h3.a["href"]

                manga_list.append(
                    {"Name": manga_name, "Link": manga_link, "Latest_chapter": latest_chapter})

                index = index + 1
                if index == 10:
                    break
            except UnboundLocalError:
                print("local variable 'index' referenced before assignment")
            except:
                print('An error occoured')

    return manga_list


def show_updates(alert_list):

    manga_list = []

    for x in alert_list:

        uClient = req.get(alert_list[x])
        client_html = uClient.text
        client_soup = soup(client_html, 'lxml')

        homepage_item = client_soup.find("li", {"class": "a-h"})

        latest_chapter = homepage_item.a.text
        latest_chapter_link = homepage_item.a['href']

        manga_list.append(
            {"name": x, "link": alert_list[x], "latest_chapter": latest_chapter, "latest_chapter_link": latest_chapter_link})

    return manga_list
