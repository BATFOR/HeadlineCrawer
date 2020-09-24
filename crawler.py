from selenium import webdriver
import selenium
import time
import requests
from urllib.parse import urlencode
import pandas as pd
from tqdm import *

header={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'x-requested-with':'XMLHttpRequest'
}

article_dic_titel_url = {}
def get_data(search_name,offset):
    data = {    #构造请求的data
        'aid':'24',
        'app_name':'web_search',
        'offset':offset,
        'format':'json',
        'keyword':search_name,
        'autoload':'true',
        'count':'20',
        'en_qc':'1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd':'synthesis',
        'timestamp': int(time.time()),
        '_signature': '21oMXgAgEBAwjHnl59qFgNtbTUAAIWq5yRBJSZ83MdD56bgu5GDIJxHd0EHk8Y1-DDSzzYJ-ZlFlc5td8NE86Wb3wfbOIt2i-9L7pr2I3.bmY8SCimmZOjMIL2g7TKFO-Lj'
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    res = requests.get(url=url,headers=header)
    return res

def parse_article_list(search_name,offset):
    dic = get_data(search_name,offset).json() #转化为json字典
    data = dic['data']
    if data is not None:    #不为空才开始
        for item in data:
            if ("video_duration_str"not in item and "has_video" not in item) or item["has_video"] == False:  #不需要视频文章，视频没有文字
                if 'title' in item: #标题
                    if 'article_url' in item:  # 文章url
                            article_dic_titel_url[item['title']] = item['article_url']

def parse_article(article_url:str, browser):
    title = ""
    author=""
    release_time=""
    content=""
    if "toutiao.com" in article_url:  #头条站点内的文章
        # article_url = article_url_convert(article_url)
        browser.get(article_url)  # Load page
        time.sleep(0.2)  # Let the page load, will be added to the API
        try:
            title = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/h1").text
        except selenium.common.exceptions.NoSuchElementException:
            title = ""

        try:
            release_time = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[1]/span[3]").text
            author = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[1]/span[2]").text
        except selenium.common.exceptions.NoSuchElementException:
            try:
                release_time = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[1]/span[2]").text
                author = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[1]/span[1]").text
            except selenium.common.exceptions.NoSuchElementException:
                release_time = ""
                author = ""

        try:
            content = browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/article").text
        except selenium.common.exceptions.NoSuchElementException:
            content = ""

        # https: // www.toutiao.com / a6794358241716339211 /
    else:
        None
    return article_url, title, author, release_time, content

def main(keyword):
    #获取相关文章url链接
    print("\n↓↓↓↓↓↓↓↓↓爬取文章url↓↓↓↓↓↓↓↓↓\n")
    if len(article_dic_titel_url) == 0:
        offset = 0
        for i in tqdm(range(11)):   #首页列表中只有98条（只包括文章），包含视频有180条
            parse_article_list(keyword, offset)
            offset = offset + 20

    browser = webdriver.Chrome()  # Get local session of Chrome
    all_data = {}
    all_data["url"] = []
    all_data["title"] = []
    all_data["author"] = []
    all_data["release_time"] = []
    all_data["content"] = []
    print("\n↓↓↓↓↓↓↓↓↓爬取文章详情↓↓↓↓↓↓↓↓↓\n")
    count = 0
    for t, url in tqdm(article_dic_titel_url.items()):  #解析所有文章
        article_url, title, author, release_time, content = parse_article(url, browser)
        all_data["url"].append(article_url)
        all_data["title"].append(title)
        all_data["author"].append(author)
        all_data["release_time"].append(release_time)
        all_data["content"].append(content)
        if content != "":
            count += 1
    df = pd.DataFrame(all_data)
    df.to_csv("spider_data/"+keyword+"_"+str(count)+"条_articles_info_"+str(time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()))+".csv")
    browser.close()
if __name__ == "__main__":
    main("无人船")
