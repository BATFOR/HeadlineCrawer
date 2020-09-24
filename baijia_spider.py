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
    response = get_data(key_word,pn)
    soup = BeautifulSoup(response.text, 'lxml')
    a = soup.select_one("#\34 1 > div > h3 > a")
    print(a)





def parse_article(article_url):
    None

# offset = 0
# for i in tqdm(range(10)):   #首页列表中只有98条（只包括文章），包含视频有180条
#     parse_article_list('无人艇', offset)
#     offset = offset + 20
# print(len(article_dic_titel_url))
# print(article_dic_titel_url)
parse_article_list("无人艇",10)

