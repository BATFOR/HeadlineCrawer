import time
import json
import requests
from urllib.parse import urlencode
from tqdm import *
from bs4 import BeautifulSoup

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

def parse_article_list(search_name,page):
    dic = get_data(search_name,page).json() #转化为json字典
    data = dic['data']
    if data is not None:    #不为空才开始
        for item in data:
            if ("video_duration_str"not in item and "has_video" not in item) or item["has_video"] == False:  #不需要视频文章，视频没有文字
                if 'title' in item: #标题
                    if 'article_url' in item:  # 文章url
                            article_dic_titel_url[item['title']] = item['article_url']

def article_url_convert(article_url):
    # http://toutiao.com/group/6519751747085271566/ -> http://toutiao.com/a6519751747085271566/
    if "toutiao.com/group" in article_url:
        url_split = article_url.split("/")
        return "https://www.toutiao.com/a" + url_split[-2] + "/"
    return article_url

def parse_article(article_url):
    if "toutiao.com" in article_url:  #头条站点内的文章
        article_url = article_url_convert(article_url)
        print(article_url)
        res = requests.get(url=article_url,headers=header)
        print(res.text)
        soup = BeautifulSoup(res.text, 'lxml')   #返回内容为js代码， 抽取script中的数据
        js_script_string = soup.select_one("body > script:nth-of-type(3)").string
        base_data_string = js_script_string.split("=")[1][:-1]
        base_data_dic = json.loads(base_data_string)
        print(base_data_dic)
        # print(title)
        # print(release_author)
        # print(release_time)
        # print(article_string)

# offset = 0
# for i in tqdm(range(10)):   #首页列表中只有98条（只包括文章），包含视频有180条
#     parse_article_list('无人艇', offset)
#     offset = offset + 20
# print(len(article_dic_titel_url))
# print(article_dic_titel_url)
parse_article("https://www.toutiao.com/i6616645307906130435/")

