import pymysql
from DBUtils.PooledDB import PooledDB

class Operation_MySQL():

    def __init__(self):

        self.host = 'localhost'
        self.user = 'root'
        self.password = '123456'
        self.port = 3306
        self.db = 'dazhong_data'
        # self._db = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port, db=self.db)
        # self._db.ping(reconnect=True)
        # self._cur = self._db.cursor()

        self.POOL = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=10,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=1,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            ping=0,
            # ping MySQL服务端，检查是否服务可用。
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.db,
            charset='utf8'
        )

    def save_data(self, save_dates, table, url, thread_num):
        """
        存储详情页url
        :param url_list:
        :param table:
        :return:
        """
        conn = self.POOL.connection()
        cursor = conn.cursor()
        i = 0
        for item in save_dates:


            keys = ', '.join(item.keys())
            values = ', '.join(['%s'] * len(item))
            sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys,
                                                                         values=values)
            try:
                if cursor.execute(sql, tuple(item.values())):
                    conn.commit()
                    i += 1

            except Exception as a:
                print(':插入数据失败, 原因', a)
        conn.close()
        print("{}: {}采集完成 插入数据库条目{}".format(thread_num, url, i))

    def get_url(self):
        """
        提取出所有待采集url
        :return:
        """

        conn = self.POOL.connection()
        cursor = conn.cursor()
        sql = "SELECT shop_url, Comment_number, state, progress FROM `haidilao_data_v2` WHERE (`city` = '成都' OR `city` = '绵阳' OR `city` = '自贡' OR `city` = '攀枝花' OR `city` = '泸州' OR `city` = '德阳' OR `city` = '广元' OR `city` = '遂宁' OR `city` = '内江' OR `city` = '乐山' OR `city` = '资阳' OR `city` = '宜宾' OR `city` = '南充' OR `city` = '达州' OR `city` = '雅安' OR `city` = '广安' OR `city` = '巴中' OR `city` = '眉山' OR `city` = '重庆') AND `state` IS NULL AND `Comment_number` IS NOT NULL"

        try:
            cursor.execute(sql)  # 执行sql语句
            results = cursor.fetchall()  # 获取查询的所有记录
            urls = [(i[0], i[1], i[2], i[3]) for i in results if i[1] != None]
        except Exception as e:
            print('查询失败 原因： ', e)
        conn.close()
        return urls

    def save_comment(self, url, save_data, Thread_name, table='part_comments'):
        """
        存储评论数据
        :param url:
        :param save_data:
        :param Thread_name:
        :param table:
        :return:
        """
        conn = self.POOL.connection()
        cursor = conn.cursor()
        i = 0
        for item in save_data:

            keys = ', '.join(item.keys())
            values = ', '.join(['%s'] * len(item))
            sql = 'INSERT INTO {table}({keys}) VALUES ({values})'.format(table=table, keys=keys,
                                                                         values=values)
            try:
                if cursor.execute(sql, tuple(item.values())):
                    conn.commit()
                    i += 1

            except Exception as a:
                print(':插入数据失败, 原因', a)
        conn.close()
        print("{}: {}采集完成 插入数据库条目{}".format(Thread_name, url, i))

    def modify_statue(self, url, process, statue=''):
        """
        采集完成url 修改状态
        :param url:
        :return:
        """
        conn = self.POOL.connection()
        cursor = conn.cursor()
        if statue == '':
            sql = "update haidilao_data_v2 set progress = '{}' where shop_url = '{}'".format(process, url)
        else:
            sql = "update haidilao_data_v2 set state = {}, progress = '{}' where shop_url = '{}'".format(statue, process, url)
        try:
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print(e)

Mysql = Operation_MySQL()
# Mysql.modify_statue('http://www.dianping.com/shop/102198946', 1, statue=1)
