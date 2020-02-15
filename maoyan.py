import requests
import re
from requests.exceptions import RequestException
import json
from config import *
import pymongo

client = pymongo.MongoClient(mongo_url)
db = client[mongo_db]

def get_one_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0(Macintosh;Intel Mac OS X 10_14_6)AppleWebKit/537.36(KHTML, like Gecko)Chrome/79.0.3945.130Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?name"><a'
                         + '.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                         + '.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield{
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

    # data = json.loads(item)

# def write_to_file(content):
#     with open('movie_score.txt','a', encoding='utf-8') as f:
#         f.write(json.dumps(content,ensure_ascii=False) + '\n')
#         f.close()
def save_to_mongo(content):
    if db[mongo_table].insert(content):
        print('Successful', content)
        return True
    return False

def main(offset):
    url = 'https://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    for item in parse_one_page(html):
        print(item)
        save_to_mongo(item)

if __name__ == '__main__':
    for i in  range(10):
        main(i*10)