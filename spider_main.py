import threading
import time
from mysql_model import Mysql
from ip_pool import Ip_pool, get_ip, break_ip_pool
from queue import Queue
from Font_svg import parse_action
from random import shuffle
import random

url_queue = Queue()       # 构造一个不限大小的队列
threads = []              # 构造工作线程池

# cookies = ["__mta=51347094.1571707475917.1571707475917.1571707475917.1; _lxsdk_cuid=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _lxsdk=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _hc.v=63c163cf-d75d-89b9-0dc1-74a9b2026548.1571362621; ctu=cdff7056daa2405159990763801b14e0b74443eb8302ce0928ea5e3d95696905; s_ViewType=10; aburl=1; _dp.ac.v=da84abba-5c47-4040-ac30-40e09e04162f; cy=9; cye=chongqing; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; ll=7fd06e815b796be3df069dec7836c3df; dper=c248c2fc8d9af6503c166c3da06a2f71e1be4a6476faa229b3f992b0fd81ee695c76c7cc983633b86d06d0e136a4d3893efcf665deb744ba7c05980edd01a4dae3bca250e186668c7e1d16a1729ad03964b0cd93fc51c38f2f2b49ae731e5957; ua=sph; uamo=15292060685; _lxsdk_s=16e8c7bb0b3-89a-da2-311%7C%7C219", ]
cookies = [
    "__mta=51347094.1571707475917.1571707475917.1574387915496.2; _lxsdk_cuid=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _lxsdk=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _hc.v=63c163cf-d75d-89b9-0dc1-74a9b2026548.1571362621; ctu=cdff7056daa2405159990763801b14e0b74443eb8302ce0928ea5e3d95696905; s_ViewType=10; aburl=1; _dp.ac.v=da84abba-5c47-4040-ac30-40e09e04162f; cy=9; cye=chongqing; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; dper=c0946d912942f6255a519107ce45d1a6d7928b4d7d1ca98882e1e6180a80ca6d4d781f5078fa9240a45e4cdfb00aaef86edb50b38a3eaa3ca96bef0a18263690902df9826217ef014ce526cc93eba9b34685d08c2ebbdb4f996396981bba1709; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuser_1439442656; uamo=18740110241; _lxsdk_s=16ea0647878-eb2-83d-351%7C%7C672",
    # "__mta=51347094.1571707475917.1571707475917.1574387915496.2; _lxsdk_cuid=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _lxsdk=16ddc82c62cc8-0c2da24cdecceb-7373e61-15f900-16ddc82c62dc8; _hc.v=63c163cf-d75d-89b9-0dc1-74a9b2026548.1571362621; ctu=cdff7056daa2405159990763801b14e0b74443eb8302ce0928ea5e3d95696905; s_ViewType=10; aburl=1; _dp.ac.v=da84abba-5c47-4040-ac30-40e09e04162f; cy=9; cye=chongqing; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; lgtoken=090c8e732-bd19-4a23-b9c7-79544def0687; dper=0904ebab2a24cb665773161810815d378563d2b5d14dd2a71ae474ae09455d43c653745486814c3256a8d6533fef379fb423050a4fec7cf7dc58043bb8a823c77c3ce8343cfb0182c5be04607a497119b69590c12e60497e90987cb3ab6137c7; ll=7fd06e815b796be3df069dec7836c3df; ua=dpuserAt_0548192458; uamo=18740111235; _lxsdk_s=16ea0647878-eb2-83d-351%7C%7C245",

]
# shuffle(cookies)

threadNum = 1    # 线程数量

def Spider_Action():

    class Spider(threading.Thread):
        """多线程类"""
        def __init__(self, Thread_name, func):
            super().__init__()
            self.Thread_name = Thread_name
            self.func = func

        def run(self):
            self.func(self.Thread_name)


    def worker(Thread_name):

        """
        工作方法
        :param Thread_name:
        :return:
        """
        global url_queue
        global cookies
        print(Thread_name + ':启动')
        cookie = cookies.pop()
        thread_num = int(Thread_name.replace('Thread_', ''))
        while not url_queue.empty():   #队列不为空继续运行
            proxy = get_ip(thread_num)
            # print('{}:本次使用ip为 {}'.format(thread_num, proxy))
            url_data = url_queue.get()
            url = url_data[0]
            process = url_data[3]
            parse_action(cookie, url, proxy, Thread_name, process)


    def main():
        """
        主线程
        :return:
        """
        global url_queue
        global ip_go_on_flag

        start = time.time()


        """为ip池构造线程"""
        t = threading.Thread(target=Ip_pool, args=())
        t.start()
        time.sleep(3)

        # url_list = Mysql.get_url_list()
        url_list = Mysql.get_url()
        len_urls = len(url_list)
        print("Tread_main:待采集url获取完成，数量{}".format(len_urls))
        for i in range(0, len_urls):
            url_queue.put(url_list[i])


        """构造采集线程"""
        for i in range(1, threadNum+1):
            thread = Spider("Thread_" + str(i), worker)
            thread.start()
            threads.append(thread)

        """阻塞"""
        for thread in threads:
            thread.join()

        end = time.time()
        print("-------------------------------")
        print("下载完成. 用时{}秒".format(end - start))
        break_ip_pool()   # 下载完成 停止ip池



    main()
    print("1111111111111111")

# if __name__ == "__main__":
#     main()
Spider_Action()