import pyperclip
import requests
import random
import time
import os
import re

from bs4 import BeautifulSoup


head = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0"}

h2_title = ""
root = r"C:\Users\Administrator\Desktop\Im"
root2 = r"C:\Users\Administrator\Desktop"

def get_valid_name(name):
    """排除系统不可用字符小工具"""
    name = str(name)
    for invalid_str in ["/", "\\", ":", "*", "\"", "<", ">", "|", "?"]:
        name = str(name).replace(invalid_str, " ")
    return str(name).strip()

def link_to(url):
    count = 1
    while True:
        try:
            res = requests.get(url, headers=head)
            if res.status_code != 200:
                raise Exception("连接地址失败.")
            return res
        except Exception as e:
            print(e)
            if count > 3:
                break
            print("在尝试... %d" %count)
            count += 1
            time.sleep(random.randint(2, 5))

def get_image_spans(res):
    global h2_title
    soup = BeautifulSoup(res.text, 'lxml')
    h2_title = soup.find("h2", id="activity-name", class_="rich_media_title")
    h2_title = str(h2_title.text).encode("utf-8").decode("utf-8")
    span_lst = soup.find_all("span", class_="bannerfix-wrapper")
    if span_lst:
        return span_lst
    else:
        raise Exception("图片列表为空.")

def get_image_links(span_lst):
    image_list = list()
    for span in span_lst:
        if span.img['data-src']:
            image_list.append(span.img['data-src'])
        elif span.img['src']:
            image_list.append(span.img['src'])
        else:
            raise Exception("未找到图片地址.")
    return image_list

def get_name_from_link(url):
    link = str(url)
    name_section1 = (link.split("/0?fmt="))[0]
    name = (name_section1.split("/0-"))[-1]
    suffix_section1 = (link.split("0?fmt="))[1]
    suffix = (suffix_section1.split("&size"))[0]
    file_name = name + "." + suffix
    return file_name

def save_image(url, save_point, file_name):
    directory = (save_point + "\\" + (get_valid_name(str(h2_title))).strip() + "\\")
    if not os.path.exists(directory):
        os.makedirs(directory)
    res = link_to(url)
    with open(directory + file_name, 'wb') as img_file:
        if res.content is None:
            raise Exception("获得图片时出错.")
        img_file.write(res.content)
    return directory

def run_main(main_link):
    res = link_to(main_link)
    span_lst = get_image_spans(res)
    img_lst = get_image_links(span_lst)
    for info in img_lst:
        name = get_name_from_link(info)
        directory = save_image("http:" + info, root, name)

def run_main2(main_link):
    ct = 1
    directory = ""
    res = link_to(main_link)
    span_lst = get_image_spans(res)
    img_lst = get_image_links(span_lst)
    print(h2_title)
    for info in img_lst:
        name = get_name_from_link(info)
        print("Loading... %s   %d" %(name, ct))
        directory = save_image("http:" + info, choice_root(h2_title), name)
        ct += 1
    print(directory, "total: %d" %(ct-1))
    if (ct-1) <=4:
        print("Warning: May don't get all pictures.")

def choice_root(words):
    screen = ("筛选内容")
    for scr in screen:
        if scr in words:
            return root2
    return root


if __name__ == "__main__":
    
    RE_TIME = 0.01
    old_paste = "null_str"

    pyperclip.copy("listening the clipboard...")
    while True:
        link = pyperclip.paste()
        if link != old_paste:
            old_paste = link
            if re.findall(r"^http.*", link):
                run_main2(link)
        time.sleep(RE_TIME)
        

