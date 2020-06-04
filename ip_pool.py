import requests
import time

go_on_flag = True   # 继续维护代理池的标志位
ip_num = 1          # 每次通过api获取的ip数量
ip_pool = []        # 定时代理


def Ip_pool():
    """
    代理池
    :return:
    """
    global ip_num
    global go_on_flag
    global ip_pool
    print("IP_thread:启动")
    while 1:
        if go_on_flag == False:
            break
        else:
            ip_list = requests.get(
                url="http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=8c1fe70d7ceb3a4e77284561df11f0d5&orderNo=GL201911081617074x1TEkxm&count={}&isTxt=1&proxyType=1".format(ip_num)).text.split(
                "\r\n")
            ip_pool = [{"https": "https://{}".format(ip)} for ip in ip_list if ip != ""]
            print("{}:ip到时 重新获取ip 当前ip池为{}".format("thread_ip", ip_pool))
            time.sleep(400)


def break_ip_pool():
    """
    停止代理池
    :return:
    """
    global go_on_flag
    go_on_flag = False


def modify_ip_num(num):
    """
    修改每次获取的ip数量
    :param num:
    :return:
    """
    global ip_num
    ip_num = num

def stop_ip_pool():
    """
    停止代理池维护
    :return:
    """
    global go_on_flag
    go_on_flag = True

def get_ip(index=None):
    """
    获取获取临时代理
    :return:
    """
    global ip_pool
    if index == None:
        return ip_pool[0]
    return ip_pool[index-1]
