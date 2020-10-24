import json
import re
import requests
from bs4 import BeautifulSoup

url = 'https://schedule.hololive.tv/simple/hololive'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3622.0 Safari/537.36'
}

cookies = {
    'timezone': 'Asia/Shanghai'  # 设置时区中国上海
}

proxies = {
    'http': 'http://192.168.28.190:6666',
    'https': 'http://192.168.28.190:6666'
}

'''
日文->中文 星期表达 对应字典
'''
weekly_jp_cn = {
    '(月)': '(星期一)',
    '(火)': '(星期二)',
    '(水)': '(星期三)',
    '(木)': '(星期四)',
    '(金)': '(星期五)',
    '(土)': '(星期六)',
    '(日)': '(星期日)'
}

dict = {
    0: 'yesterday',
    1: 'today',
    2: 'tomorrow'
}

cover_image_host = 'https://img.youtube.com/vi/'
cover_image_type = '/mqdefault.jpg'  # 封面图清晰度选择 从小到大依次为mqdefault，hqdefault，sddefault，maxresdefault

r = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
# r=requests.get('http://192.168.28.190:8080/first.html')
# r.encoding='utf-8'
# print(r.text)

soup = BeautifulSoup(r.text, "html.parser")
date_msg = soup.find_all('div', class_='holodule navbar-text')
date_dict = {}
for i in range(len(date_msg)):
    date_data = date_msg[i].text.split()
    date_dict[i] = {'date': date_data[0], 'weekly': weekly_jp_cn[date_data[1]]}
#print(date_dict)

stream_msg = soup.find_all('a', target='_blank',href=re.compile(r'^https://www.youtube.com'))

pattern = re.compile(r'v=(.*?)$')
day_set = 0
time_before = 0
temp_list=[]
for i in stream_msg:
    temp = {}
    link = i['href']
    image = cover_image_host + pattern.search(link).group(1) + cover_image_type
    text = i.text.split()
    time = text[0]
    name = text[1]
    hour = int(time[:2])
    if hour < time_before:
        date_dict[day_set]['list']=temp_list
        day_set += 1
        temp_list=[]
    time_before = hour

    temp['time'] = time
    temp['name'] = name
    temp['cover_image_url'] = image
    temp['video_url'] = link
    temp_list.append(temp)
date_dict[day_set]['list'] = temp_list

for i in range(len(date_dict)):
    date_dict[dict[i]] = date_dict.pop(i)

with open('hololive.json', 'w+') as token_file:
    token_file.write(json.dumps(date_dict,ensure_ascii=False))
