# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from twisted.enterprise import adbapi
from .settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME


class TianyanchaSpiderPipeline(object):
    def process_item(self, item, spider):
        return item



# 采用异步的机制写入mysql,进行了简写处理
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        if spider.name == "tianyan_splash":
            query = self.dbpool.runInteraction(self.do_insert, item)
            query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class MysqlPipeline(object):
    # 采用同步的机制写入mysql，进行了简写处理
    def __init__(self):
        self.conn = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME, charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        if spider.name == "tianyan_splash":

            insert_sql = """
                             insert into tp_com_info(company

                              )
                             VALUES (%s)
                             ON DUPLICATE KEY UPDATE
                               company=VALUES(company)

                         """
            try:
                self.cursor.execute(insert_sql, (item["company_name"]))
                print("successful")
                self.conn.commit()
            except Exception as e:
                print(e)
                print("Failed")
                self.conn.rollback()
