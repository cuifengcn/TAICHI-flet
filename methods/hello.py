from flask import Flask, request
import traceback
import requests
import re
import os
import json
from lxml import etree
from urllib.parse import unquote

cilimao_site = ''

app = Flask(__name__, static_folder='/')


@app.route("/", methods=['GET','POST'])
def index():
    return app.send_static_file('index.html')

@app.route("/api", methods=['POST'])  # type: ignore
def hello_world():
    data = json.loads(request.get_data())
    try:
        if data.get('action') == 'search':
            return search(data)
        elif data.get('action') == 'detail':
            return detail(data)
        elif data.get('action') == 'next':
            return next(data)
        else:
            return {'success': False, 'err_msg': '不支持的action'}
    except Exception:
        # 把服务器捕获到的异常打印并发送一份给客户端
        print(traceback.format_exc())
        return {'success': False, 'err_msg': traceback.format_exc()}


def search(data):
    kw = data.get('key_word')
    page_count = data.get('page_count')
    engin = data.get('engin')
    if len(kw) == 0:
        print('缺少搜索关键字')
        return {'success': False}
    else:
        kw = data['key_word']
        if engin == 'btsow':
            result = btsow(kw, page_count, fuzzy=data['fuzzy'])
        elif engin == 'sukebei':
            result = sukebei(kw, page_count, fuzzy=data['fuzzy'])
        elif engin == 'thepiratebay':
            result = thepiratebay(kw)
        elif engin == 'torrentkitty':
            result = torrentkitty(kw, page_count)
        elif engin == 'torrentgalaxy':
            result = torrentgalaxy(kw)
        elif engin == '1337x':
            result = _1337x(kw, page_count)
        elif engin == 'cilimao':
            result = cilimao(kw, page_count)
        elif engin == 'nyaa':
            result = nyaa(kw, page_count)
        elif engin == 'iloveyou':
            result = yuhuage(kw, page_count)
        else:
            result = {'success': False, 'err_msg': '未支持的站点'}
        return result


def detail(data):
    engin = data.get('engin')
    link = data.get('link')
    if engin == 'torrentkitty':
        return detail_kitty(link)
    elif engin == '1337x':
        return detail_1377x(link)
    # 雨花阁engin名因为当时用户教程演示,所以继续保留特殊性
    elif engin == 'iloveyou':
        return detail_yuhuage(link)
    else:
        return {'success': False, 'err_msg': '未定义的详情页动作'}


def btsow(kw, page_count, fuzzy=True):
    result_arr = []
    url = f'https://btsow.com/search/{kw}/page/{page_count}'
    page = requests.get(url)
    html = etree.HTML(page.text)  # type: ignore
    # 最后一个按钮当被添加class时,就说明已经是最后一页了
    next_page_ = html.xpath('//ul[@class="pagination pagination-lg"]')
    if next_page_:
        next_page_ = next_page_[0].xpath('./li[last()]/@class')
        if next_page_:
            next_page = False
        else:
            next_page = True
    else:
        next_page = False
    result = html.xpath('/html/body/div[2]/div[4]/div[@class="row"]')
    for x in result:
        title = x.xpath('./a/@title')[0]
        size = x.xpath('./div[1]/text()')[0]
        magnet = x.xpath('./a/@href')[0]
        magnet = 'magnet:?xt=urn:btih:' + re.sub(r'/.*/', '',
                                                 magnet) + '&dn=' + title
        # 是否需要模糊匹配
        if not fuzzy:
            if kw in title:
                result_arr.append({
                    'title': title,
                    'magnet': magnet,
                    'size': size
                })
        else:
            result_arr.append({'title': title, 'magnet': magnet, 'size': size})
    return {'success': True, 'result': result_arr, 'next_page': next_page}


