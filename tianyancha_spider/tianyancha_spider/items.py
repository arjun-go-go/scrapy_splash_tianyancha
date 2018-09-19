# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TianyanchaSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TianYanItem(scrapy.Item):
    company_name = scrapy.Field()

    def get_insert_sql(self):

        insert_sql = """
               insert into tp_tianyan_info(company
                 ) VALUES (%s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE company=VALUES(company)

           """
        params = (
            self["company"]

        )
        return insert_sql, params
