import time
import requests
from urllib.parse import urlencode
from tqdm import *
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
import traceback

PATT_PARSE_IMG=re.compile(r'<img.+?(src=".*?").*?>')  #提取html中文本和图片地址
PATT_REMOVE_HTML_PART_TAG = re.compile(r'(?!<img)(?P<ss><\w+[^>]*>|</[a-z\d-]*>)',re.S)   #查找html标签（除img外）用字符串""替换
IMG_DIR_PATH = "E:/PythonWorkSpace/HeadlineCrawler/spider_data/bai_jia/img/"
Temp_Img_names = []   #["xxxx.png","",...]
header={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'x-requested-with':'XMLHttpRequest'
}
all_aritcle_urls = set()   #存放每次爬取的文章url
def download_img(img_url, img_to_save_url):
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        try:
            open(img_to_save_url, 'wb').write(r.content)  # 将内容写入图片
            return True
        except Exception as e:
            print("图片保存失败！ " + str(e))
            return False
        finally:
            del r
    return False

#re.sub(...)函数的回调函数
def replacement(match):
    sentence = match.group(1)
    if sentence.startswith("src"):
        url = sentence[5:-1]  # 获取url
        url = url.replace("&amp;", "&")
        # 下载图片到本地
        img_name = str(time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()))
        if download_img(url, IMG_DIR_PATH + img_name + ".png"):
            sentence = "[图片" + "](./img/spider_data/" + img_name + ".png)"
            Temp_Img_names.append(img_name + ".png")
        else:
            sentence = "[图片" + "](" + url + ")"

    return sentence

#文章爬取失败删除图片
def del_imgs():
    for img_name in Temp_Img_names:
        path = IMG_DIR_PATH + img_name
        if os.path.exists(path):
            os.remove(path)

def get_data(key_word,pn):   #pn/10 = 页数
    data = {    #构造请求的data
        "ie": "utf - 8",
        "medium": 2,
        "rtt": 1,
        "bsst": 1,
        "rsv_dl": "news_b_pn",
        "cl": 2,
        "wd": key_word,
        "tn": "news",
        "rsv_bp": 1,
        "rsv_sug3": 6,
        "rsv_sug1": 4,
        "rsv_sug7": 101,
        "oq":"",
        "rsv_btype": "t",
        "f": 8,
        "inputT": 10998,
        "rsv_sug4": 66996,
        "rsv_sug": 9,
        "x_bfe_rqs": "03E80",
        "x_bfe_tjscore": "0.595014",
        "tngroupname": "organic_news",
        "newVideo": 12,
        "pn": pn
    }
    url = 'https://www.baidu.com/s?' + urlencode(data)
    res = requests.get(url=url,headers=header)
    return res

def parse_article_list(key_word,pn):
    """
    将爬取到的文章url保存至全局变量articles_url， 并且返回当次爬取到的url的个数
    :param key_word: 文章关键字
    :param pn: pn/10 等于页数
    :return: 返回当次爬取到的url的个数
    """
    response = get_data(key_word,pn)
    soup = BeautifulSoup(response.text, 'lxml')
    div = soup.select_one("#content_left > div:nth-of-type(2)")
    articles_url = div.find_all(name="a",href = re.compile(r'^https://.+'), class_=re.compile(r'^news-title-.+'))
    for a_tag in articles_url:
        all_aritcle_urls.add(a_tag["href"])
    return len(articles_url)

def parse_article(article_url):
        res = requests.get(url=article_url, headers=header)
        soup = BeautifulSoup(res.text, 'lxml')
        try:
            title = soup.select_one("#detail-page > div.title_border > div > div.article-title > h2").string
        except Exception as e:
            title = ""
            print("------------exception-----------title")

        try:
            author = soup.select_one("#detail-page > div.title_border > div > div.article-desc.clearfix > div.author-txt > p").string
        except Exception as e:
            author = ""
            print("------------exception-----------author")

        try:
            date = soup.select_one("#detail-page > div.title_border > div > div.article-desc.clearfix > div.author-txt > div > span.date").string.split("：")[1].strip()
        except Exception as e:
            date = ""
            print("------------exception-----------date")

        try:
            time = soup.select_one("#detail-page > div.title_border > div > div.article-desc.clearfix > div.author-txt > div > span.time").string
        except Exception as e:
            time = ""
            print("------------exception-----------time")

        try:
            article_content_tag = soup.select_one("#article > div").contents
            article_content = "".join([str(tag) for tag in article_content_tag])
            content_html = re.sub(PATT_REMOVE_HTML_PART_TAG, "", article_content)  # 消除除img以外的标签
            content = re.sub(PATT_PARSE_IMG, replacement, content_html)
        except  Exception as e:
            content = ""
            print("------------exception-----------content")

        return title, author, date+" "+time, content, article_url

def main(key_word):
    Temp_Img_names = []
    #爬取url
    print("\n↓↓↓↓↓↓↓↓↓爬取文章url↓↓↓↓↓↓↓↓↓\n")
    pn = 0
    while True:
        if parse_article_list(key_word, pn) >= 10:
            pn += 10
        else:
            break
    print("---------共爬取--{}--条url----------".format(pn))

    try:
        #解析文章
        all_data = {}
        all_data["url"] = []
        all_data["title"] = []
        all_data["author"] = []
        all_data["release_time"] = []
        all_data["content"] = []
        count = 0
        print("\n↓↓↓↓↓↓↓↓↓爬取文章详情↓↓↓↓↓↓↓↓↓\n")
        for url in tqdm(all_aritcle_urls):
            title, author, date_time, content, article_url = parse_article(url)
            all_data["url"].append(article_url)
            all_data["title"].append(title)
            all_data["author"].append(author)
            all_data["release_time"].append(date_time)
            all_data["content"].append(content)
            if content != "":
                count += 1
        df = pd.DataFrame(all_data)
        df.to_csv("spider_data/bai_jia/" + key_word + "_" + str(count) + "条_articles_info_" + str(
            time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())) + ".csv")
    except Exception as e:
        print("csv保存失败！")
        print(traceback.format_exc())
        del_imgs()

if __name__ == "__main__":
    main("无人驾驶船舶")
    # print(parse_article_list("无人艇", 100))