def nyaa_(url, kw, fuzzy=True):
    result_arr = []
    page = requests.get(url)
    with open('1.html', 'w+', encoding='utf-8') as f:
        f.write(page.text)
    html = etree.HTML(page.text)  # type: ignore
    next_page_ = html.xpath('//ul[@class="pagination"]')
    if next_page_:
        next_page_ = next_page_[0].xpath('./li[last()]/@class')[0]
        if next_page_ == 'next disabled':
            next_page = False
        else:
            next_page = True
    else:
        next_page = False
    # result = html.xpath(f'/html/body/div/div[{index}]/table/tbody/tr')
    result = html.xpath('//div[@class="table-responsive"]/table/tbody/tr')
    for x in result:
        title = x.xpath('./td[2]/a[last()]/text()')[0]
        size = x.xpath('./td[4]/text()')[0]
        seeder = x.xpath('./td[6]/text()')[0]
        # 不要直接指定第二个a标签,有些链接没有种子文件
        magnet = x.xpath('./td[3]/a[last()]/@href')[0]
        # magnet = re.sub(r'&tr.*', '', unquote(magnet))
        magnet = unquote(magnet)
        # 是否需要模糊匹配
        if not fuzzy:
            if kw in title:
                result_arr.append({
                    'title': title,
                    'magnet': magnet,
                    'size': size,
                    'seeder': seeder
                })
        else:
            result_arr.append({
                'title': title,
                'magnet': magnet,
                'size': size,
                'seeder': seeder
            })
    return {'success': True, 'result': result_arr, 'next_page': next_page}


def nyaa(kw, page_count):
    url = f'https://nyaa.si/?q={kw}&p={page_count}'
    return nyaa_(url, kw)


def sukebei(kw, page_count, fuzzy=True):
    url = f'https://sukebei.nyaa.si/?q={kw}&p={page_count}'
    return nyaa_(url, kw, fuzzy)


def thepiratebay(kw):
    result_arr = []
    url = f'https://apibay.org/q.php?q={kw}&cat=/'
    page = requests.get(url).json()
    if page[0]['id'] != '0':
        for x in page:
            title = x['name']
            size = f'{round(int(x["size"])/1073741824,1)}GB'
            magnet = f'magnet:?xt=urn:btih:{x["info_hash"]}&dn={title}'
            seeder = x['seeders']
            result_arr.append({
                'title': title,
                'magnet': magnet,
                'size': size,
                'seeder': seeder
            })
    return {'success': True, 'result': result_arr, 'next_page': False}


def torrentkitty(kw, page_count):
    result_arr = []
    # 永久域名(被墙)
    # url = f'https://www.torrentkitty.net/search/{kw}/'
    # 国内可用域名
    url = f'https://www.torrentkitty.red/search/{kw}/{page_count}'
    page = requests.get(url)
    html = etree.HTML(page.text)  # type: ignore
    # 最后一个按钮当被添加class(disabled)时,就说明已经是最后一页了
    next_page_ = html.xpath('//div[@class="pagination"]')
    if next_page_:
        next_page_ = next_page_[0].xpath('./*[last()]/@class')
        if next_page_:
            next_page = False
        else:
            next_page = True
    else:
        next_page = False
    result = html.xpath('//table[@id="archiveResult"]/tr')
    test_result = result[1].xpath('./td[@class="name"]')[0].xpath('string(.)')
    if not ('No result' in test_result):
        result = result[1:]
        for x in result:
            # title = x.xpath('./td[@class="name"]/text()')[0]
            # 直接获取text()的话,部分标题会分段导致获取不完整
            title = x.xpath('./td[@class="name"]')[0].xpath('string(.)')
            magnet = x.xpath('.//a[@rel="magnet"]/@href')[0]
            magnet = unquote(magnet)
            detail = 'https://www.torrentkitty.red/information/' + \
                re.findall(r'\w{40}', magnet)[0]
            result_arr.append({
                'title': title,
                'magnet': magnet,
                'detail': detail
            })
    return {'success': True, 'result': result_arr, 'next_page': next_page}


