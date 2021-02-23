from requests_toolbelt import MultipartEncoder
import requests, string, random
import pymysql
from DBUtils.PooledDB import PooledDB
from .constants import Sidus_Dev_Database, Sidus_Pro_Database


def client_post_mutipart_formdata_requests(request_url, requestdict):
    m = MultipartEncoder(
        fields=requestdict,
        boundary='------' + ''.join(random.sample(string.ascii_letters + string.digits, 32))
    )
    # 发送请求报文到服务端
    r = requests.post(request_url, data=m, headers={'Content-Type': m.content_type})
    # 获取服务端的响应报文数据
    responsedata = r.json()
    # 返回请求响应报文
    return responsedata


dev_pool = PooledDB(pymysql,
                    mincached=1,
                    maxcached=5,
                    host=Sidus_Dev_Database.get('host'),
                    port=Sidus_Dev_Database.get('port'),
                    user=Sidus_Dev_Database.get('user'),
                    passwd=Sidus_Dev_Database.get('password'),
                    db=Sidus_Dev_Database.get('database'),
                    charset='utf8')

pro_pool = PooledDB(pymysql,
                    mincached=1,
                    maxcached=5,
                    host=Sidus_Pro_Database.get('host'),
                    port=Sidus_Pro_Database.get('port'),
                    user=Sidus_Pro_Database.get('user'),
                    passwd=Sidus_Pro_Database.get('password'),
                    db=Sidus_Pro_Database.get('database'),
                    charset='utf8')


class SQLHepler(object):
    @staticmethod
    # 处理连接功能
    def open(cursor, db_dict):
        # POOL=current_app.config['PYMYSQL_POOL']
        #
        # #连接
        # conn = POOL.connection()
        # conn = pymysql.connect(
        #     host=db_dict.get('host'),
        #     port=db_dict.get('port'),
        #     user=db_dict.get('user'),
        #     password=db_dict.get('password'),
        #     database=db_dict.get('database'),
        #     charset='utf8')
        if db_dict.get('tag') == "pro":
            pool = pro_pool
        else:
            pool = dev_pool

        conn = pool.connection()
        cursor = conn.cursor(cursor=cursor)

        return conn, cursor

    @staticmethod
    # 关闭连接
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def fetch_one(cls, sql, args=None, cursor=pymysql.cursors.DictCursor, db_dict=None):
        conn, cursor = cls.open(cursor, db_dict)
        cursor.execute(sql, args)
        obj = cursor.fetchone()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def fetch_all(cls, sql, args=None, cursor=pymysql.cursors.DictCursor, db_dict=None):
        conn, cursor = cls.open(cursor, db_dict)
        cursor.execute(sql, args)
        obj = cursor.fetchall()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def sql_execute(cls, sql, args=None, cursor=pymysql.cursors.DictCursor, db_dict=None):
        conn, cursor = cls.open(cursor, db_dict)
        cursor.execute(sql, args)
        cls.close(conn, cursor)

    @classmethod
    def sql_multi_execute(cls, sql, args=None, cursor=None):
        cursor.execute(sql, args)

    @classmethod
    def sql_multi_fetch_one(cls, sql, args=None, cursor=None):
        cursor.execute(sql, args)
        obj = cursor.fetchone()
        return obj

    @classmethod
    def sql_multi_fetch_all(cls, sql, args=None, cursor=None):
        cursor.execute(sql, args)
        obj = cursor.fetchall()
        return obj

    @classmethod
    def sql_multi_open(cls, db_dict, cursor=pymysql.cursors.DictCursor):
        if db_dict.get('tag') == "pro":
            pool = pro_pool
        else:
            pool = dev_pool

        conn = pool.connection()

        cursor = conn.cursor(cursor=cursor)

        return conn, cursor
