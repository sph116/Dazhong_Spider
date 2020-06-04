import requests
from lxml import etree
import re
import time
import random
from mysql_model import Mysql

css_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

headers = {
    'Accept': 'application/json, text/javascript',
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    'Connection': 'keep-alive',
    'Host': 'www.dianping.com',
    "Upgrade-Insecu re-Requests": "1",
    "Referer": "http://www.dianping.com/shop/128001304",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    }


def get_node_dict(css_url, cookie):
    """
    获取坐标值 对应 文字 字典
    :param background_image_link:
    :return:
    """
    res = requests.get(css_url, headers=css_headers)
    node_data_ls = re.findall(r'\.([a-zA-Z0-9]{5,6}).*?round:(.*?)px (.*?)px;', res.text)  # 提取节点名与对应坐标
    background_image_link = re.findall("background-image: url\((.*?)\)", res.text)         # 提取 坐标对应数字 css文件地址
    word_coordinate_dict, y_ls = get_word_coordinate_dict(background_image_link)           #
    node_data_dict = {}
    for i in node_data_ls:
        """构造成{节点名: 数字, .........}"""
        x = -int(i[1][:-2]) // 14
        for index in range(len(y_ls)):
            if -int(i[2][:-2]) <= int(y_ls[index]):
                y = y_ls[index]
                break
        try:
            node_data_dict[i[0]] = word_coordinate_dict[(int(x), str(y))]
        except Exception as e:
            pass
    return node_data_dict

def get_word_coordinate_dict(background_image_link):
    """
    获取坐标值 对应 文字 字典
    :param background_image_link:
    :return:
    """
    word_coordinate_dict = {}
    y_ls = []
    for svg_url in background_image_link:
        url = "http:" + svg_url
        res = requests.get(url, headers=css_headers)
        # time.sleep(random.uniform(30, 120))    # 随机休眠
        Text = res.text
        if 'x=' in Text:
            font_list = re.findall(r'<text x="(.*?)" y="(.*?)">(.*?)</text>', Text)     # 提取坐标对应数字
            if len(font_list) < 20:
                continue
            for i in font_list:
                if i[1] not in y_ls:
                    y_ls.append(i[1])
                for j in range(len(i[2])):
                    word_coordinate_dict[(j, i[1])] = i[2][j]

        elif 'textPath' in Text:
            Y_ls = re.findall(r'<path id="(.*?)" d="M0 (.*?) H600"/>', Text)
            if len(Y_ls) < 20:
                continue
            font_list = re.findall(r'<textPath xlink:href="(.*?)" textLength="(.*?)">(.*?)</textPath>', Text)
            font_list = [(i[1], j[1], i[2]) for i, j in zip(font_list, Y_ls)]
            for i in font_list:
                if i[1] not in y_ls:
                    y_ls.append(i[1])
                for j in range(len(i[2])):
                    word_coordinate_dict[(j, i[1])] = i[2][j]

    return word_coordinate_dict, y_ls

def replace_html(html, css_url, cookie):
    """
    提取全部节点，根据节点名 替换数据 返回真实html数据
    :param html:
    :param css_url:
    :param cookie:
    :return:
    """
    node_data_dict = get_node_dict(css_url, cookie)
    node_names = set()
    for i in re.findall('<svgmtsi class="([a-zA-Z0-9]{5,6})"></svgmtsi>', html):  # 提取所有节点名
        node_names.add(i)
    for node_name in node_names:
        try:
            html = re.sub('<svgmtsi class="%s"></svgmtsi>' % node_name, node_data_dict[node_name], html)  # 替换html节点为数字
        except KeyError as e:
            # print(e)
            pass

    return html


