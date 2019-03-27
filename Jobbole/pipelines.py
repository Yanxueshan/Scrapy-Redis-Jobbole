# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from pymysql.cursors import DictCursor
from twisted.enterprise import adbapi


class JobbolePipeline(object):
    '''
        示例Pipeline
    '''
    def process_item(self, item, spider):
        '''
            示例处理item
        '''
        return item


class MySQLPipeline(object):
    '''
        将获取到的数据保存到数据库Mysql中
    '''
    def __init__(self, connect):
        '''
            Pipeline的构造函数，获取Mysql的连接
        '''
        self.connect = connect
        self.cursor = self.connect.cursor()

    @classmethod
    def from_settings(cls, settings):
        '''
            读取settings配置文件中Mysql相关内容，并建立连接
        '''
        connect = pymysql.connect(host=settings['MYSQL_HOST'],
                                  db=settings['MYSQL_DBNAME'],
                                  user=settings['MYSQL_USER'],
                                  passwd=settings['MYSQL_PASSWORD'],
                                  charset='utf8')

        return cls(connect)

    def process_item(self, item, spider):
        '''
            Mysql插入语句的具体执行逻辑
        '''
        insert_sql = 'insert into article(title, url, url_id, content, support_nums, collection_nums, ' \
                     'comment_nums, publish_date, tags) values(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON ' \
                     'DUPLICATE KEY UPDATE publish_date=VALUES(publish_date)'

        self.cursor.execute(insert_sql, (item['title'], item['url'], item['url_id'], item['content'],
                                         item['support_nums'], item['collection_nums'], item['comment_nums'],
                                         item['publish_date'], item['tags']))
        self.connect.commit()



class MySQLTwistedPipeline(object):
    '''
        使用twisted将mysql插入变成异步执行
    '''
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_settings(cls, settings):
        db_parameters = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True
        )

        db_pool = adbapi.ConnectionPool('pymysql', **db_parameters)
        return cls(db_pool)

    def process_item(self, item, spider):
        '''
            使用twisted将mysql插入变成异步执行
        '''
        query = self.db_pool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        '''
            处理异步插入时产生的异常，failure为异常信息
        '''
        print(failure)

    def do_insert(self, cursor, item):
        '''
            具体的插入逻辑
        '''
        insert_sql = 'insert into article(title, url, url_id, content, support_nums, collection_nums, ' \
                     'comment_nums, publish_date, tags) values(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON ' \
                     'DUPLICATE KEY UPDATE publish_date=VALUES(publish_date)'

        cursor.execute(insert_sql, (item['title'], item['url'], item['url_id'], item['content'],
                                    item['support_nums'], item['collection_nums'], item['comment_nums'],
                                    item['publish_date'], item['tags']))
