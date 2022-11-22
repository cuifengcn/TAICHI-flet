from utils import HTMLSession

IMG_BASE_URL = "https://www.vmgirls.com/page/{}/"


def get_image_urls(base_url):
    session = HTMLSession()
    res = session.get(base_url)
    print(res.text)
    if res.status_code != 200:
        yield False, res.text
    else:
        elems = res.html.xpath('//a[@class="media-content"]')
        for elem in elems:
            s = elem.attrs.get("href")
            if s:
                detail = session.get(s)
                detail_imgs = detail.html.xpath(
                    '//div[@class="nc-light-gallery"]//img[@src]'
                )
                for detail_img in detail_imgs:
                    d = detail_img.attrs.get("src")
                    if d:
                        yield d


"""次元岛
import requests
import re
import parsel
from tqdm import tqdm
#注意headers里面的大小写
n = 0
headers={#不能爬了，就在这里添加cookie
'Referer':'http://ciyuandao.com/photo/list/0-0-1',
'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Mobile Safari/537.36'
}
for i in tqdm(range(37, 247)):
    n = n + 1
    print ("第%s图片开始获取......"% (n)) 
    try:
        url=f'http://ciyuandao.com/photo/list/0-1-{i}'
        response=requests.get(url=url,headers=headers)
        # print(response.text)
        src=re.findall('\s< img src="(.*?)">',response.text)
        selector=parsel.Selector(response.text)
        a=selector.css('p a ::text').getall()
        # print(len(a))
        # author=selector.css('p>a[href*="coser"]::text').getall()
        Title=[]
        for i in range(0,40,2):
            Title.append(a[i]+a[i+1])
            #创建文件夹
        import os
        #os.makedirs('xxx')
         
        for i in range(0,20):
            url1=src[i]
            title=Title[i]
            response_content=requests.get(url=url1,headers=headers).content
            syspath="C:/Users/Administrator/Desktop/xxx/"
            pic_name=(syspath + title + ".png")
            with open( pic_name,mode='wb') as f:
                f.write(response_content)
    except FileNotFoundError as f:
        pass
    except OSError as o:
        pass
    continue   

"""
"""2美女
import os
import re
import time
from urllib import request
from bs4 import BeautifulSoup
 
 
def get_last_page(text):
    return int(re.findall('[^/$]\d*', re.split('/', text)[-1])[0])
 
 
def html_parse(url, headers):
    time.sleep(3)
    resp = request.Request(url=url, headers=headers)
    res = request.urlopen(resp)
    html = res.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    return soup
 
 
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36 Edg/91.0.864.59'
}
 
url = "https://www.2meinv.com/"
for p in range(1, 10 + 1):
    next_url = url + "index-" + str(p) + ".html"
    soup = html_parse(next_url, headers)
    link_node = soup.findAll('div', attrs={"class": "dl-name"})
    for a in link_node:
        path = "G:/spider/image/2meinv/"
        href = a.find('a', attrs={'target': '_blank'}).get('href')
        no = re.findall('[^-$][\d]', href)[1] + re.findall('[^-$][\d]', href)[2]
        first_url = url + "/article-" + no + ".html"
        title = a.find('a', attrs={'target': '_blank'}).text
        path = path + title + "/"
        soup = html_parse(href, headers)
        count = soup.find('div', attrs={'class': 'des'}).find('h1').text
        last_page = get_last_page(count)
        for i in range(1, last_page + 1):
            next_url = url + "/article-" + no + "-" + str(i) + ".html"
            soup = html_parse(next_url, headers)
            image_url = soup.find('img')['src']
            image_name = image_url.split("/")[-1]
            fileName = path + image_name
            if not os.path.exists(path):
                os.makedirs(path)
            if os.path.exists(fileName):
                continue
            request.urlretrieve(image_url, filename=fileName)
            request.urlcleanup()
        print(title, "下载完成了")
"""