def parse_html(html, shop_id):
    """
    解析html 第一次采集 提取好评差评数量
    后续采集 提取口味，环境，服务，食材，星级，评论
    :param html:
    :param i:
    :return:
    """
    sel = etree.HTML(html)
    save_data = []


    for node_num in range(1, 16):
        comment_content_3 = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[3]/text()'.format(node_num))   # 评论数据存在于 两个节点  div3号节点数据
        comment_content_4 = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[4]/text()'.format(node_num))   # div4号节点数据
        if len(''.join(comment_content_3)) > len(''.join(comment_content_4).replace(' ', '').replace(r'\n', '')):
            comment_content = comment_content_3
        else:
            comment_content = comment_content_4
        taste_score = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[1]/text()'.format(node_num))        # 口味评分
        environment_score = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[2]/text()'.format(node_num))  # 环境评分
        service_score = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[3]/text()'.format(node_num))      # 服务评分
        food_score = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[2]/span[4]/text()'.format(node_num))         # 食物评分
        food_score = ''.join(food_score).strip().replace('食材：', '')
        per_capita = ''
        if "人均" in food_score:    #
            per_capita = food_score.replace('人均：', '').replace('元', '')
            food_score = ''
        star_level = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[3]/div[3]/ul/li[{}]/div/div[2]/span[1]/@class'.format(node_num))

        item = {
            'taste_score': ''.join(taste_score).strip().replace('口味：', ''),
            'environment_score': ''.join(environment_score).strip().replace('环境：', ''),
            'service_score': ''.join(service_score).strip().replace('服务：', ''),
            'food_score': food_score,
            'per_capita': per_capita,
            'shop_id': shop_id,
            'star_level': ''.join(star_level).strip().replace('sml-rank-stars sml-str', '').replace(' star', ''),
            'comment_content': ''.join(comment_content).strip(),
        }
        save_data.append(item)
    return save_data



def parse_action(cookie, main_url, proxy, Thread_name, progress):
    """
    详情页采集主函数
    :param cookie:
    :param url:
    :return:
    """
    # cookie = "__mta=51347094.1571707475917.1571707475917.1571707475917.1; _lxsdk_cuid=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _lxsdk=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _hc.v=63c163cf-d75d-89b9-0dc1-74a9b2026548.1571362621; ua=sph; ctu=cdff7056daa2405159990763801b14e0b74443eb8302ce0928ea5e3d95696905; s_ViewType=10; aburl=1; _dp.ac.v=da84abba-5c47-4040-ac30-40e09e04162f; uamo=15292060685; cy=1; cye=shanghai; dper=ae518422253841cb8382badd9f84a3d471e237b43479f8d74f098a5ea02eabda1d22f0912bc506af3ff0f9dfc1cabd260be8824e9a0abeff2b67e50524f5875806e64becebd3923d9b402b395373f85a7f4228bc2e2dfc6533237b19446496e3; ll=7fd06e815b796be3df069dec7836c3df; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_s=16e353fda1a-7ba-0ce-cef%7C%7C124"
    # url = "http://www.dianping.com/shop/128001304/review_all"
    headers["Cookie"] = cookie
    headers['Host'] = 'www.dianping.com'
    # ip_list = requests.get(
    #     url="http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=8c1fe70d7ceb3a4e77284561df11f0d5&orderNo=GL20191111103706QQa4ktHu&count=1&isTxt=1&proxyType=1").text.split("\r\n")
    # ip_pool = [{"http": "http://{}".format(ip)} for ip in ip_list if ip != ""]
    # main_url = "http://www.dianping.com/shop/100034705"
    shop_id = main_url.replace("http://www.dianping.com/shop/", "")   # 提取shop_id

    if progress == None:
        progress = 1

    for page_num in range(int(progress)+1, 1000):
        url = "http://www.dianping.com/shop/{}/review_all/p{}?queryType=isAll&queryVal=true".format(shop_id, page_num)   # 生成url
        time.sleep(random.uniform(85, 120))  # 每次随机休眠50-100秒
        i = 0
        while i < 2:
            try:
                rep = requests.get(url, headers=headers, timeout=25, proxies=proxy)
                break
            except requests.exceptions.ConnectionError as e:
                i += 1
                time.sleep(300)
                print('{}: 请求失败 休眠300秒 url:{}'.format(Thread_name, url))
                continue

        Text = rep.text

        sel = etree.HTML(Text)
        go_on_flag = sel.xpath('//*[@id="review-list"]/div[2]/div[3]/div[2]/div[3]/text()')
        if go_on_flag == ["暂无点评"]:     # 解析出暂无电影 则退出采集
            print("{}: {}店铺 采集完毕".format(Thread_name, shop_id, ))
            Mysql.modify_statue(main_url, page_num, 1)
            break

        css_url = "http:" + re.findall('<link rel="stylesheet" type="text/css" href="(.*?svg.*?)">', Text)[0]   # 提取cssurl地址
        html = replace_html(Text, css_url, cookie)         # 原始html 替换节点后 生成带有原文的pdf
        save_data = parse_html(html, shop_id)              # 解析
        Mysql.save_comment(url, save_data, Thread_name)    # 存储
        Mysql.modify_statue(main_url, page_num)





