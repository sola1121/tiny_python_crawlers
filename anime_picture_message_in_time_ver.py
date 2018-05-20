# coding: utf8

import os
import time
import math
import random
import requests

from bs4 import BeautifulSoup
from multiprocessing import Process, Pool, Value, SimpleQueue

POOL_NUM = math.ceil(os.cpu_count()/3*2)
ROOT = os.getcwd()
DESKTOP = os.environ['HOME'] + "\\Desktop\\"
NEW_DIR = "animeylon.pl_%d"

HEAD = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"}
HTML_PAGE = "http://animenylon.pl/page/%d/"


class ImageToSave:

    def __init__(self, link):
        self.link = link
        self.image_name = self._get_name(link)
        self.image_content = self._get_content(link)

    def __repr__(self):
        return "<ImageSave object at %s>" % str(id())

    def _get_name(self, link):
        return str(link).split("/")[-1].strip()

    def _get_content(self, link):
        res = link_html(link)
        return res.content

    def save(self, directory):
        if self.image_content is None:
            raise ValueError("None content.")
        if not os.path.exists(directory):
            os.makedirs(directory)
        image_route = directory + self.image_name
        with open(image_route, 'wb') as file:
            file.write(self.image_content)


def link_html(link):
    count = 1
    while True:
        try:
            res = requests.get(link, headers=HEAD, timeout=20)
            if res.status_code != 200:
                raise Exception("Failed Link %s" % link)
            return res
        except Exception as e:
            print(e)
            if count < 4:
                print("Relink.%d.." % count, link)
                count += 1
                time.sleep(random.randint(1, 4))
                continue
            else:
                print("Failed Link, End Relink")
                error_log(link)
                return


def get_image_page(page_url):
    result_lists = list()
    res = link_html(page_url)
    if res is None:
        raise Exception("get image page Error")
    soup = BeautifulSoup(res.text, 'lxml')
    source_lists = soup.find_all("div", class_="post-container")
    for source in source_lists:
        result_lists.append(source.div.a['href'])
    return result_lists


def get_image_link(page_url):
    res = link_html(page_url)
    if res is None:
        raise Exception("get image link Error")
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        detail_link = soup.find("div", class_="post-content").p.a['href']
    except:
        try:
            detail_link = soup.find("video").a['href']
        except:
            print("Hint !!!: An ignored image link. %s" % page_url)
            detail_link = None
    return detail_link


def create_image(que, directory, COUNTER):
    COUNTER.value += 1
    image_link = que.get()
    print("Image %s:" % COUNTER.value, image_link)
    image = ImageToSave(image_link)
    image.save(directory)


def error_log(link):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
    with open("error_log.txt", 'w+') as er_log:
        er_log.write(time_str + "Failed Link To: " + link + "\n")


if __name__ == "__main__":

    COUNTER = Value('i', 0)

    while True:
        HTML_NUM = int(input("\nanimenylon_pl page number: "))
        if HTML_NUM <= 0:
            break
        start_time = time.time()
        directory = DESKTOP + "dev1_animenylon_pl0%d\\"%HTML_NUM

        lst = list()
        process_list = list()
        que = SimpleQueue()
        pool = Pool(processes=POOL_NUM)

        page_lst = get_image_page(HTML_PAGE%HTML_NUM)
        page_num = len(page_lst)
        print("Get image page %d, analyzing..." % page_num)

        for url in page_lst:
            res = pool.apply_async(get_image_link, (url,))
            res.wait()
            image_url = res.get()
            if image_url is None:
                continue
            que.put(image_url)
            pro = Process(target=create_image, args=(que, directory, COUNTER))
            process_list.append(pro)
            pro.start()
        
        pool.close()
        pool.join()

        for pro in process_list:
            pro.join()
        
        print("\nUse %8s .  Total %d .  AT %s  .\a\a" % (time.time()-start_time, COUNTER.value, directory))
        if page_num != COUNTER.value:
            print("Warning: Not each page's image had got. %s\a\a" % (HTML_PAGE % HTML_NUM))
        COUNTER.value = 0
