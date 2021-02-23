import pymysql


class SQLHepler(object):
    @staticmethod
    # 处理连接功能
    def open(cursor, data_dict):
        # #连接
        # conn = POOL.connection()
        conn = pymysql.connect(
            host=data_dict.get('host'),
            port=data_dict.get('port'),
            user=data_dict.get('user'),
            password=data_dict.get('password'),
            database=data_dict.get('database'),
            charset='utf8')

        cursor = conn.cursor(cursor=cursor)

        return conn, cursor

    @staticmethod
    # 关闭连接
    def close(conn, cursor):
        conn.commit()
        cursor.close()
        conn.close()

    @classmethod
    def fetch_one(cls, sql, args=None, cursor=pymysql.cursors.DictCursor, data_dict=None):
        conn, cursor = cls.open(cursor, data_dict)
        cursor.execute(sql, args)
        obj = cursor.fetchone()
        cls.close(conn, cursor)
        return obj

    @classmethod
    def fetch_all(cls, sql, args=None, cursor=pymysql.cursors.DictCursor, data_dict=None):
        conn, cursor = cls.open(cursor, data_dict)
        cursor.execute(sql, args)
        obj = cursor.fetchall()
        cls.close(conn, cursor)
        return obj
