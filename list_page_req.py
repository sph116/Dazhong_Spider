import requests
from lxml import etree
import time
import random
import re
from Font_decryption_demo import Font_Decryption
import json
import threading
from ip_pool import Ip_pool, stop_ip_pool, get_ip
from mysql_model import Mysql
from fake_useragent import UserAgent
# ua = UserAgent()


headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    "Cookie": "_lxsdk_cuid=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _lxsdk=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _hc.v=63c163cf-d75d-89b9-0dc1-74a9b2026548.1571362621; ua=sph; ctu=cdff7056daa2405159990763801b14e0b74443eb8302ce0928ea5e3d95696905; s_ViewType=10; aburl=1; _dp.ac.v=da84abba-5c47-4040-ac30-40e09e04162f; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dper=ae518422253841cb8382badd9f84a3d4d1cab3368f96b8b833d0ed54b7ba5ec5e1f19bb70643b83040755a6bae10220d2f115c21ad91fdcb6575b68e18fa5b10f94dd03ce59e7626eda956281deb519384ef81d07a0efea07928db045089bc94; ll=7fd06e815b796be3df069dec7836c3df; uamo=15292060685; cy=1; cye=shanghai; _lxsdk_s=16dfb55a64d-2d3-ea9-574%7C%7C121",
    'Host': 'www.dianping.com',
}


def get_list_page(keywords):
    for place in range(1, 1000):
        i = 1  # 纪录每次翻页页码
        page_nums = 0  # 记录最大页码
        empty_flag = False  # 是否搜索失败
        while 1:
            retry_times = 1  # 重试次数
            while retry_times < 5:  # 最多三次重试
                try:
                    proxy = get_ip()  # 获取ip
                    # headers["User-Agent"] = random.choice(ua)
                    # print(headers["User-Agent"])
                    url = "http://www.dianping.com/search/keyword/{}/10_{}/p{}".format(place, keywords, i)
                    rep = requests.get(url=url, headers=headers, proxies=proxy, timeout=20)    # 每次使用代理请求
                    time.sleep(random.uniform(6, 20))                                          # 每次请求随机休眠时间
                    if rep.status_code == 200:
                        Text = rep.text
                        sel = etree.HTML(Text)

                        if sel.xpath("/html/body/div[2]/div[2]/div[1]/div/div/div[2]/p[1]/text()") == ["建议您："] or "not-found-suggest" in Text or 'not-found-words-highlight' in Text:  # 未搜索到信息 退出
                            empty_flag = True
                            break
                        if i == 1:
                            page_num = sel.xpath('//a[@class="PageLink"]/@data-ga-page')
                            if page_num == []:
                                max_page_num = 1
                            else:
                                max_page_num = max(sel.xpath('//a[@class="PageLink"]/@data-ga-page'))  # 提取最大页码

                        city = sel.xpath('//*[@id="logo-input"]/div[1]/a[2]/span[2]/text()')
                        urls = re.findall('type="text/css" href="(.*?)"', Text)
                        font_css_url = [i for i in urls if "svg" in i][0]  # css地址
                        pf = Font_Decryption(css_url="http:" + font_css_url)         # 存储字体表
                        all_font = pf.get_all_font()  # 取出全部字体表
                        for key in all_font:
                            Text = Text.replace(key.replace("uni", ""), all_font[key])

                        save_data =[]
                        sel = etree.HTML(Text.replace("&#", "").replace(";", ""))
                        for li in sel.xpath('//*[@id="shop-all-list"]/ul/li'):
                            Recommended = ','.join(li.xpath('./div[2]/div[4]/a/text()'))         # 推荐菜
                            shop_name = ''.join(li.xpath('./div[2]/div[1]/a/h4/text()'))             # 店铺名
                            street = ''.join(li.xpath('./div[2]/div[3]/a[2]/span//text()'))          # 商铺所在街区
                            star_level = ''.join(li.xpath('./div[2]/div[2]/span/@title'))            # 星级
                            address = ''.join(li.xpath('.//span[@class="addr"]//text()'))            # 商铺具体地址
                            per_capita = ''.join(li.xpath('./div[2]/div[2]/a[2]/b//text()')).replace('斯', '3')    # 人均消费
                            taste_score = ''.join(li.xpath('./div[2]/span/span[1]/b//text()')).replace('斯', '3')  # 消费分数
                            environmental_score = ''.join(li.xpath('./div[2]/span/span[2]/b//text()')).replace('斯',
                                                                                                                 '3')  # 环境分数
                            service_score = ''.join(li.xpath('./div[2]/span/span[3]/b//text()')).replace('斯',
                                                                                                         '3')          # 服务分数
                            shop_url = ''.join(li.xpath('./div[1]/a/@href'))                                           # 店铺url


                            save_data.append({
                                "city": city,
                                "street": street,
                                "star_level": star_level,
                                "address": address,
                                "per_capita": per_capita,
                                "taste_score": taste_score,
                                "environmental_score": environmental_score,
                                "service_score": service_score,
                                "shop_url": shop_url,
                                'shop_name': shop_name,
                                'Recommended': Recommended,
                                'Comment_number': Comment_number
                            })
                        Mysql.save_url(save_dates=save_data, table="haidilao_data_v2", url=url)   # 存储店铺详情信息
                        break

                    elif rep.status_code == 404:  # 网址错误 退出
                        empty_flag = True
                        break
                except Exception as e:
                    print("{}:失败，原因:{} 重试".format(url, e))
                    if retry_times == 3:
                        time.sleep(150)
                    retry_times += 1
                    continue
            i += 1

            if empty_flag == True:
                print("{} 此类型采集完毕----------".format(url))
                break
            elif i >= int(max_page_num) == True:  # 翻页结束
                print("{} 此类型采集完毕----------".format(url))
                break


if __name__ == "__main__":
    """为ip池构造线程"""
    t = threading.Thread(target=Ip_pool, args=())
    t.start()
    time.sleep(3)

    get_list_page("%E6%B5%B7%E5%BA%95%E6%8D%9E") # 启动列表页采集  搜索海底捞
    stop_ip_pool()   # 采集结束 停止维护ip池