def torrentgalaxy(kw):
    result_arr = []
    url = f'https://torrentgalaxy.to/torrents.php?search={kw}#results'
    # 银河的下一页有问题,懒得匹配了
    # url = f'https://torrentgalaxy.to/torrents.php?search={kw}&page={page_count}'
    page = requests.get(url)
    html = etree.HTML(page.text)  # type: ignore
    result = html.xpath('//div[@class="tgxtablerow txlight"]')
    for x in result:
        title = x.xpath('./div[4]/div/a/b/text()')[0]
        size = x.xpath('.//td[3]/span/text()')[0]
        seeder = x.xpath('.//td[4]/span/font/b/text()')[0]
        magnet = x.xpath('./div[5]/a[2]/@href')[0]
        magnet = re.sub(r'&tr.*', '', unquote(magnet))
        result_arr.append({
            'title': title,
            'magnet': magnet,
            'size': size,
            'seeder': seeder
        })
    return {'success': True, 'result': result_arr, 'next_page': False}


def _1337x(kw, page_count):
    result_arr = []
    hd = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    url = f'https://1337x.to/search/{kw}/{page_count}/'
    page = requests.get(url, headers=hd)
    page.encoding = "utf-8"
    html = etree.HTML(page.text)  # type: ignore
    # 当前页面按钮的class=active,最后一页为last,当最后一个按钮被添加active时,就说明当前已经是最后一页
    next_page_ = html.xpath(
        '//div[@class="pagination"]/ul/li[last()]/@class')[0]
    if next_page_ == 'active':
        next_page = False
    else:
        next_page = True
    result = html.xpath(
        '/html/body/main/div/div/div/div[2]/div[1]/table/tbody/tr')
    for x in result:
        title = x.xpath('./td[1]/a[2]/text()')[0]
        size = x.xpath('./td[5]/text()')[0]
        seeder = x.xpath('./td[2]/text()')[0]
        detail = x.xpath('./td/a[2]/@href')[0]
        detail = 'https://1337x.to' + detail
        result_arr.append({
            'title': title,
            'size': size,
            'seeder': seeder,
            'detail': detail
        })
    return {'success': True, 'result': result_arr, 'next_page': next_page}


def detail_1377x(url):
    hd = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    file_list = []
    page = requests.get(url, headers=hd)
    html = etree.HTML(page.text)  # type: ignore
    magnet = html.xpath(
        '//div[@class="col-9 page-content"]/div/div[2]/div/ul/li[1]/a/@href'
    )[0]
    magnet = unquote(magnet)
    files = html.xpath('//div[@id="files"]/ul/li')
    if files:
        for file in files:
            file_list.append(file.xpath('string(.)').replace('\n', ''))
        return {'success': True, 'magnet': magnet, 'files': file_list}
    else:
        return {'success': False, 'err_msg': '无法匹配到文件列表'}


def detail_kitty(url):
    file_list = []
    page = requests.get(url)
    html = etree.HTML(page.text)  # type: ignore
    size = html.xpath('//table[@class="detailSummary"]/tr[4]/td/text()')[0]
    files = html.xpath('//table[@id="torrentDetail"]/tr')
    files = files[1:]
    if files:
        for file in files:
            file_list.append(file.xpath('string(.)'))
        return {'success': True, 'size': size, 'files': file_list}
    else:
        return {'success': False, 'err_msg': '无法匹配到文件列表'}


# 从发布页获取磁力猫地址
def get_cilimao_site():
    print('正在初始化磁力猫地址...')
    global cilimao_site
    page = requests.get('https://xn--tfrs17es0d.com/')
    # page.encoding = "utf-8"
    lis = re.findall(r'<a href="(.*)" target="_blank">', page.text)
    for available in lis:
        try:
            if requests.get(available, timeout=10).status_code == 200:
                print(f'{available} 可用')
                cilimao_site = available
                break
            else:
                print(f'{available} 网址无效,重新测试下一个')
        except requests.exceptions.RequestException:
            print(f'{available}网址无效,重新测试下一个')
    return {
        'success': False,
        'err_msg': f'网址失效,已更新为{cilimao_site}, 新地址将在下一次搜索时生效'
    }


def cilimao(kw, page_count):
    # 磁力只有hash
    result_arr = []
    global cilimao_site
    # 不同的备用域名会让结果产生偏差,有点坑
    url = f'{cilimao_site}/search-{kw}-0-0-{page_count}.html'
    try:
        page = requests.get(url)
    except requests.exceptions.RequestException:
        return get_cilimao_site()
    page.encoding = "utf-8"
    if page.status_code == 200:
        if '<title>正在进入</title>' in page.text:
            return get_cilimao_site()
        else:
            html = etree.HTML(page.text)  # type: ignore
            next_page_ = html.xpath('//div[@class="pager"]/a[last()]/@href')[0]
            if next_page_ == '#':
                next_page = False
                # print('已经是最后一页')
            else:
                next_page = True
                # print('还有下一页')
            result = html.xpath('//div[@class="ssbox"]')
            for x in result:
                title = x.xpath('./div[@class="title"]/h3/a')[0].xpath(
                    'string(.)')
                size = x.xpath(
                    './div/span/b[@class="cpill yellow-pill"]/text()')[0]
                seeder = x.xpath(
                    './div[@class="sbar"]/span[last()]/b/text()')[0]
                magnet = x.xpath('./div[@class="sbar"]/span[1]/a/@href')[0]
                files_ = x.xpath('./div[@class="slist"]/ul/li')
                tmp_files = []
                for file in files_:
                    tmp_files.append(file.xpath('string(.)'))
                result_arr.append({
                    'title': title,
                    'size': size,
                    'seeder': seeder,
                    'magnet': magnet,
                    'files': tmp_files
                })
            return {
                'success': True,
                'result': result_arr,
                'next_page': next_page
            }
    else:
        return get_cilimao_site()


def yuhuage(kw, page_count):
    # 地址发布页 https://github.com/yuhuage/dizhi/
    result_arr = []
    url = f'https://www.yuhuabt.com/search/{kw}-{page_count}.html'
    page = requests.get(url)
    html = etree.HTML(page.text)  # type: ignore
    # 当前页面为最后一页时会被添加一个 current,其余标签没有额外的class名
    next_page_ = html.xpath(
        '//div[@class="bottom-pager detail-width"]/*[last()]/@class')
    if next_page_:
        next_page = False
    else:
        next_page = True
    result = html.xpath('//div[@class="search-item detail-width"]')
    for x in result:
        title = x.xpath('./div[1]/h3/a')[0].xpath('string(.)')
        size = x.xpath('./div[3]/span[2]/b/text()')[0]
        seeder = x.xpath('./div[3]/span[4]/b/text()')[0]
        detail = x.xpath('./div[1]/h3/a/@href')[0]
        detail = 'https://www.yuhuabt.com' + detail
        torrent = {
            'title': title,
            'seeder': seeder,
            'size': size,
            'detail': detail
        }
        result_arr.append(torrent)
    return {'success': True, 'result': result_arr, 'next_page': next_page}


def detail_yuhuage(url):
    page = requests.get(url)
    files = re.findall(r'convert\((.*)\);', page.text)[0]
    files = re.findall(r'"(.*?)":', files)
    # 雨花阁磁力只有hash
    magnet = re.findall(r'magnet:\?xt=urn:btih:\w+', page.text)
    return {'success': True, 'magnet': magnet[0], 'files': files}


def set_local_proxy():
    if os.name == 'nt':
        import winreg
        path = 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings'
        try:
            internet = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, path, 0,
                                        winreg.KEY_ALL_ACCESS)
            ProxyEnable = winreg.QueryValueEx(internet, 'ProxyEnable')[0]
            ProxyServer = winreg.QueryValueEx(internet, 'ProxyServer')[0]
            if ProxyEnable == 1:
                print(f'检测到本地代理 {ProxyServer}')
                proxy_ = f'http://{ProxyServer}'
                os.environ["http_proxy"] = proxy_
                os.environ["https_proxy"] = proxy_
        except Exception:
            print('本地代理检测失败,跳过代理配置')


set_local_proxy()
# get_cilimao_site()
"""
指定python版本
pipenv install --python 3.8
pyinstaller hello.py -i ./static/favicon.ico --add-data=static;.
pipenv install flask lxml pyinstaller requests

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)

"""